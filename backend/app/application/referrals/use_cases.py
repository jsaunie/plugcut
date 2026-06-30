"""Referral use cases: create, read, and drive the deal lifecycle."""

from __future__ import annotations

import secrets
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.application.identity.ports import UserRepository
from app.application.notifications.ports import EmailSender, ReminderEmailRenderer
from app.application.referrals.dtos import (
    CreateReferralCommand,
    ReferralStats,
    TimelineEntry,
)
from app.application.referrals.errors import (
    AgreementNotReady,
    DealFrozen,
    InstallmentNotFound,
    InvitationNotFound,
    ProofNotFound,
    ReferralForbidden,
    ReferralNotFound,
)
from app.application.referrals.ports import (
    AgreementRenderer,
    EvidenceRenderer,
    FileStorage,
    InstallmentRepository,
    InvoiceRenderer,
    ReferralRepository,
)
from app.domain.billing.entities import (
    CommissionInstallment,
    CommissionSchedule,
    NothingToRemind,
    PaymentProof,
)
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
    """For mutations: only the referrer (who owns the deal) may act."""
    referral = await referrals.get(referral_id)
    if referral is None:
        raise ReferralNotFound
    if referral.referrer_id != requester_id:
        raise ReferralForbidden
    return referral


async def _load_visible(
    referrals: ReferralRepository, referral_id: UUID, requester_id: UUID
) -> Referral:
    """For reads: either party (referrer or the placed person) may view the deal."""
    referral = await referrals.get(referral_id)
    if referral is None:
        raise ReferralNotFound
    if requester_id not in (referral.referrer_id, referral.placed_person_id):
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
    """Every deal the user is a party to: those they refer and those they owe."""

    def __init__(self, referrals: ReferralRepository) -> None:
        self._referrals = referrals

    async def execute(self, user_id: UUID) -> list[Referral]:
        return await self._referrals.list_for_user(user_id)


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


def _synthesize_timeline(
    referral: Referral, installments: list[CommissionInstallment]
) -> list[TimelineEntry]:
    """Build the deal's audit trail from its stored timestamps (no event table)."""
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

    for installment in installments:
        if installment.status is InstallmentStatus.PAID and installment.paid_at is not None:
            entries.append(
                TimelineEntry("payment_recorded", installment.paid_at, str(installment.sequence))
            )
        if installment.last_reminded_at is not None:
            entries.append(
                TimelineEntry(
                    "reminder_sent", installment.last_reminded_at, str(installment.sequence)
                )
            )

    if referral.disputed_at is not None:
        entries.append(
            TimelineEntry("disputed", referral.disputed_at, referral.dispute_reason or "")
        )

    entries.sort(key=lambda entry: entry.at)
    return entries


class GetDealTimeline:
    """Synthesize the deal's audit trail from its stored timestamps (no event table)."""

    def __init__(
        self, referrals: ReferralRepository, installments: InstallmentRepository
    ) -> None:
        self._referrals = referrals
        self._installments = installments

    async def execute(self, referral_id: UUID, *, requester_id: UUID) -> list[TimelineEntry]:
        referral = await _load_visible(self._referrals, referral_id, requester_id)
        installments = await self._installments.list_for_referral(referral_id)
        return _synthesize_timeline(referral, installments)


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
        referral = await _load_visible(self._referrals, referral_id, requester_id)
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
        referral = await _load_visible(self._referrals, referral_id, requester_id)
        if referral.status not in _AGREEMENT_READY:
            raise AgreementNotReady
        referrer = await self._users.get_by_id(referral.referrer_id)
        referrer_email = referrer.email.value if referrer is not None else ""
        return self._renderer.render(referral, referrer_email=referrer_email, locale=locale)


class DisputeReferral:
    """Either party flags and freezes a live deal, stating a reason."""

    def __init__(
        self, referrals: ReferralRepository, *, now: Callable[[], datetime] = _utc_now
    ) -> None:
        self._referrals = referrals
        self._now = now

    async def execute(self, referral_id: UUID, *, requester_id: UUID, reason: str) -> Referral:
        referral = await _load_visible(self._referrals, referral_id, requester_id)
        referral.dispute(at=self._now(), reason=reason, by=requester_id)
        await self._referrals.save(referral)
        return referral


class ResolveDispute:
    """Lift a dispute and restore the deal to its prior status. Either party may resolve."""

    def __init__(self, referrals: ReferralRepository) -> None:
        self._referrals = referrals

    async def execute(self, referral_id: UUID, *, requester_id: UUID) -> Referral:
        referral = await _load_visible(self._referrals, referral_id, requester_id)
        referral.resolve_dispute()
        await self._referrals.save(referral)
        return referral


