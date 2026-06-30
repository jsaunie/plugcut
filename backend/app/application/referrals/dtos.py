"""DTOs for the referrals use cases."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateReferralCommand:
    referrer_id: UUID
    placed_person_email: str
    client_reference: str
    daily_rate: Decimal
    commission_rate: Decimal
    duration_months: int
    days_per_period: int = 20
    currency: str = "EUR"
