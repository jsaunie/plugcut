"""Tests for the concrete security adapters: bcrypt hashing and JWT signing."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.application.identity.errors import InvalidToken
from app.infrastructure.config import Settings
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.infrastructure.security.password_hasher import BcryptPasswordHasher

_TEST_SECRET = "x" * 48  # >= 32 bytes, satisfies pyjwt's HMAC key-length check


def _settings() -> Settings:
    return Settings(jwt_secret=_TEST_SECRET, access_token_ttl_minutes=15)


class TestBcryptPasswordHasher:
    def test_hash_is_not_reversible_and_salted(self) -> None:
        hasher = BcryptPasswordHasher(rounds=4)  # low cost for test speed
        h1 = hasher.hash("supersecret")
        h2 = hasher.hash("supersecret")
        assert h1 != "supersecret"
        assert h1 != h2  # unique salt per hash

    def test_verify_roundtrip(self) -> None:
        hasher = BcryptPasswordHasher(rounds=4)
        hashed = hasher.hash("supersecret")
        assert hasher.verify("supersecret", hashed) is True
        assert hasher.verify("wrong", hashed) is False

    def test_malformed_hash_fails_closed(self) -> None:
        assert BcryptPasswordHasher().verify("x", "not-a-bcrypt-hash") is False


class TestJwtTokenService:
    def test_access_token_roundtrip(self) -> None:
        service = JwtTokenService(_settings())
        token = service.create_access_token("user-123")
        claims = service.decode(token)
        assert claims.subject == "user-123"
        assert claims.token_type == "access"

    def test_refresh_token_carries_type(self) -> None:
        service = JwtTokenService(_settings())
        claims = service.decode(service.create_refresh_token("user-123"))
        assert claims.token_type == "refresh"

    def test_expired_token_is_rejected(self) -> None:
        # Mint a token whose clock is 1h in the past so it is already expired now.
        past = datetime.now(UTC) - timedelta(hours=1)
        minted_in_past = JwtTokenService(_settings(), now=lambda: past)
        token = minted_in_past.create_access_token("user-123")
        with pytest.raises(InvalidToken):
            JwtTokenService(_settings()).decode(token)

    def test_tampered_signature_is_rejected(self) -> None:
        token = JwtTokenService(_settings()).create_access_token("user-123")
        other_secret = JwtTokenService(Settings(jwt_secret="y" * 48))
        with pytest.raises(InvalidToken):
            other_secret.decode(token)
