"""Domain service that forecasts a commission schedule from negotiated terms.

This is pure, deterministic business logic with no I/O — the heart of the product and
the most heavily unit-tested piece.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.domain.billing.entities import CommissionInstallment, CommissionSchedule
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.calendar import add_months

# Days after a period ends before its commission is considered due.
DEFAULT_PAYMENT_GRACE_DAYS = 15


class CommissionScheduleService:
    """Generates the recurring installments implied by a set of commission terms."""

    def __init__(self, grace_days: int = DEFAULT_PAYMENT_GRACE_DAYS) -> None:
        self._grace_days = grace_days

    def generate(self, terms: CommissionTerms, *, start_date: date) -> CommissionSchedule:
        installments: list[CommissionInstallment] = []
        for index in range(terms.duration_months):
            period_start = add_months(start_date, index)
            period_end = add_months(start_date, index + 1) - timedelta(days=1)
            due_date = period_end + timedelta(days=self._grace_days)
            installments.append(
                CommissionInstallment(
                    sequence=index + 1,
                    period_start=period_start,
                    period_end=period_end,
                    due_date=due_date,
                    expected_days=terms.expected_days_per_period,
                    expected_amount=terms.expected_amount_per_period,
                )
            )
        return CommissionSchedule(installments=installments)
