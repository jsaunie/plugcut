"""Pydantic request/response models for the API edge."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.identity.entities import User


class RegisterRequest(BaseModel):
    # Email shape is enforced by the domain (Email value object) so the rule lives in
    # one place; password length is mirrored here for clear OpenAPI docs + early 422.
    email: str
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    email_verified: bool

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            id=user.id,
            email=user.email.value,
            created_at=user.created_at,
            email_verified=user.email_verified,
        )
