"""Referral use cases: create, read, and drive the deal lifecycle."""

from __future__ import annotations

import secrets
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.application.identity.ports import UserRepository
from app.application.referrals.dtos import (
    CreateReferralCommand,
    ReferralStats,
    TimelineEntry,
)
from app.application.referrals.errors import (
    AgreementNotReady,
    InstallmentNotFound,
    InvitationNotFound,
    ReferralForbidden,
    ReferralNotFound,
)
from app.application.referrals.ports import (
    AgreementRenderer,
    InstallmentRepository,
    InvoiceRenderer,
    ReferralRepository,
)
from app.domain.billing.entities import CommissionInstallment, CommissionSchedule
from app.domain.billing.services import CommissionScheduleService
from app.domain.referrals.entities import Referral
from app.domain.referrals.enums import InstallmentStatus, ReferralStatus
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.value_objects import Money, Percentage


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _make_invitation_token() -> str:
    return secrets.token_urlsafe(24)


async def _persist_schedule_on_signing(
    referral: Referral,
    was_signed: bool,
    installments: InstallmentRepository,
    schedule_service: CommissionScheduleService,
) -> None:
    """When a deal becomes signed, generate and persist its commission schedule."""
    if referral.status is ReferralStatus.SIGNED and not was_signed:
        schedule = schedule_service.generate(
            referral.terms, start_date=referral.created_at.date()
        )
        await installments.replace_for_referral(referral.id, schedule.installments)


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
        token_factory: Callable[[], str] = _make_invitation_token,
    ) -> None:
        self._referrals = referrals
        self._now = now
        self._id_factory = id_factory
        self._token_factory = token_factory

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
            invitation_token=self._token_factory(),
        )
        await self._referrals.add(referral)
        return referral


class ListReferrals:
    def __init__(self, referrals: ReferralRepository) -> None:
        self._referrals = referrals

    async def execute(self, referrer_id: UUID) -> list[Referral]:
        return await self._referrals.list_for_referrer(referrer_id)


_COMMITTED = {ReferralStatus.SIGNED, ReferralStatus.ACTIVE, ReferralStatus.COMPLETED}


class GetReferralStats:
    """Aggregate KPIs across one referrer's deals: pipeline, run-rate, money flow."""

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._now = now

    async def execute(self, referrer_id: UUID) -> ReferralStats:
        deals = await self._referrals.list_for_referrer(referrer_id)
        today = self._now().date()

        active = 0
        currency = "EUR"
        pipeline = monthly = collected = outstanding = overdue = Decimal("0")

        for deal in deals:
            currency = deal.terms.daily_rate.currency
            monthly_amount = deal.terms.expected_amount_per_period.amount
            if deal.status is ReferralStatus.ACTIVE:
                active += 1
                monthly += monthly_amount
            if deal.status not in _COMMITTED:
                continue
            pipeline += monthly_amount * deal.terms.duration_months
            for installment in await self._installments.list_for_referral(deal.id):
                installment.refresh_status(as_of=today)
                amount = installment.amount_due.amount
                if installment.status is InstallmentStatus.PAID:
                    collected += amount
                else:
                    outstanding += amount
                    if installment.status is InstallmentStatus.OVERDUE:
                        overdue += amount

        return ReferralStats(
            total_deals=len(deals),
            active_deals=active,
            pipeline_expected=float(pipeline),
            monthly_run_rate=float(monthly),
            collected=float(collected),
            outstanding=float(outstanding),
            overdue=float(overdue),
            currency=currency,
        )


