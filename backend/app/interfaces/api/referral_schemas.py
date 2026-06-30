"""Pydantic request/response models for the referrals API."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.billing.entities import CommissionInstallment, CommissionSchedule
from app.domain.referrals.entities import Referral


class ReferralCreateRequest(BaseModel):
    placed_person_email: str
    client_reference: str = Field(min_length=1, max_length=255)
    daily_rate: Decimal = Field(gt=0)
    commission_rate: Decimal = Field(ge=0, le=100)
    duration_months: int = Field(gt=0, le=120)
    days_per_period: int = Field(default=20, ge=1, le=31)
    currency: str = Field(default="EUR", min_length=3, max_length=3)


class ReferralResponse(BaseModel):
    id: UUID
    placed_person_email: str
    client_reference: str
    daily_rate: float
    currency: str
    commission_rate: float
    duration_months: int
    status: str
    attribution_hash: str | None
    created_at: datetime
    monthly_expected: float
    total_expected: float

    @classmethod
    def from_domain(cls, referral: Referral) -> ReferralResponse:
        monthly = referral.terms.expected_amount_per_period
        return cls(
            id=referral.id,
            placed_person_email=referral.placed_person_email,
            client_reference=referral.client_reference,
            daily_rate=float(referral.terms.daily_rate.amount),
            currency=referral.terms.daily_rate.currency,
            commission_rate=float(referral.terms.commission.value),
            duration_months=referral.terms.duration_months,
            status=referral.status.value,
            attribution_hash=referral.attribution_hash,
            created_at=referral.created_at,
            monthly_expected=float(monthly.amount),
            total_expected=float(monthly.amount) * referral.terms.duration_months,
        )


class InstallmentResponse(BaseModel):
    sequence: int
    period_start: date
    period_end: date
    due_date: date
    expected_amount: float
    status: str

    @classmethod
    def from_domain(cls, installment: CommissionInstallment) -> InstallmentResponse:
        return cls(
            sequence=installment.sequence,
            period_start=installment.period_start,
            period_end=installment.period_end,
            due_date=installment.due_date,
            expected_amount=float(installment.expected_amount.amount),
            status=installment.status.value,
        )


class ReferralDetailResponse(ReferralResponse):
    schedule: list[InstallmentResponse]

    @classmethod
    def from_domain_with_schedule(
        cls, referral: Referral, schedule: CommissionSchedule
    ) -> ReferralDetailResponse:
        base = ReferralResponse.from_domain(referral)
        return cls(
            **base.model_dump(),
            schedule=[InstallmentResponse.from_domain(i) for i in schedule.installments],
        )
