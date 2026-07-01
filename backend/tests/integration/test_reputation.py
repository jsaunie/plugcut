"""Integration tests for the reputation endpoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.infrastructure.config import Settings
from app.main import create_app


@pytest_asyncio.fixture
async def client(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    settings = Settings(
        jwt_secret="x" * 48,
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}",
        auto_create_schema=True,
    )
    app = create_app(settings)
    await app.state.database.create_all()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await app.state.database.dispose()


async def _headers(client: AsyncClient, email: str = "ref@example.com") -> dict[str, str]:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret"})
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "supersecret"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _create(client: AsyncClient, headers: dict[str, str]) -> str:
    response = await client.post(
        "/api/v1/referrals",
        json={
            "placed_person_email": "dev@example.com",
            "client_reference": "ACME",
            "daily_rate": "500",
            "commission_rate": "10",
            "duration_months": 12,
            "currency": "EUR",
        },
        headers=headers,
    )
    return str(response.json()["id"])


async def _sign(client: AsyncClient, headers: dict[str, str]) -> str:
    deal_id = await _create(client, headers)
    await client.post(f"/api/v1/referrals/{deal_id}/qualify", headers=headers)
    await client.post(
        f"/api/v1/referrals/{deal_id}/accept",
        json={"party": "referrer", "signature": "Jean Apporteur"},
        headers=headers,
    )
    await client.post(
        f"/api/v1/referrals/{deal_id}/accept",
        json={"party": "placed", "signature": "Dev Place"},
        headers=headers,
    )
    return deal_id


class TestReputationEndpoint:
    async def test_new_user_has_empty_reputation(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        response = await client.get("/api/v1/reputation/me", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["sealed_deals"] == 0
        assert body["trust_score"] == 0
        assert body["has_track_record"] is False

    async def test_unsigned_deal_does_not_build_reputation(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        await _create(client, headers)  # created but not signed
        response = await client.get("/api/v1/reputation/me", headers=headers)
        assert response.json()["sealed_deals"] == 0

    async def test_signed_deal_builds_reputation(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        await _sign(client, headers)
        response = await client.get("/api/v1/reputation/me", headers=headers)
        body = response.json()
        assert body["sealed_deals"] == 1
        assert body["as_referrer"] == 1
        assert body["has_track_record"] is True
        assert body["trust_score"] > 0

    async def test_reputation_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/reputation/me")
        assert response.status_code == 401
