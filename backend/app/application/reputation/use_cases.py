"""Reputation use cases: read a person's trust standing from their deals."""

from __future__ import annotations

from uuid import UUID

from app.application.referrals.ports import ReferralRepository
from app.domain.reputation.entities import Reputation
from app.domain.reputation.service import ReputationService


class GetReputation:
    """Compute a user's reputation from every deal they are a party to."""

    def __init__(
        self,
        referrals: ReferralRepository,
        service: ReputationService | None = None,
    ) -> None:
        self._referrals = referrals
        self._service = service or ReputationService()

    async def execute(self, subject_id: UUID) -> Reputation:
        deals = await self._referrals.list_for_user(subject_id)
        return self._service.compute(deals, subject_id=subject_id)
