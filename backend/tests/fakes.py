"""In-memory test doubles for the identity ports."""

from __future__ import annotations

from uuid import UUID

from app.domain.identity.entities import User
from app.domain.identity.value_objects import Email


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._by_email: dict[str, User] = {}

    async def get_by_email(self, email: Email) -> User | None:
        return self._by_email.get(email.value)

    async def get_by_id(self, user_id: UUID) -> User | None:
        return next((u for u in self._by_email.values() if u.id == user_id), None)

    async def add(self, user: User) -> None:
        self._by_email[user.email.value] = user


class FakePasswordHasher:
    """Deterministic, fast hasher for unit tests (NOT for production)."""

    def hash(self, raw: str) -> str:
        return f"hashed::{raw}"

    def verify(self, raw: str, hashed: str) -> bool:
        return hashed == f"hashed::{raw}"
