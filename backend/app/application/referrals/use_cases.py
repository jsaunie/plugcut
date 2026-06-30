"""Referral use cases: create, read, and drive the deal lifecycle."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.referrals.dtos import CreateReferralCommand
from app.application.referrals.errors import (
    InstallmentNotFound,
    ReferralForbidden,
    ReferralNotFound,
)
from app.application.referrals.ports import InstallmentRepository, ReferralRepository
from app.domain.billing.entities import CommissionInstallment, CommissionSchedule
from app.domain.billing.services import CommissionScheduleService
from app.domain.referrals.entities import Referral
from app.domain.referrals.enums import ReferralStatus
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.value_objects import Money, Percentage


def _utc_now() -> datetime:
    return datetime.now(UTC)


async def _load_owned(
    referrals: ReferralRepository, referral_id: UUID, requester_id: UUID
) -> Referral:
    referral = await referrals.get(referral_id)
    if referral is None:
        raise ReferralNotFound
    if referral.referrer_id != requester_id:
        raise ReferralForbidden
    return referral


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
    """Fetch a referral the caller owns, plus its commission schedule.

    Persisted installments (once the deal is signed) take precedence; otherwise the
    forecast is generated from the terms. Statuses are refreshed against today.
    """

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        *,
        schedule_service: CommissionScheduleService | None = None,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._schedule_service = schedule_service or CommissionScheduleService()
        self._now = now

    async def execute(
        self, referral_id: UUID, *, requester_id: UUID
    ) -> tuple[Referral, CommissionSchedule]:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        persisted = await self._installments.list_for_referral(referral_id)
        if persisted:
            schedule = CommissionSchedule(installments=persisted)
        else:
            start = (referral.activated_at or referral.created_at).date()
            schedule = self._schedule_service.generate(referral.terms, start_date=start)
        today = self._now().date()
        for installment in schedule.installments:
            installment.refresh_status(as_of=today)
        return referral, schedule


class QualifyReferral:
    def __init__(self, referrals: ReferralRepository) -> None:
        self._referrals = referrals

    async def execute(self, referral_id: UUID, *, requester_id: UUID) -> Referral:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        referral.qualify()
        await self._referrals.save(referral)
        return referral


class AcceptReferral:
    """Record one party's acceptance; signs and builds the schedule when both agree."""

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
        schedule_service: CommissionScheduleService | None = None,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._now = now
        self._schedule_service = schedule_service or CommissionScheduleService()

    async def execute(
        self, referral_id: UUID, *, requester_id: UUID, party: str
    ) -> Referral:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        was_signed = referral.status is ReferralStatus.SIGNED
        at = self._now()
        if party == "placed":
            referral.accept_as_placed_person(at=at)
        else:
            referral.accept_as_referrer(at=at)
        await self._referrals.save(referral)
        if referral.status is ReferralStatus.SIGNED and not was_signed:
            schedule = self._schedule_service.generate(
                referral.terms, start_date=referral.created_at.date()
            )
            await self._installments.replace_for_referral(referral.id, schedule.installments)
        return referral


class ActivateReferral:
    def __init__(
        self,
        referrals: ReferralRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._referrals = referrals
        self._now = now

    async def execute(self, referral_id: UUID, *, requester_id: UUID) -> Referral:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        referral.activate(at=self._now())
        await self._referrals.save(referral)
        return referral


class RecordInstallmentPayment:
    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
    ) -> None:
        self._referrals = referrals
        self._installments = installments

    async def execute(
        self, referral_id: UUID, sequence: int, *, requester_id: UUID
    ) -> CommissionInstallment:
        await _load_owned(self._referrals, referral_id, requester_id)
        installment = await self._installments.get(referral_id, sequence)
        if installment is None:
            raise InstallmentNotFound
        installment.mark_paid()
        await self._installments.update(referral_id, installment)
        return installment
