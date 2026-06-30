"""DTOs for the referrals use cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class TimelineEntry:
    type: str
    at: datetime
    detail: str = ""


@dataclass(frozen=True, slots=True)
class ReferralStats:
    total_deals: int
    active_deals: int
    pipeline_expected: float
    monthly_run_rate: float
    collected: float
    outstanding: float
    overdue: float
    currency: str = "EUR"


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