class GetDealTimeline:
    """Synthesize the deal's audit trail from its stored timestamps (no event table)."""

    def __init__(
        self, referrals: ReferralRepository, installments: InstallmentRepository
    ) -> None:
        self._referrals = referrals
        self._installments = installments

    async def execute(self, referral_id: UUID, *, requester_id: UUID) -> list[TimelineEntry]:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        entries: list[TimelineEntry] = [TimelineEntry("created", referral.created_at)]

        if referral.accepted_by_referrer_at is not None:
            entries.append(
                TimelineEntry(
                    "accepted_referrer",
                    referral.accepted_by_referrer_at,
                    referral.referrer_signature or "",
                )
            )
        if referral.accepted_by_placed_at is not None:
            entries.append(
                TimelineEntry(
                    "accepted_placed",
                    referral.accepted_by_placed_at,
                    referral.placed_signature or "",
                )
            )
        if (
            referral.attribution_hash is not None
            and referral.accepted_by_referrer_at is not None
            and referral.accepted_by_placed_at is not None
        ):
            signed_at = max(referral.accepted_by_referrer_at, referral.accepted_by_placed_at)
            entries.append(TimelineEntry("signed", signed_at))
        if referral.activated_at is not None:
            entries.append(TimelineEntry("activated", referral.activated_at))

        for installment in await self._installments.list_for_referral(referral_id):
            if installment.status is InstallmentStatus.PAID and installment.paid_at is not None:
                entries.append(
                    TimelineEntry(
                        "payment_recorded", installment.paid_at, str(installment.sequence)
                    )
                )

        entries.sort(key=lambda entry: entry.at)
        return entries


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
        self, referral_id: UUID, *, requester_id: UUID, party: str, signature: str
    ) -> Referral:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        was_signed = referral.status is ReferralStatus.SIGNED
        at = self._now()
        if party == "placed":
            referral.accept_as_placed_person(at=at, signature=signature)
        else:
            referral.accept_as_referrer(at=at, signature=signature)
        await self._referrals.save(referral)
        await _persist_schedule_on_signing(
            referral, was_signed, self._installments, self._schedule_service
        )
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


_AGREEMENT_READY = {
    ReferralStatus.SIGNED,
    ReferralStatus.ACTIVE,
    ReferralStatus.COMPLETED,
}


class GetAgreement:
    """Render the referral contract once the deal is signed."""

    def __init__(
        self,
        referrals: ReferralRepository,
        users: UserRepository,
        renderer: AgreementRenderer,
    ) -> None:
        self._referrals = referrals
        self._users = users
        self._renderer = renderer

    async def execute(self, referral_id: UUID, *, requester_id: UUID, locale: str) -> str:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        if referral.status not in _AGREEMENT_READY:
            raise AgreementNotReady
        referrer = await self._users.get_by_id(referral.referrer_id)
        referrer_email = referrer.email.value if referrer is not None else ""
        return self._renderer.render(referral, referrer_email=referrer_email, locale=locale)


class GetInstallmentInvoice:
    """Render the monthly commission invoice for one installment of a signed deal."""

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        users: UserRepository,
        renderer: InvoiceRenderer,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._users = users
        self._renderer = renderer

    async def execute(
        self, referral_id: UUID, sequence: int, *, requester_id: UUID, locale: str
    ) -> str:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        if referral.status not in _AGREEMENT_READY:
            raise AgreementNotReady
        installment = await self._installments.get(referral_id, sequence)
        if installment is None:
            raise InstallmentNotFound
        referrer = await self._users.get_by_id(referral.referrer_id)
        referrer_email = referrer.email.value if referrer is not None else ""
        return self._renderer.render(
            referral, installment, referrer_email=referrer_email, locale=locale
        )


class RecordInstallmentPayment:
    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._now = now

    async def execute(
        self, referral_id: UUID, sequence: int, *, requester_id: UUID
    ) -> CommissionInstallment:
        await _load_owned(self._referrals, referral_id, requester_id)
        installment = await self._installments.get(referral_id, sequence)
        if installment is None:
            raise InstallmentNotFound
        installment.mark_paid(at=self._now())
        await self._installments.update(referral_id, installment)
        return installment


class GetReferralByInvitation:
    """Public read of a referral by its invitation token (for the placed person)."""

    def __init__(self, referrals: ReferralRepository, users: UserRepository) -> None:
        self._referrals = referrals
        self._users = users

    async def execute(self, token: str) -> tuple[Referral, str]:
        referral = await self._referrals.get_by_invitation_token(token)
        if referral is None:
            raise InvitationNotFound
        referrer = await self._users.get_by_id(referral.referrer_id)
        return referral, (referrer.email.value if referrer is not None else "")


class SignByInvitation:
    """The placed person signs their side of the deal via the invitation token."""

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        users: UserRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
        schedule_service: CommissionScheduleService | None = None,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._users = users
        self._now = now
        self._schedule_service = schedule_service or CommissionScheduleService()

    async def execute(self, token: str, *, signature: str) -> tuple[Referral, str]:
        referral = await self._referrals.get_by_invitation_token(token)
        if referral is None:
            raise InvitationNotFound
        was_signed = referral.status is ReferralStatus.SIGNED
        referral.accept_as_placed_person(at=self._now(), signature=signature)
        await self._referrals.save(referral)
        await _persist_schedule_on_signing(
            referral, was_signed, self._installments, self._schedule_service
        )
        referrer = await self._users.get_by_id(referral.referrer_id)
        return referral, (referrer.email.value if referrer is not None else "")
