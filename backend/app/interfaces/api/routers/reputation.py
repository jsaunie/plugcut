"""Reputation routes: a user's trust standing, earned from sealed deals."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.application.reputation.use_cases import GetReputation
from app.domain.reputation.entities import Reputation
from app.interfaces.api.deps import CurrentUser, get_reputation

router = APIRouter(prefix="/reputation", tags=["reputation"])


class ReputationResponse(BaseModel):
    sealed_deals: int
    completed_deals: int
    disputed_deals: int
    as_referrer: int
    as_placed: int
    trust_score: int
    has_track_record: bool

    @classmethod
    def from_domain(cls, reputation: Reputation) -> ReputationResponse:
        return cls(
            sealed_deals=reputation.sealed_deals,
            completed_deals=reputation.completed_deals,
            disputed_deals=reputation.disputed_deals,
            as_referrer=reputation.as_referrer,
            as_placed=reputation.as_placed,
            trust_score=reputation.trust_score,
            has_track_record=reputation.has_track_record,
        )


@router.get("/me", response_model=ReputationResponse)
async def my_reputation(
    current_user: CurrentUser,
    use_case: Annotated[GetReputation, Depends(get_reputation)],
) -> ReputationResponse:
    reputation = await use_case.execute(current_user.id)
    return ReputationResponse.from_domain(reputation)
