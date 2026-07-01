"""Ports for the intro use cases."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.intros.entities import IntroRequest


class IntroRepository(Protocol):
    async def add(self, intro: IntroRequest) -> None: ...

    async def save(self, intro: IntroRequest) -> None: ...

    async def get(self, intro_id: UUID) -> IntroRequest | None: ...

    async def list_inbound(self, to_user_id: UUID) -> list[IntroRequest]: ...

    async def list_outbound(self, from_user_id: UUID) -> list[IntroRequest]: ...

    async def pending_between(
        self, from_user_id: UUID, to_user_id: UUID
    ) -> IntroRequest | None: ...
