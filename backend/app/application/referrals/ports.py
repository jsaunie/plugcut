"""Ports for the referrals use cases."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.referrals.entities import Referral


class ReferralRepository(Protocol):
    async def add(self, referral: Referral) -> None: ...

    async def get(self, referral_id: UUID) -> Referral | None: ...

    async def list_for_referrer(self, referrer_id: UUID) -> list[Referral]: ...
