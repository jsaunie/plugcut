"""Data transfer objects for the identity use cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class AuthenticateUserCommand:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True, slots=True)
class TokenClaims:
    subject: str
    token_type: str
    expires_at: datetime
