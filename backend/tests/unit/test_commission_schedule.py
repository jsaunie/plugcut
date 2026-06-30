"""Unit tests for the commission schedule domain service."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.domain.billing.entities import (
    MAX_PROOF_BYTES,
    EmptyProof,
    NothingToRemind,
    PaymentProof,
    ProofRequiresPaid,
    ProofTooLarge,
    UnsupportedProofType,
)
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

    def test_mark_reminded_records_the_timestamp(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=1), start_date=date(2026, 1, 1)
        )
        installment = schedule.installments[0]
        moment = datetime(2026, 2, 10, tzinfo=UTC)
        installment.mark_reminded(at=moment)
        assert installment.last_reminded_at == moment

    def test_cannot_remind_a_paid_installment(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=1), start_date=date(2026, 1, 1)
        )
        installment = schedule.installments[0]
        installment.mark_paid()
        with pytest.raises(NothingToRemind):
            installment.mark_reminded(at=datetime(2026, 2, 10, tzinfo=UTC))


def make_proof(**overrides: object) -> PaymentProof:
    defaults: dict[str, object] = {
        "filename": "receipt.pdf",
        "content_type": "application/pdf",
        "size": 1024,
        "storage_key": "deal:1",
        "uploaded_at": datetime(2026, 2, 10, tzinfo=UTC),
    }
    defaults.update(overrides)
    return PaymentProof(**defaults)  # type: ignore[arg-type]


class TestPaymentProof:
    def test_accepts_a_valid_pdf(self) -> None:
        proof = make_proof()
        assert proof.content_type == "application/pdf"
        assert proof.size == 1024

    def test_rejects_an_empty_file(self) -> None:
        with pytest.raises(EmptyProof):
            make_proof(size=0)

    def test_rejects_a_file_over_the_size_cap(self) -> None:
        with pytest.raises(ProofTooLarge):
            make_proof(size=MAX_PROOF_BYTES + 1)

    def test_rejects_an_unsupported_content_type(self) -> None:
        with pytest.raises(UnsupportedProofType):
            make_proof(content_type="application/zip")

    def test_attaches_to_a_paid_installment(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=1), start_date=date(2026, 1, 1)
        )
        installment = schedule.installments[0]
        installment.mark_paid(at=datetime(2026, 2, 10, tzinfo=UTC))
        proof = make_proof()
        installment.attach_proof(proof)
        assert installment.proof is proof

    def test_cannot_attach_to_an_unpaid_installment(self) -> None:
        schedule = CommissionScheduleService().generate(
            make_terms(duration_months=1), start_date=date(2026, 1, 1)
        )
        with pytest.raises(ProofRequiresPaid):
            schedule.installments[0].attach_proof(make_proof())
