"""Ports the identity use cases depend on."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.application.identity.dtos import TokenClaims
from app.domain.identity.entities import User
from app.domain.identity.value_objects import Email


class UserRepository(Protocol):
    async def get_by_email(self, email: Email) -> User | None: ...

    async def get_by_id(self, user_id: UUID) -> User | None: ...

    async def add(self, user: User) -> None: ...


class TokenService(Protocol):
    def create_access_token(self, subject: str) -> str: ...

    def create_refresh_token(self, subject: str) -> str: ...

    def decode(self, token: str) -> TokenClaims: ...
