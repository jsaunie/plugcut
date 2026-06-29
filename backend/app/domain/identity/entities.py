"""The User aggregate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.identity.errors import WeakPassword
from app.domain.identity.ports import PasswordHasher
from app.domain.identity.value_objects import Email

MIN_PASSWORD_LENGTH = 8


@dataclass(slots=True)
class User:
    """An account holder. Stores only the password *hash*, never the raw password."""

    id: UUID
    email: Email
    password_hash: str
    created_at: datetime
    is_active: bool = True
    email_verified: bool = False

    @classmethod
    def register(
        cls,
        *,
        id: UUID,
        email: Email,
        raw_password: str,
        hasher: PasswordHasher,
        now: datetime,
    ) -> User:
        if len(raw_password) < MIN_PASSWORD_LENGTH:
            raise WeakPassword
        return cls(
            id=id,
            email=email,
            password_hash=hasher.hash(raw_password),
            created_at=now,
        )

    def verify_password(self, raw_password: str, hasher: PasswordHasher) -> bool:
        return hasher.verify(raw_password, self.password_hash)
