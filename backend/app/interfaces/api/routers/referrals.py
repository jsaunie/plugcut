"""Referral routes: create a deal, list my deals, read one with its schedule."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.referrals.dtos import CreateReferralCommand
from app.application.referrals.use_cases import (
    CreateReferral,
    GetReferralWithSchedule,
    ListReferrals,
)
from app.interfaces.api.deps import (
    CurrentUser,
    get_create_referral,
    get_get_referral,
    get_list_referrals,
    get_session,
)
from app.interfaces.api.referral_schemas import (
    ReferralCreateRequest,
    ReferralDetailResponse,
    ReferralResponse,
)

router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.post("", response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
async def create_referral(
    payload: ReferralCreateRequest,
    current_user: CurrentUser,
    use_case: Annotated[CreateReferral, Depends(get_create_referral)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReferralResponse:
    referral = await use_case.execute(
        CreateReferralCommand(
            referrer_id=current_user.id,
            placed_person_email=payload.placed_person_email,
            client_reference=payload.client_reference,
            daily_rate=payload.daily_rate,
            commission_rate=payload.commission_rate,
            duration_months=payload.duration_months,
            days_per_period=payload.days_per_period,
            currency=payload.currency,
        )
    )
    await session.commit()
    return ReferralResponse.from_domain(referral)


@router.get("", response_model=list[ReferralResponse])
async def list_referrals(
    current_user: CurrentUser,
    use_case: Annotated[ListReferrals, Depends(get_list_referrals)],
) -> list[ReferralResponse]:
    referrals = await use_case.execute(current_user.id)
    return [ReferralResponse.from_domain(referral) for referral in referrals]


@router.get("/{referral_id}", response_model=ReferralDetailResponse)
async def get_referral(
    referral_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetReferralWithSchedule, Depends(get_get_referral)],
) -> ReferralDetailResponse:
    referral, schedule = await use_case.execute(referral_id, requester_id=current_user.id)
    return ReferralDetailResponse.from_domain_with_schedule(referral, schedule)
