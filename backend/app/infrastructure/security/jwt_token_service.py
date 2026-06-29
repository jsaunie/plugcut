"""JWT token service — signs and verifies our own access/refresh tokens (pyjwt)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import jwt

from app.application.identity.dtos import TokenClaims
from app.application.identity.errors import InvalidToken
from app.infrastructure.config import Settings

ACCESS = "access"
REFRESH = "refresh"


class JwtTokenService:
    def __init__(
        self,
        settings: Settings,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._settings = settings
        self._now = now or (lambda: datetime.now(UTC))

    def create_access_token(self, subject: str) -> str:
        return self._create(
            subject, ACCESS, timedelta(minutes=self._settings.access_token_ttl_minutes)
        )

    def create_refresh_token(self, subject: str) -> str:
        return self._create(
            subject, REFRESH, timedelta(days=self._settings.refresh_token_ttl_days)
        )

    def decode(self, token: str) -> TokenClaims:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            raise InvalidToken from exc
        return TokenClaims(
            subject=str(payload["sub"]),
            token_type=str(payload["type"]),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
        )

    def _create(self, subject: str, token_type: str, ttl: timedelta) -> str:
        issued_at = self._now()
        payload = {
            "sub": subject,
            "type": token_type,
            "iat": int(issued_at.timestamp()),
            "exp": int((issued_at + ttl).timestamp()),
        }
        return jwt.encode(
            payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm
        )
