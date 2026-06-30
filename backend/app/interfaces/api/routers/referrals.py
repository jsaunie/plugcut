"""Referral routes: create a deal, list my deals, read one with its schedule."""

from __future__ import annotations

from dataclasses import asdict
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.referrals.dtos import CreateReferralCommand
from app.application.referrals.use_cases import (
    AcceptReferral,
    ActivateReferral,
    CreateReferral,
    DisputeReferral,
    GetAgreement,
    GetDealTimeline,
    GetDisputeEvidence,
    GetInstallmentInvoice,
    GetReferralStats,
    GetReferralWithSchedule,
    ListReferrals,
    QualifyReferral,
    RecordInstallmentPayment,
    ResolveDispute,
)
from app.interfaces.api.deps import (
    CurrentUser,
    get_accept_referral,
    get_activate_referral,
    get_create_referral,
    get_deal_timeline,
    get_dispute_evidence,
    get_dispute_referral,
    get_get_agreement,
    get_get_invoice,
    get_get_referral,
    get_list_referrals,
    get_locale,
    get_qualify_referral,
    get_record_payment,
    get_referral_stats,
    get_resolve_dispute,
    get_session,
)
from app.interfaces.api.referral_schemas import (
    AcceptReferralRequest,
    AgreementResponse,
    DisputeRequest,
    InstallmentResponse,
    ReferralCreateRequest,
    ReferralDetailResponse,
    ReferralResponse,
    ReferralStatsResponse,
    TimelineEntryResponse,
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
    return ReferralResponse.from_domain(referral, current_user.id)


@router.get("", response_model=list[ReferralResponse])
async def list_referrals(
    current_user: CurrentUser,
    use_case: Annotated[ListReferrals, Depends(get_list_referrals)],
) -> list[ReferralResponse]:
    referrals = await use_case.execute(current_user.id)
    return [ReferralResponse.from_domain(referral, current_user.id) for referral in referrals]


@router.get("/stats", response_model=ReferralStatsResponse)
async def referral_stats(
    current_user: CurrentUser,
    use_case: Annotated[GetReferralStats, Depends(get_referral_stats)],
) -> ReferralStatsResponse:
    stats = await use_case.execute(current_user.id)
    return ReferralStatsResponse(**asdict(stats))


@router.get("/{referral_id}", response_model=ReferralDetailResponse)
async def get_referral(
    referral_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetReferralWithSchedule, Depends(get_get_referral)],
) -> ReferralDetailResponse:
    referral, schedule = await use_case.execute(referral_id, requester_id=current_user.id)
    return ReferralDetailResponse.from_domain_with_schedule(referral, schedule, current_user.id)


@router.post("/{referral_id}/qualify", response_model=ReferralResponse)
async def qualify_referral(
    referral_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[QualifyReferral, Depends(get_qualify_referral)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReferralResponse:
    referral = await use_case.execute(referral_id, requester_id=current_user.id)
    await session.commit()
    return ReferralResponse.from_domain(referral, current_user.id)


@router.post("/{referral_id}/accept", response_model=ReferralResponse)
async def accept_referral(
    referral_id: UUID,
    payload: AcceptReferralRequest,
    current_user: CurrentUser,
    use_case: Annotated[AcceptReferral, Depends(get_accept_referral)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReferralResponse:
    referral = await use_case.execute(
        referral_id,
        requester_id=current_user.id,
        party=payload.party,
        signature=payload.signature,
    )
    await session.commit()
    return ReferralResponse.from_domain(referral, current_user.id)


@router.post("/{referral_id}/activate", response_model=ReferralResponse)
async def activate_referral(
    referral_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[ActivateReferral, Depends(get_activate_referral)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReferralResponse:
    referral = await use_case.execute(referral_id, requester_id=current_user.id)
    await session.commit()
    return ReferralResponse.from_domain(referral, current_user.id)


@router.get("/{referral_id}/timeline", response_model=list[TimelineEntryResponse])
async def deal_timeline(
    referral_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetDealTimeline, Depends(get_deal_timeline)],
) -> list[TimelineEntryResponse]:
    entries = await use_case.execute(referral_id, requester_id=current_user.id)
    return [
        TimelineEntryResponse(type=e.type, at=e.at, detail=e.detail) for e in entries
    ]


@router.post("/{referral_id}/dispute", response_model=ReferralResponse)
async def dispute_referral(
    referral_id: UUID,
    payload: DisputeRequest,
    current_user: CurrentUser,
    use_case: Annotated[DisputeReferral, Depends(get_dispute_referral)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReferralResponse:
    referral = await use_case.execute(
        referral_id, requester_id=current_user.id, reason=payload.reason
    )
    await session.commit()
    return ReferralResponse.from_domain(referral, current_user.id)


@router.post("/{referral_id}/dispute/resolve", response_model=ReferralResponse)
async def resolve_dispute(
    referral_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[ResolveDispute, Depends(get_resolve_dispute)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReferralResponse:
    referral = await use_case.execute(referral_id, requester_id=current_user.id)
    await session.commit()
    return ReferralResponse.from_domain(referral, current_user.id)


@router.get("/{referral_id}/evidence", response_model=AgreementResponse)
async def get_dispute_evidence_pack(
    referral_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetDisputeEvidence, Depends(get_dispute_evidence)],
    locale: Annotated[str, Depends(get_locale)],
) -> AgreementResponse:
    html = await use_case.execute(referral_id, requester_id=current_user.id, locale=locale)
    return AgreementResponse(html=html)


@router.get("/{referral_id}/agreement", response_model=AgreementResponse)
async def get_agreement(
    referral_id: UUID,
    current_user: CurrentUser,
    use_case: Annotated[GetAgreement, Depends(get_get_agreement)],
    locale: Annotated[str, Depends(get_locale)],
) -> AgreementResponse:
    html = await use_case.execute(referral_id, requester_id=current_user.id, locale=locale)
    return AgreementResponse(html=html)


@router.get("/{referral_id}/installments/{sequence}/invoice", response_model=AgreementResponse)
async def get_installment_invoice(
    referral_id: UUID,
    sequence: int,
    current_user: CurrentUser,
    use_case: Annotated[GetInstallmentInvoice, Depends(get_get_invoice)],
    locale: Annotated[str, Depends(get_locale)],
) -> AgreementResponse:
    html = await use_case.execute(
        referral_id, sequence, requester_id=current_user.id, locale=locale
    )
    return AgreementResponse(html=html)


@router.post("/{referral_id}/installments/{sequence}/pay", response_model=InstallmentResponse)
async def pay_installment(
    referral_id: UUID,
    sequence: int,
    current_user: CurrentUser,
    use_case: Annotated[RecordInstallmentPayment, Depends(get_record_payment)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> InstallmentResponse:
    installment = await use_case.execute(referral_id, sequence, requester_id=current_user.id)
    await session.commit()
    return InstallmentResponse.from_domain(installment)
