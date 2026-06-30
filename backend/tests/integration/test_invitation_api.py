"""Integration tests for the public invitation flow (placed person signs by token)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.infrastructure.config import Settings
from app.main import create_app

PAYLOAD = {
    "placed_person_email": "dev@example.com",
    "client_reference": "ACME",
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


async def _headers(client: AsyncClient, email: str = "ref@example.com") -> dict[str, str]:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret"})
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "supersecret"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def _create_deal(client: AsyncClient, headers: dict[str, str]) -> dict[str, Any]:
    response = await client.post("/api/v1/referrals", json=PAYLOAD, headers=headers)
    return response.json()


class TestInvitationView:
    async def test_create_exposes_token_only_to_referrer(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal = await _create_deal(client, headers)
        assert deal["invitation_token"]

    async def test_view_returns_public_deal(self, client: AsyncClient) -> None:
        headers = await _headers(client, "owner@example.com")
        deal = await _create_deal(client, headers)
        response = await client.get(f"/api/v1/invitations/{deal['invitation_token']}")
        assert response.status_code == 200
        body = response.json()
        assert body["referrer_email"] == "owner@example.com"
        assert body["client_reference"] == "ACME"
        assert body["placed_signed"] is False

    async def test_invalid_token_is_404(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/invitations/does-not-exist")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "invitation.not_found"


class TestSignByInvitation:
    async def _referrer_signs(
        self, client: AsyncClient, headers: dict[str, str], deal_id: str
    ) -> None:
        await client.post(f"/api/v1/referrals/{deal_id}/qualify", headers=headers)
        await client.post(
            f"/api/v1/referrals/{deal_id}/accept",
            json={"party": "referrer", "signature": "Jean Apporteur"},
            headers=headers,
        )

    async def test_placed_signature_seals_attribution(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal = await _create_deal(client, headers)
        await self._referrer_signs(client, headers, deal["id"])

        response = await client.post(
            f"/api/v1/invitations/{deal['invitation_token']}/accept",
            json={"signature": "Dev Placed"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "signed"
        assert body["placed_signed"] is True
        assert body["attribution_hash"] is not None

    async def test_empty_signature_is_422(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal = await _create_deal(client, headers)
        response = await client.post(
            f"/api/v1/invitations/{deal['invitation_token']}/accept",
            json={"signature": ""},
        )
        assert response.status_code == 422
