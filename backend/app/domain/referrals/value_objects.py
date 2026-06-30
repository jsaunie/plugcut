"""Value objects for the referrals context."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.referrals.enums import BillingFrequency
from app.domain.shared.errors import InvariantViolation
from app.domain.shared.value_objects import Money, Percentage


class InvalidTerms(InvariantViolation):
    code = "referral.invalid_terms"


class SignatureRequired(InvariantViolation):
    code = "referral.signature_required"


@dataclass(frozen=True, slots=True)
class CommissionTerms:
    """The negotiated commission deal: a cut of the daily rate over a fixed duration.

    ``expected_days_per_period`` is the estimated number of billable days the placed
    person works each period; it drives the *forecast* schedule. Actual amounts are
    reconciled per installment once real worked days are recorded.
    """

    daily_rate: Money
    commission: Percentage
    duration_months: int
    frequency: BillingFrequency = BillingFrequency.MONTHLY
    expected_days_per_period: int = 20

    def __post_init__(self) -> None:
        if self.duration_months <= 0:
            raise InvalidTerms("duration_months must be positive")
        if not (1 <= self.expected_days_per_period <= 31):
            raise InvalidTerms("expected_days_per_period must be between 1 and 31")
        if self.daily_rate.amount <= 0:
            raise InvalidTerms("daily_rate must be positive")

    def commission_for_days(self, days: int) -> Money:
        """Commission owed for ``days`` billed days: TJM x days x rate."""
        if days < 0:
            raise InvalidTerms("days cannot be negative")
        return self.commission.of(self.daily_rate * days)

    @property
    def expected_amount_per_period(self) -> Money:
        return self.commission_for_days(self.expected_days_per_period)
