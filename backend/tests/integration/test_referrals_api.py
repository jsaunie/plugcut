"""Integration tests for the referrals API (auth-protected)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.infrastructure.config import Settings
from app.main import create_app

PAYLOAD = {
    "placed_person_email": "dev@example.com",
    "client_reference": "ACME (discreet)",
    "daily_rate": 500,
    "commission_rate": 10,
    "duration_months": 12,
    "days_per_period": 20,
}


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


async def _auth_headers(client: AsyncClient, email: str = "ref@example.com") -> dict[str, str]:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret"})
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "supersecret"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class TestCreateReferral:
    async def test_requires_auth(self, client: AsyncClient) -> None:
        assert (await client.post("/api/v1/referrals", json=PAYLOAD)).status_code == 401

    async def test_creates_with_computed_amounts(self, client: AsyncClient) -> None:
        headers = await _auth_headers(client)
        response = await client.post("/api/v1/referrals", json=PAYLOAD, headers=headers)
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "sent"
        assert body["monthly_expected"] == 1000.0  # 500 x 20 x 10%
        assert body["total_expected"] == 12000.0
        assert body["attribution_hash"] is None

    async def test_rejects_invalid_terms(self, client: AsyncClient) -> None:
        headers = await _auth_headers(client)
        bad = {**PAYLOAD, "duration_months": 0}
        response = await client.post("/api/v1/referrals", json=bad, headers=headers)
        assert response.status_code == 422


class TestListAndGet:
    async def test_list_returns_own_referrals(self, client: AsyncClient) -> None:
        headers = await _auth_headers(client)
        await client.post("/api/v1/referrals", json=PAYLOAD, headers=headers)
        response = await client.get("/api/v1/referrals", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_get_detail_includes_schedule(self, client: AsyncClient) -> None:
        headers = await _auth_headers(client)
        created = await client.post("/api/v1/referrals", json=PAYLOAD, headers=headers)
        referral_id = created.json()["id"]
        response = await client.get(f"/api/v1/referrals/{referral_id}", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert len(body["schedule"]) == 12
        assert body["schedule"][0]["expected_amount"] == 1000.0

    async def test_cannot_read_another_users_referral(self, client: AsyncClient) -> None:
        owner = await _auth_headers(client, "owner@example.com")
        created = await client.post("/api/v1/referrals", json=PAYLOAD, headers=owner)
        referral_id = created.json()["id"]

        intruder = await _auth_headers(client, "intruder@example.com")
        response = await client.get(f"/api/v1/referrals/{referral_id}", headers=intruder)
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "referral.forbidden"

    async def test_missing_referral_is_404(self, client: AsyncClient) -> None:
        headers = await _auth_headers(client)
        missing = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/referrals/{missing}", headers=headers)
        assert response.status_code == 404
