"""Public invitation routes: the placed person views and signs a deal by token.

These endpoints are intentionally unauthenticated. The invitation token (a 24-byte
url-safe secret) is the credential, so the placed person can sign without an account.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.referrals.use_cases import GetReferralByInvitation, SignByInvitation
from app.domain.identity.entities import User
from app.interfaces.api.deps import (
    get_invitation_view,
    get_optional_current_user,
    get_session,
    get_sign_invitation,
)
from app.interfaces.api.referral_schemas import (
    PublicReferralResponse,
    SignInvitationRequest,
)

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.get("/{token}", response_model=PublicReferralResponse)
async def view_invitation(
    token: str,
    use_case: Annotated[GetReferralByInvitation, Depends(get_invitation_view)],
) -> PublicReferralResponse:
    referral, referrer_email = await use_case.execute(token)
    return PublicReferralResponse.from_domain(referral, referrer_email)


@router.post("/{token}/accept", response_model=PublicReferralResponse)
async def sign_invitation(
    token: str,
    payload: SignInvitationRequest,
    use_case: Annotated[SignByInvitation, Depends(get_sign_invitation)],
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)],
) -> PublicReferralResponse:
    placed_person_id = current_user.id if current_user is not None else None
    referral, referrer_email = await use_case.execute(
        token, signature=payload.signature, placed_person_id=placed_person_id
    )
    await session.commit()
    return PublicReferralResponse.from_domain(referral, referrer_email)
