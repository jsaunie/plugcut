"""FastAPI dependency wiring: settings, db session, repos, use-cases, current user."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.contacts.ports import ContactImporter, ContactRepository
from app.application.contacts.use_cases import (
    CreateContact,
    DeleteContact,
    GetContact,
    ListContacts,
    UpdateContact,
)
from app.application.identity.errors import InvalidToken
from app.application.identity.ports import TokenService, UserRepository
from app.application.identity.use_cases import (
    AuthenticateUser,
    RefreshAccessToken,
    RegisterUser,
)
from app.application.notifications.ports import EmailSender, ReminderEmailRenderer
from app.application.profiles.ports import ProfileRepository
from app.application.profiles.use_cases import (
    GetMyProfile,
    GetPublicProfile,
    UpsertMyProfile,
)
from app.application.referrals.ports import (
    AgreementRenderer,
    EvidenceRenderer,
    FileStorage,
    InstallmentRepository,
    InvoiceRenderer,
    ReferralRepository,
)
from app.application.referrals.use_cases import (
    AcceptReferral,
    ActivateReferral,
    CreateReferral,
    DisputeReferral,
    GetAgreement,
    GetDealTimeline,
    GetDisputeEvidence,
    GetInstallmentInvoice,
    GetPaymentProof,
    GetReferralByInvitation,
    GetReferralStats,
    GetReferralWithSchedule,
    ListReferrals,
    QualifyReferral,
    RecordInstallmentPayment,
    RecordPaymentProof,
    ResolveDispute,
    SendInstallmentReminder,
    SignByInvitation,
)
from app.application.reputation.use_cases import GetReputation
from app.domain.identity.entities import User
from app.domain.identity.ports import PasswordHasher
from app.infrastructure.agreements.html_renderer import HtmlAgreementRenderer
from app.infrastructure.config import Settings
from app.infrastructure.contacts.pdf_importer import PdfContactImporter
from app.infrastructure.email.logging_sender import LoggingEmailSender
from app.infrastructure.email.reminder_renderer import HtmlReminderEmailRenderer
from app.infrastructure.email.resend_sender import ResendEmailSender
from app.infrastructure.evidence.html_renderer import HtmlEvidenceRenderer
from app.infrastructure.invoices.html_renderer import HtmlInvoiceRenderer
from app.infrastructure.persistence.contact_repository import SqlAlchemyContactRepository
from app.infrastructure.persistence.file_storage import SqlAlchemyFileStorage
from app.infrastructure.persistence.installment_repository import (
    SqlAlchemyInstallmentRepository,
)
from app.infrastructure.persistence.profile_repository import SqlAlchemyProfileRepository
from app.infrastructure.persistence.referral_repository import SqlAlchemyReferralRepository
from app.infrastructure.persistence.repositories import SqlAlchemyUserRepository
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.infrastructure.security.password_hasher import BcryptPasswordHasher
from app.interfaces.api.i18n import resolve_locale

_bearer = HTTPBearer(auto_error=False)


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.database.session_factory() as session:
        yield session


def get_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


def get_token_service(settings: Annotated[Settings, Depends(get_settings)]) -> TokenService:
    return JwtTokenService(settings)


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_register_user(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_hasher)],
) -> RegisterUser:
    return RegisterUser(users, hasher, now=lambda: datetime.now(UTC))


def get_authenticate_user(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    hasher: Annotated[PasswordHasher, Depends(get_hasher)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> AuthenticateUser:
    return AuthenticateUser(users, hasher, tokens)


def get_refresh_access_token(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
) -> RefreshAccessToken:
    return RefreshAccessToken(users, tokens)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    if credentials is None:
        raise InvalidToken
    claims = tokens.decode(credentials.credentials)
    if claims.token_type != "access":
        raise InvalidToken
    user = await users.get_by_id(UUID(claims.subject))
    if user is None or not user.is_active:
        raise InvalidToken
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    tokens: Annotated[TokenService, Depends(get_token_service)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> User | None:
    """Returns the authenticated user if a valid token is present, else None.

    Lets a public endpoint (the invitation signing page) link the deal to the placed
    person's account when they happen to be logged in, without requiring it.
    """
    if credentials is None:
        return None
    try:
        claims = tokens.decode(credentials.credentials)
    except InvalidToken:
        return None
    if claims.token_type != "access":
        return None
    user = await users.get_by_id(UUID(claims.subject))
    return user if user is not None and user.is_active else None


def get_referral_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReferralRepository:
    return SqlAlchemyReferralRepository(session)


def get_create_referral(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
) -> CreateReferral:
    return CreateReferral(referrals, now=lambda: datetime.now(UTC))


def get_list_referrals(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
) -> ListReferrals:
    return ListReferrals(referrals)


def get_installment_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InstallmentRepository:
    return SqlAlchemyInstallmentRepository(session)


def get_referral_stats(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
) -> GetReferralStats:
    return GetReferralStats(referrals, installments)


def get_get_referral(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
) -> GetReferralWithSchedule:
    return GetReferralWithSchedule(referrals, installments)


def get_qualify_referral(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
) -> QualifyReferral:
    return QualifyReferral(referrals)


def get_accept_referral(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
) -> AcceptReferral:
    return AcceptReferral(referrals, installments)


def get_activate_referral(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
) -> ActivateReferral:
    return ActivateReferral(referrals)


def get_record_payment(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
) -> RecordInstallmentPayment:
    return RecordInstallmentPayment(referrals, installments)


def get_file_storage(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FileStorage:
    return SqlAlchemyFileStorage(session)


def get_reputation(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
) -> GetReputation:
    return GetReputation(referrals)


def get_profile_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileRepository:
    return SqlAlchemyProfileRepository(session)


def get_upsert_profile(
    profiles: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> UpsertMyProfile:
    return UpsertMyProfile(profiles)


def get_my_profile(
    profiles: Annotated[ProfileRepository, Depends(get_profile_repository)],
) -> GetMyProfile:
    return GetMyProfile(profiles)


def get_public_profile(
    profiles: Annotated[ProfileRepository, Depends(get_profile_repository)],
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
) -> GetPublicProfile:
    return GetPublicProfile(profiles, referrals)


def get_record_proof(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
    storage: Annotated[FileStorage, Depends(get_file_storage)],
) -> RecordPaymentProof:
    return RecordPaymentProof(referrals, installments, storage)


def get_get_proof(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
    storage: Annotated[FileStorage, Depends(get_file_storage)],
) -> GetPaymentProof:
    return GetPaymentProof(referrals, installments, storage)


def get_email_sender(
    settings: Annotated[Settings, Depends(get_settings)],
) -> EmailSender:
    """Resend when an API key is set, otherwise a logging fallback (no real mail)."""
    if settings.email_enabled:
        return ResendEmailSender(settings.resend_api_key, settings.email_from)
    return LoggingEmailSender()


def get_reminder_renderer() -> ReminderEmailRenderer:
    return HtmlReminderEmailRenderer()


def get_send_reminder(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    renderer: Annotated[ReminderEmailRenderer, Depends(get_reminder_renderer)],
    sender: Annotated[EmailSender, Depends(get_email_sender)],
) -> SendInstallmentReminder:
    return SendInstallmentReminder(referrals, installments, users, renderer, sender)


def get_agreement_renderer() -> AgreementRenderer:
    return HtmlAgreementRenderer()


def get_get_agreement(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    renderer: Annotated[AgreementRenderer, Depends(get_agreement_renderer)],
) -> GetAgreement:
    return GetAgreement(referrals, users, renderer)


def get_evidence_renderer() -> EvidenceRenderer:
    return HtmlEvidenceRenderer()


def get_dispute_referral(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
) -> DisputeReferral:
    return DisputeReferral(referrals)


def get_resolve_dispute(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
) -> ResolveDispute:
    return ResolveDispute(referrals)


def get_dispute_evidence(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    renderer: Annotated[EvidenceRenderer, Depends(get_evidence_renderer)],
) -> GetDisputeEvidence:
    return GetDisputeEvidence(referrals, installments, users, renderer)


def get_invitation_view(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetReferralByInvitation:
    return GetReferralByInvitation(referrals, users)


def get_sign_invitation(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> SignByInvitation:
    return SignByInvitation(referrals, installments, users)


def get_deal_timeline(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
) -> GetDealTimeline:
    return GetDealTimeline(referrals, installments)


def get_invoice_renderer() -> InvoiceRenderer:
    return HtmlInvoiceRenderer()


def get_get_invoice(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    installments: Annotated[InstallmentRepository, Depends(get_installment_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    renderer: Annotated[InvoiceRenderer, Depends(get_invoice_renderer)],
) -> GetInstallmentInvoice:
    return GetInstallmentInvoice(referrals, installments, users, renderer)


def get_locale(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    return resolve_locale(request.headers.get("accept-language"), settings.default_locale)


def get_contact_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ContactRepository:
    return SqlAlchemyContactRepository(session)


def get_contact_importer() -> ContactImporter:
    return PdfContactImporter()


def get_create_contact(
    contacts: Annotated[ContactRepository, Depends(get_contact_repository)],
) -> CreateContact:
    return CreateContact(contacts)


def get_list_contacts(
    contacts: Annotated[ContactRepository, Depends(get_contact_repository)],
) -> ListContacts:
    return ListContacts(contacts)


def get_get_contact(
    contacts: Annotated[ContactRepository, Depends(get_contact_repository)],
) -> GetContact:
    return GetContact(contacts)


def get_update_contact(
    contacts: Annotated[ContactRepository, Depends(get_contact_repository)],
) -> UpdateContact:
    return UpdateContact(contacts)


def get_delete_contact(
    contacts: Annotated[ContactRepository, Depends(get_contact_repository)],
) -> DeleteContact:
    return DeleteContact(contacts)
