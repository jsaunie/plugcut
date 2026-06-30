"""SQLAlchemy implementation of the referral repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.referrals.entities import Referral
from app.domain.referrals.enums import BillingFrequency, ReferralStatus
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.value_objects import Money, Percentage
from app.infrastructure.persistence.models import ReferralModel


def _to_domain(model: ReferralModel) -> Referral:
    terms = CommissionTerms(
        daily_rate=Money(model.daily_rate_amount, model.currency),
        commission=Percentage(model.commission_rate),
        duration_months=model.duration_months,
        frequency=BillingFrequency(model.frequency),
        expected_days_per_period=model.expected_days_per_period,
    )
    return Referral(
        id=model.id,
        referrer_id=model.referrer_id,
        placed_person_email=model.placed_person_email,
        client_reference=model.client_reference,
        terms=terms,
        created_at=model.created_at,
        status=ReferralStatus(model.status),
        placed_person_id=model.placed_person_id,
        accepted_by_referrer_at=model.accepted_by_referrer_at,
        accepted_by_placed_at=model.accepted_by_placed_at,
        activated_at=model.activated_at,
        attribution_hash=model.attribution_hash,
        invitation_token=model.invitation_token,
        referrer_signature=model.referrer_signature,
        placed_signature=model.placed_signature,
        disputed_at=model.disputed_at,
        dispute_reason=model.dispute_reason,
        disputed_by=model.disputed_by,
        status_before_dispute=(
            ReferralStatus(model.status_before_dispute)
            if model.status_before_dispute is not None
            else None
        ),
    )


def _apply_to_model(model: ReferralModel, referral: Referral) -> ReferralModel:
    model.id = referral.id
    model.referrer_id = referral.referrer_id
    model.placed_person_id = referral.placed_person_id
    model.placed_person_email = referral.placed_person_email
    model.client_reference = referral.client_reference
    model.daily_rate_amount = referral.terms.daily_rate.amount
    model.currency = referral.terms.daily_rate.currency
    model.commission_rate = referral.terms.commission.value
    model.duration_months = referral.terms.duration_months
    model.frequency = referral.terms.frequency.value
    model.expected_days_per_period = referral.terms.expected_days_per_period
    model.status = referral.status.value
    model.created_at = referral.created_at
    model.accepted_by_referrer_at = referral.accepted_by_referrer_at
    model.accepted_by_placed_at = referral.accepted_by_placed_at
    model.activated_at = referral.activated_at
    model.attribution_hash = referral.attribution_hash
    model.invitation_token = referral.invitation_token
    model.referrer_signature = referral.referrer_signature
    model.placed_signature = referral.placed_signature
    model.disputed_at = referral.disputed_at
    model.dispute_reason = referral.dispute_reason
    model.disputed_by = referral.disputed_by
    model.status_before_dispute = (
        referral.status_before_dispute.value
        if referral.status_before_dispute is not None
        else None
    )
    return model


class SqlAlchemyReferralRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, referral: Referral) -> None:
        self._session.add(_apply_to_model(ReferralModel(), referral))

    async def save(self, referral: Referral) -> None:
        """Upsert by primary key (insert on create, update on lifecycle change)."""
        await self._session.merge(_apply_to_model(ReferralModel(), referral))

    async def get(self, referral_id: UUID) -> Referral | None:
        model = await self._session.get(ReferralModel, referral_id)
        return _to_domain(model) if model is not None else None

    async def get_by_invitation_token(self, token: str) -> Referral | None:
        model = await self._session.scalar(
            select(ReferralModel).where(ReferralModel.invitation_token == token)
        )
        return _to_domain(model) if model is not None else None

    async def list_for_referrer(self, referrer_id: UUID) -> list[Referral]:
        result = await self._session.scalars(
            select(ReferralModel)
            .where(ReferralModel.referrer_id == referrer_id)
            .order_by(ReferralModel.created_at.desc())
        )
        return [_to_domain(model) for model in result.all()]

    async def list_for_user(self, user_id: UUID) -> list[Referral]:
        result = await self._session.scalars(
            select(ReferralModel)
            .where(
                (ReferralModel.referrer_id == user_id)
                | (ReferralModel.placed_person_id == user_id)
            )
            .order_by(ReferralModel.created_at.desc())
        )
        return [_to_domain(model) for model in result.all()]
