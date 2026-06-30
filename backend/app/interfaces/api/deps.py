"""FastAPI dependency wiring: settings, db session, repos, use-cases, current user."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.identity.errors import InvalidToken
from app.application.identity.ports import TokenService, UserRepository
from app.application.identity.use_cases import (
    AuthenticateUser,
    RefreshAccessToken,
    RegisterUser,
)
from app.application.referrals.ports import (
    AgreementRenderer,
    InstallmentRepository,
    ReferralRepository,
)
from app.application.referrals.use_cases import (
    AcceptReferral,
    ActivateReferral,
    CreateReferral,
    GetAgreement,
    GetReferralByInvitation,
    GetReferralStats,
    GetReferralWithSchedule,
    ListReferrals,
    QualifyReferral,
    RecordInstallmentPayment,
    SignByInvitation,
)
from app.domain.identity.entities import User
from app.domain.identity.ports import PasswordHasher
from app.infrastructure.agreements.html_renderer import HtmlAgreementRenderer
from app.infrastructure.config import Settings
from app.infrastructure.persistence.installment_repository import (
    SqlAlchemyInstallmentRepository,
)
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


def get_agreement_renderer() -> AgreementRenderer:
    return HtmlAgreementRenderer()


def get_get_agreement(
    referrals: Annotated[ReferralRepository, Depends(get_referral_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    renderer: Annotated[AgreementRenderer, Depends(get_agreement_renderer)],
) -> GetAgreement:
    return GetAgreement(referrals, users, renderer)


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


def get_locale(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    return resolve_locale(request.headers.get("accept-language"), settings.default_locale)
