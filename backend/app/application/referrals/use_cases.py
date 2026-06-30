"""Referral use cases: create, list, and read with the forecast schedule."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from app.application.referrals.dtos import CreateReferralCommand
from app.application.referrals.errors import ReferralForbidden, ReferralNotFound
from app.application.referrals.ports import ReferralRepository
from app.domain.billing.entities import CommissionSchedule
from app.domain.billing.services import CommissionScheduleService
from app.domain.referrals.entities import Referral
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.value_objects import Money, Percentage


class CreateReferral:
    def __init__(
        self,
        referrals: ReferralRepository,
        *,
        now: Callable[[], datetime],
        id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._referrals = referrals
        self._now = now
        self._id_factory = id_factory

    async def execute(self, command: CreateReferralCommand) -> Referral:
        terms = CommissionTerms(
            daily_rate=Money(command.daily_rate, command.currency),
            commission=Percentage(command.commission_rate),
            duration_months=command.duration_months,
            expected_days_per_period=command.days_per_period,
        )
        referral = Referral(
            id=self._id_factory(),
            referrer_id=command.referrer_id,
            placed_person_email=command.placed_person_email,
            client_reference=command.client_reference,
            terms=terms,
            created_at=self._now(),
        )
        await self._referrals.add(referral)
        return referral


class ListReferrals:
    def __init__(self, referrals: ReferralRepository) -> None:
        self._referrals = referrals

    async def execute(self, referrer_id: UUID) -> list[Referral]:
        return await self._referrals.list_for_referrer(referrer_id)


class GetReferralWithSchedule:
    """Fetch a referral the caller owns, plus its forecast commission schedule."""

    def __init__(
        self,
        referrals: ReferralRepository,
        schedule_service: CommissionScheduleService | None = None,
    ) -> None:
        self._referrals = referrals
        self._schedule_service = schedule_service or CommissionScheduleService()

    async def execute(
        self, referral_id: UUID, *, requester_id: UUID
    ) -> tuple[Referral, CommissionSchedule]:
        referral = await self._referrals.get(referral_id)
        if referral is None:
            raise ReferralNotFound
        if referral.referrer_id != requester_id:
            raise ReferralForbidden
        start = (referral.activated_at or referral.created_at).date()
        schedule = self._schedule_service.generate(referral.terms, start_date=start)
        return referral, schedule
