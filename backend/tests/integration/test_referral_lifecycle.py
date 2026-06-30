"""Integration tests for the referral deal lifecycle (qualify/accept/activate/pay)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.application.notifications.ports import EmailMessage
from app.infrastructure.config import Settings
from app.interfaces.api.deps import get_email_sender
from app.main import create_app


class _CapturingSender:
    """Test double for the EmailSender port; records what would be sent."""

    def __init__(self) -> None:
        self.outbox: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> None:
        self.outbox.append(message)

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


class TestStats:
    async def test_empty_stats(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        response = await client.get("/api/v1/referrals/stats", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["total_deals"] == 0
        assert body["pipeline_expected"] == 0

    async def test_stats_after_sign_activate_pay(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        await client.post(f"/api/v1/referrals/{deal_id}/activate", headers=headers)
        await client.post(f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers)

        body = (await client.get("/api/v1/referrals/stats", headers=headers)).json()
        assert body["total_deals"] == 1
        assert body["active_deals"] == 1
        assert body["pipeline_expected"] == 12000.0
        assert body["monthly_run_rate"] == 1000.0
        assert body["collected"] == 1000.0
        assert body["outstanding"] == 11000.0


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


class TestInvoice:
    async def test_not_ready_before_signed(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _create(client, headers)
        response = await client.get(
            f"/api/v1/referrals/{deal_id}/installments/1/invoice", headers=headers
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "agreement.not_ready"

    async def test_invoice_html_after_signing(self, client: AsyncClient) -> None:
        headers = await _headers(client, "owner@example.com")
        deal_id = await _sign(client, headers)
        response = await client.get(
            f"/api/v1/referrals/{deal_id}/installments/1/invoice",
            headers={**headers, "Accept-Language": "fr"},
        )
        assert response.status_code == 200
        html = response.json()["html"]
        assert "Facture de commission" in html
        assert "owner@example.com" in html

    async def test_missing_installment_is_404(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        response = await client.get(
            f"/api/v1/referrals/{deal_id}/installments/99/invoice", headers=headers
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "installment.not_found"


class TestTimeline:
    async def test_timeline_after_full_flow(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        await client.post(f"/api/v1/referrals/{deal_id}/activate", headers=headers)
        await client.post(f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers)

        response = await client.get(f"/api/v1/referrals/{deal_id}/timeline", headers=headers)
        assert response.status_code == 200
        types = [entry["type"] for entry in response.json()]
        assert types[0] == "created"
        for expected in (
            "accepted_referrer",
            "accepted_placed",
            "signed",
            "activated",
            "payment_recorded",
        ):
            assert expected in types

    async def test_timeline_forbidden_for_others(self, client: AsyncClient) -> None:
        owner = await _headers(client, "owner@example.com")
        deal_id = await _create(client, owner)
        intruder = await _headers(client, "intruder@example.com")
        response = await client.get(f"/api/v1/referrals/{deal_id}/timeline", headers=intruder)
        assert response.status_code == 403


class TestDispute:
    async def test_dispute_freezes_then_resolve_restores(self, client: AsyncClient) -> None:
        headers = await _headers(client, "owner@example.com")
        deal_id = await _sign(client, headers)
        await client.post(f"/api/v1/referrals/{deal_id}/activate", headers=headers)

        disputed = await client.post(
            f"/api/v1/referrals/{deal_id}/dispute",
            json={"reason": "Le paiement de mars manque."},
            headers=headers,
        )
        assert disputed.status_code == 200
        body = disputed.json()
        assert body["status"] == "disputed"
        assert body["dispute_reason"] == "Le paiement de mars manque."

        # Frozen: paying an installment is refused.
        frozen = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers
        )
        assert frozen.status_code == 409
        assert frozen.json()["error"]["code"] == "referral.frozen"

        resolved = await client.post(
            f"/api/v1/referrals/{deal_id}/dispute/resolve", headers=headers
        )
        assert resolved.status_code == 200
        assert resolved.json()["status"] == "active"
        assert resolved.json()["dispute_reason"] is None

        # Unfrozen: paying works again.
        paid = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers
        )
        assert paid.status_code == 200
        assert paid.json()["status"] == "paid"

    async def test_dispute_requires_a_reason(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        response = await client.post(
            f"/api/v1/referrals/{deal_id}/dispute", json={"reason": "  "}, headers=headers
        )
        assert response.status_code == 422

    async def test_dispute_shows_in_timeline(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        await client.post(
            f"/api/v1/referrals/{deal_id}/dispute",
            json={"reason": "désaccord"},
            headers=headers,
        )
        timeline = await client.get(f"/api/v1/referrals/{deal_id}/timeline", headers=headers)
        types = [entry["type"] for entry in timeline.json()]
        assert "disputed" in types

    async def test_evidence_pack_after_signing(self, client: AsyncClient) -> None:
        headers = await _headers(client, "owner@example.com")
        deal_id = await _sign(client, headers)
        await client.post(
            f"/api/v1/referrals/{deal_id}/dispute",
            json={"reason": "facture impayée"},
            headers=headers,
        )
        response = await client.get(
            f"/api/v1/referrals/{deal_id}/evidence",
            headers={**headers, "Accept-Language": "fr"},
        )
        assert response.status_code == 200
        html = response.json()["html"]
        assert "Dossier de preuve" in html
        assert "facture impayée" in html
        assert "owner@example.com" in html

    async def test_evidence_not_ready_before_signed(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _create(client, headers)
        response = await client.get(f"/api/v1/referrals/{deal_id}/evidence", headers=headers)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "agreement.not_ready"

    async def test_dispute_forbidden_for_others(self, client: AsyncClient) -> None:
        owner = await _headers(client, "owner@example.com")
        deal_id = await _sign(client, owner)
        intruder = await _headers(client, "intruder@example.com")
        response = await client.post(
            f"/api/v1/referrals/{deal_id}/dispute",
            json={"reason": "pas mon deal"},
            headers=intruder,
        )
        assert response.status_code == 403


@pytest_asyncio.fixture
async def reminder_ctx(
    tmp_path: Path,
) -> AsyncIterator[tuple[AsyncClient, _CapturingSender]]:
    """A client whose email sender is a capturing double (no real mail)."""
    settings = Settings(
        jwt_secret="x" * 48,
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'test.db'}",
        auto_create_schema=True,
    )
    app = create_app(settings)
    await app.state.database.create_all()
    sender = _CapturingSender()
    app.dependency_overrides[get_email_sender] = lambda: sender
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, sender
    await app.state.database.dispose()


class TestReminders:
    async def test_reminder_sends_email_and_records_timestamp(
        self, reminder_ctx: tuple[AsyncClient, _CapturingSender]
    ) -> None:
        client, sender = reminder_ctx
        headers = await _headers(client, "owner@example.com")
        deal_id = await _sign(client, headers)

        response = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/remind", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["last_reminded_at"] is not None
        assert len(sender.outbox) == 1
        assert sender.outbox[0].to == "dev@example.com"

    async def test_reminder_blocked_when_already_paid(
        self, reminder_ctx: tuple[AsyncClient, _CapturingSender]
    ) -> None:
        client, sender = reminder_ctx
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        await client.post(f"/api/v1/referrals/{deal_id}/activate", headers=headers)
        await client.post(f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers)

        response = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/remind", headers=headers
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "installment.nothing_to_remind"
        assert sender.outbox == []

    async def test_reminder_appears_in_timeline(
        self, reminder_ctx: tuple[AsyncClient, _CapturingSender]
    ) -> None:
        client, _ = reminder_ctx
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        await client.post(f"/api/v1/referrals/{deal_id}/installments/1/remind", headers=headers)
        timeline = await client.get(f"/api/v1/referrals/{deal_id}/timeline", headers=headers)
        types = [entry["type"] for entry in timeline.json()]
        assert "reminder_sent" in types

    async def test_reminder_blocked_when_frozen(
        self, reminder_ctx: tuple[AsyncClient, _CapturingSender]
    ) -> None:
        client, sender = reminder_ctx
        headers = await _headers(client)
        deal_id = await _sign(client, headers)
        await client.post(
            f"/api/v1/referrals/{deal_id}/dispute", json={"reason": "litige"}, headers=headers
        )
        response = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/remind", headers=headers
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "referral.frozen"
        assert sender.outbox == []

    async def test_reminder_forbidden_for_non_owner(
        self, reminder_ctx: tuple[AsyncClient, _CapturingSender]
    ) -> None:
        client, _ = reminder_ctx
        owner = await _headers(client, "owner@example.com")
        deal_id = await _sign(client, owner)
        intruder = await _headers(client, "intruder@example.com")
        response = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/remind", headers=intruder
        )
        assert response.status_code == 403


async def _sign_and_pay(client: AsyncClient, headers: dict[str, str]) -> str:
    """Sign a deal and mark installment 1 as paid, ready for a proof."""
    deal_id = await _sign(client, headers)
    await client.post(f"/api/v1/referrals/{deal_id}/activate", headers=headers)
    await client.post(f"/api/v1/referrals/{deal_id}/installments/1/pay", headers=headers)
    return deal_id


_PDF = ("receipt.pdf", b"%PDF-1.4 fake receipt bytes", "application/pdf")


class TestPaymentProof:
    async def test_upload_then_download_a_proof(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign_and_pay(client, headers)

        uploaded = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/proof",
            files={"file": _PDF},
            headers=headers,
        )
        assert uploaded.status_code == 200
        proof = uploaded.json()["proof"]
        assert proof["filename"] == "receipt.pdf"
        assert proof["content_type"] == "application/pdf"
        assert proof["size"] == len(_PDF[1])

        detail = await client.get(f"/api/v1/referrals/{deal_id}", headers=headers)
        assert detail.json()["schedule"][0]["proof"]["filename"] == "receipt.pdf"

        downloaded = await client.get(
            f"/api/v1/referrals/{deal_id}/installments/1/proof", headers=headers
        )
        assert downloaded.status_code == 200
        assert downloaded.content == _PDF[1]
        assert downloaded.headers["content-type"].startswith("application/pdf")

    async def test_cannot_attach_proof_to_an_unpaid_installment(
        self, client: AsyncClient
    ) -> None:
        headers = await _headers(client)
        deal_id = await _sign(client, headers)  # installment 1 not paid
        response = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/proof",
            files={"file": _PDF},
            headers=headers,
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "installment.proof_requires_paid"

    async def test_rejects_an_unsupported_file_type(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign_and_pay(client, headers)
        response = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/proof",
            files={"file": ("archive.zip", b"PK\x03\x04 zip", "application/zip")},
            headers=headers,
        )
        assert response.status_code == 415
        assert response.json()["error"]["code"] == "proof.unsupported_type"

    async def test_download_404_when_no_proof(self, client: AsyncClient) -> None:
        headers = await _headers(client)
        deal_id = await _sign_and_pay(client, headers)
        response = await client.get(
            f"/api/v1/referrals/{deal_id}/installments/1/proof", headers=headers
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "proof.not_found"

    async def test_upload_forbidden_for_non_owner(self, client: AsyncClient) -> None:
        owner = await _headers(client, "owner@example.com")
        deal_id = await _sign_and_pay(client, owner)
        intruder = await _headers(client, "intruder@example.com")
        forbidden = await client.post(
            f"/api/v1/referrals/{deal_id}/installments/1/proof",
            files={"file": _PDF},
            headers=intruder,
        )
        assert forbidden.status_code == 403
