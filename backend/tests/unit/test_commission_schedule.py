"""Unit tests for the commission schedule domain service."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.domain.billing.services import CommissionScheduleService
from app.domain.referrals.enums import InstallmentStatus
from app.domain.referrals.value_objects import CommissionTerms, InvalidTerms
from app.domain.shared.value_objects import Money, Percentage


def make_terms(**overrides: object) -> CommissionTerms:
    defaults: dict[str, object] = {
        "daily_rate": Money(Decimal("500")),
        "commission": Percentage(Decimal("10")),
        "duration_months": 12,
        "expected_days_per_period": 20,
    }
    defaults.update(overrides)
    return CommissionTerms(**defaults)  # type: ignore[arg-type]


class TestCommissionTerms:
    def test_rejects_non_positive_duration(self) -> None:
        with pytest.raises(InvalidTerms):
            make_terms(duration_months=0)

    def test_commission_for_days(self) -> None:
        # 500 TJM x 20 days x 10% = 1000
        assert make_terms().expected_amount_per_period == Money(Decimal("1000"))


class TestScheduleGeneration:
    def test_one_installment_per_month(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=12), start_date=date(2026, 1, 1)
        )
        assert len(schedule.installments) == 12
        assert [i.sequence for i in schedule.installments] == list(range(1, 13))

    def test_periods_are_contiguous_months(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=3), start_date=date(2026, 1, 1)
        )
        first, second, third = schedule.installments
        assert first.period_start == date(2026, 1, 1)
        assert first.period_end == date(2026, 1, 31)
        assert second.period_start == date(2026, 2, 1)
        assert second.period_end == date(2026, 2, 28)
        assert third.period_start == date(2026, 3, 1)

    def test_total_expected_is_sum(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=12), start_date=date(2026, 1, 1)
        )
        # 1000 / month x 12 = 12000
        assert schedule.total_expected == Money(Decimal("12000"))

    def test_due_date_applies_grace_period(self) -> None:
        schedule = CommissionScheduleService(grace_days=15).generate(
            make_terms(duration_months=1), start_date=date(2026, 1, 1)
        )
        assert schedule.installments[0].due_date == date(2026, 2, 15)


class TestInstallmentLifecycle:
    def test_reconcile_uses_actual_days(self) -> None:
        terms = make_terms()
        schedule = CommissionScheduleService().generate(terms, start_date=date(2026, 1, 1))
        installment = schedule.installments[0]
        installment.reconcile(days=10, terms=terms)
        # 500 x 10 x 10% = 500
        assert installment.amount_due == Money(Decimal("500"))

    def test_status_progression(self) -> None:
        schedule = CommissionScheduleService(grace_days=15).generate(
            make_terms(duration_months=1), start_date=date(2026, 1, 1)
        )
        installment = schedule.installments[0]
        installment.refresh_status(as_of=date(2026, 1, 15))
        assert installment.status is InstallmentStatus.PENDING
        installment.refresh_status(as_of=date(2026, 2, 5))
        assert installment.status is InstallmentStatus.DUE
        installment.refresh_status(as_of=date(2026, 3, 1))
        assert installment.status is InstallmentStatus.OVERDUE

    def test_paid_is_terminal(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=1), start_date=date(2026, 1, 1)
        )
        installment = schedule.installments[0]
        installment.mark_paid()
        installment.refresh_status(as_of=date(2030, 1, 1))
        assert installment.status is InstallmentStatus.PAID

    def test_outstanding_excludes_paid(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=2), start_date=date(2026, 1, 1)
        )
        schedule.installments[0].mark_paid()
        assert schedule.outstanding(as_of=date(2026, 1, 10)) == Money(Decimal("1000"))