class GetDisputeEvidence:
    """Render the evidence pack: parties, terms, attribution proof, and full timeline."""

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        users: UserRepository,
        renderer: EvidenceRenderer,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._users = users
        self._renderer = renderer

    async def execute(self, referral_id: UUID, *, requester_id: UUID, locale: str) -> str:
        referral = await _load_visible(self._referrals, referral_id, requester_id)
        if referral.attribution_hash is None:
            raise AgreementNotReady
        installments = await self._installments.list_for_referral(referral_id)
        timeline = _synthesize_timeline(referral, installments)
        referrer = await self._users.get_by_id(referral.referrer_id)
        referrer_email = referrer.email.value if referrer is not None else ""
        return self._renderer.render(
            referral, referrer_email=referrer_email, timeline=timeline, locale=locale
        )


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
        referral = await _load_visible(self._referrals, referral_id, requester_id)
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
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        if referral.is_frozen:
            raise DealFrozen
        installment = await self._installments.get(referral_id, sequence)
        if installment is None:
            raise InstallmentNotFound
        installment.mark_paid(at=self._now())
        await self._installments.update(referral_id, installment)
        return installment


class RecordPaymentProof:
    """Attach a receipt or bank record to a paid installment (referrer only).

    The bytes go through the FileStorage port; the installment keeps the metadata.
    The proof value object validates the content type and size on construction, so
    an unsupported or oversized file is rejected before anything is stored.
    """

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        storage: FileStorage,
        *,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._storage = storage
        self._now = now

    async def execute(
        self,
        referral_id: UUID,
        sequence: int,
        *,
        requester_id: UUID,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> CommissionInstallment:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        if referral.is_frozen:
            raise DealFrozen
        installment = await self._installments.get(referral_id, sequence)
        if installment is None:
            raise InstallmentNotFound
        key = f"proof:{referral_id}:{sequence}"
        proof = PaymentProof(
            filename=filename,
            content_type=content_type,
            size=len(data),
            storage_key=key,
            uploaded_at=self._now(),
        )
        installment.attach_proof(proof)
        await self._storage.save(key, data, content_type=content_type)
        await self._installments.update(referral_id, installment)
        return installment


class GetPaymentProof:
    """Return a paid installment's proof (metadata + bytes), visible to either party."""

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        storage: FileStorage,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._storage = storage

    async def execute(
        self, referral_id: UUID, sequence: int, *, requester_id: UUID
    ) -> tuple[PaymentProof, bytes]:
        await _load_visible(self._referrals, referral_id, requester_id)
        installment = await self._installments.get(referral_id, sequence)
        if installment is None or installment.proof is None:
            raise ProofNotFound
        data = await self._storage.load(installment.proof.storage_key)
        if data is None:
            raise ProofNotFound
        return installment.proof, data


class SendInstallmentReminder:
    """Email the placed person a reminder to settle one due or overdue installment.

    Only the referrer (who is owed) can send it, and not while the deal is frozen by a
    dispute. The send is recorded on the installment so the UI and audit trail can show it.
    """

    def __init__(
        self,
        referrals: ReferralRepository,
        installments: InstallmentRepository,
        users: UserRepository,
        renderer: ReminderEmailRenderer,
        sender: EmailSender,
        *,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._referrals = referrals
        self._installments = installments
        self._users = users
        self._renderer = renderer
        self._sender = sender
        self._now = now

    async def execute(
        self, referral_id: UUID, sequence: int, *, requester_id: UUID, locale: str
    ) -> CommissionInstallment:
        referral = await _load_owned(self._referrals, referral_id, requester_id)
        if referral.is_frozen:
            raise DealFrozen
        installment = await self._installments.get(referral_id, sequence)
        if installment is None:
            raise InstallmentNotFound
        now = self._now()
        installment.refresh_status(as_of=now.date())
        if installment.status is InstallmentStatus.PAID:
            raise NothingToRemind
        referrer = await self._users.get_by_id(referral.referrer_id)
        referrer_email = referrer.email.value if referrer is not None else ""
        message = self._renderer.render(
            referral, installment, referrer_email=referrer_email, locale=locale
        )
        await self._sender.send(message)
        installment.mark_reminded(at=now)
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

    async def execute(
        self, token: str, *, signature: str, placed_person_id: UUID | None = None
    ) -> tuple[Referral, str]:
        referral = await self._referrals.get_by_invitation_token(token)
        if referral is None:
            raise InvitationNotFound
        was_signed = referral.status is ReferralStatus.SIGNED
        referral.accept_as_placed_person(
            at=self._now(), signature=signature, placed_person_id=placed_person_id
        )
        await self._referrals.save(referral)
        await _persist_schedule_on_signing(
            referral, was_signed, self._installments, self._schedule_service
        )
        referrer = await self._users.get_by_id(referral.referrer_id)
        return referral, (referrer.email.value if referrer is not None else "")
