"""Integration tests for the referral deal lifecycle (qualify/accept/activate/pay)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

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


async def _create(client: AsyncClient, headers: dict[str, str]) -> str:
    response = await client.post("/api/v1/referrals", json=PAYLOAD, headers=headers)
    return response.json()["id"]


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


class TestSigningFlow:
    async def test_two_sided_acceptance_signs_and_seals_attribution(
        self, client: AsyncClient
    ) -> None:
        headers = await _headers(client)
        deal_id = await _create(client, headers)

        await client.post(f"/api/v1/referrals/{deal_id}/qualify", headers=headers)

        first = await client.post(
            f"/api/v1/referrals/{deal_id}/accept",
            json={"party": "referrer", "signature": "Jean Apporteur"},
            headers=headers,
        )
        assert first.json()["status"] == "qualified"
        assert first.json()["attribution_hash"] is None

        second = await client.post(
            f"/api/v1/referrals/{deal_id}/accept",
            json={"party": "placed", "signature": "Dev Place"},
            headers=headers,
        )
        body = second.json()
        assert body["status"] == "signed"
        assert body["attribution_hash"] is not None
        assert len(body["attribution_hash"]) == 64

    async def test_schedule_persisted_after_signing(self, client: AsyncClient) -> None:
        headers = await _headers(client)
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
        detail = await client.get(f"/api/v1/referrals/{deal_id}", headers=headers)
        assert len(detail.json()["schedule"]) == 12


class TestActivationAndPayment:
    async def test_activate_then_pay_installment(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign(client, headers)

        activated = await client.post(f"/api/v1/referrals/{deal_id}/activate", headers=headers)
        assert activated.json()["status"] == "active"

        paid = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers
        )
        assert paid.status_code == 200
        assert paid.json()["status"] == "paid"

        detail = await client.get(f"/api/v1/referrals/{deal_id}", headers=headers)
        assert detail.json()["schedule"][0]["status"] == "paid"

    async def test_paying_twice_conflicts(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        await client.post(f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers)
        again = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers
        )
        assert again.status_code == 409
        assert again.json()["error"]["code"] == "installment.already_paid"


class TestGuards:
    async def test_activate_before_signed_is_conflict(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _create(client, headers)
        response = await client.post(f"/api/v1/referrals/{deal_id}/activate", headers=headers)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "domain.illegal_state_transition"

    async def test_cannot_qualify_another_users_deal(self, client: AsyncClient) -> None:
        owner = await _headers(client, "owner@example.com")
        deal_id = await _create(client, owner)
        intruder = await _headers(client, "intruder@example.com")
        response = await client.post(f"/api/v1/referrals/{deal_id}/qualify", headers=intruder)
        assert response.status_code == 403


class TestAgreement:
    async def test_not_ready_before_signed(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _create(client, headers)
        response = await client.get(f"/api/v1/referrals/{deal_id}/agreement", headers=headers)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "agreement.not_ready"

    async def test_agreement_html_after_signing(self, client: AsyncClient) -> None:
        headers = await _headers(client, "owner@example.com")
        deal_id = await _sign(client, headers)
        response = await client.get(
            f"/api/v1/referrals/{deal_id}/agreement",
            headers={**headers, "Accept-Language": "fr"},
        )
        assert response.status_code == 200
        html = response.json()["html"]
        assert "Apporteur" in html
        assert "owner@example.com" in html
