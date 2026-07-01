"""Ports for the profile use cases."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.profiles.entities import Profile


class ProfileRepository(Protocol):
    async def add(self, profile: Profile) -> None: ...

    async def save(self, profile: Profile) -> None: ...

    async def get_by_owner(self, owner_id: UUID) -> Profile | None: ...

    async def get_by_handle(self, handle: str) -> Profile | None: ...

    async def list_all(self, *, available_only: bool = False) -> list[Profile]: ...
