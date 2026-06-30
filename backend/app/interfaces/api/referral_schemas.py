"""Pydantic request/response models for the referrals API."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.billing.entities import CommissionInstallment, CommissionSchedule
from app.domain.referrals.entities import Referral


class ReferralStatsResponse(BaseModel):
    total_deals: int
    active_deals: int
    pipeline_expected: float
    monthly_run_rate: float
    collected: float
    outstanding: float
    overdue: float
    currency: str


class ReferralCreateRequest(BaseModel):
    placed_person_email: str
    client_reference: str = Field(min_length=1, max_length=255)
    daily_rate: Decimal = Field(gt=0)
    commission_rate: Decimal = Field(ge=0, le=100)
    duration_months: int = Field(gt=0, le=120)
    days_per_period: int = Field(default=20, ge=1, le=31)
    currency: str = Field(default="EUR", min_length=3, max_length=3)


class AcceptReferralRequest(BaseModel):
    party: Literal["referrer", "placed"]
    signature: str = Field(min_length=1, max_length=120)


class SignInvitationRequest(BaseModel):
    signature: str = Field(min_length=1, max_length=120)


class DisputeRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class AgreementResponse(BaseModel):
    html: str


class TimelineEntryResponse(BaseModel):
    type: str
    at: datetime
    detail: str


class ReferralResponse(BaseModel):
    id: UUID
    placed_person_email: str
    client_reference: str
    daily_rate: float
    currency: str
    commission_rate: float
    duration_months: int
    status: str
    role: str
    accepted_by_referrer: bool
    accepted_by_placed: bool
    invitation_token: str | None
    attribution_hash: str | None
    created_at: datetime
    monthly_expected: float
    total_expected: float
    dispute_reason: str | None
    disputed_at: datetime | None

    @classmethod
    def from_domain(cls, referral: Referral, viewer_id: UUID) -> ReferralResponse:
        monthly = referral.terms.expected_amount_per_period
        is_referrer = referral.referrer_id == viewer_id
        return cls(
            id=referral.id,
            placed_person_email=referral.placed_person_email,
            client_reference=referral.client_reference,
            daily_rate=float(referral.terms.daily_rate.amount),
            currency=referral.terms.daily_rate.currency,
            commission_rate=float(referral.terms.commission.value),
            duration_months=referral.terms.duration_months,
            status=referral.status.value,
            role="referrer" if is_referrer else "placed",
            accepted_by_referrer=referral.accepted_by_referrer_at is not None,
            accepted_by_placed=referral.accepted_by_placed_at is not None,
            # The invitation token is the referrer's secret; never expose it to the placed side.
            invitation_token=referral.invitation_token if is_referrer else None,
            attribution_hash=referral.attribution_hash,
            created_at=referral.created_at,
            monthly_expected=float(monthly.amount),
            total_expected=float(monthly.amount) * referral.terms.duration_months,
            dispute_reason=referral.dispute_reason,
            disputed_at=referral.disputed_at,
        )


class PublicReferralResponse(BaseModel):
    """The placed person's view of a deal opened from an invitation link."""

    referrer_email: str
    placed_person_email: str
    client_reference: str
    daily_rate: float
    currency: str
    commission_rate: float
    duration_months: int
    monthly_expected: float
    total_expected: float
    status: str
    referrer_signed: bool
    placed_signed: bool
    attribution_hash: str | None

    @classmethod
    def from_domain(cls, referral: Referral, referrer_email: str) -> PublicReferralResponse:
        monthly = referral.terms.expected_amount_per_period
        return cls(
            referrer_email=referrer_email,
            placed_person_email=referral.placed_person_email,
            client_reference=referral.client_reference,
            daily_rate=float(referral.terms.daily_rate.amount),
            currency=referral.terms.daily_rate.currency,
            commission_rate=float(referral.terms.commission.value),
            duration_months=referral.terms.duration_months,
            monthly_expected=float(monthly.amount),
            total_expected=float(monthly.amount) * referral.terms.duration_months,
            status=referral.status.value,
            referrer_signed=referral.accepted_by_referrer_at is not None,
            placed_signed=referral.accepted_by_placed_at is not None,
            attribution_hash=referral.attribution_hash,
        )


class InstallmentResponse(BaseModel):
    sequence: int
    period_start: date
    period_end: date
    due_date: date
    expected_amount: float
    status: str
    last_reminded_at: datetime | None

    @classmethod
    def from_domain(cls, installment: CommissionInstallment) -> InstallmentResponse:
        return cls(
            sequence=installment.sequence,
            period_start=installment.period_start,
            period_end=installment.period_end,
            due_date=installment.due_date,
            expected_amount=float(installment.expected_amount.amount),
            status=installment.status.value,
            last_reminded_at=installment.last_reminded_at,
        )


class ReferralDetailResponse(ReferralResponse):
    schedule: list[InstallmentResponse]

    @classmethod
    def from_domain_with_schedule(
        cls, referral: Referral, schedule: CommissionSchedule, viewer_id: UUID
    ) -> ReferralDetailResponse:
        base = ReferralResponse.from_domain(referral, viewer_id)
        return cls(
            **base.model_dump(),
            schedule=[InstallmentResponse.from_domain(i) for i in schedule.installments],
        )
