"""Unit tests for the HTML dispute evidence pack renderer."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.application.referrals.dtos import TimelineEntry
from app.domain.referrals.entities import Referral
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.value_objects import Money, Percentage
from app.infrastructure.evidence.html_renderer import HtmlEvidenceRenderer


def _disputed_referral() -> Referral:
    referral = Referral(
        id=uuid4(),
        referrer_id=uuid4(),
        placed_person_email="dev@example.com",
        client_reference="ACME (discreet)",
        terms=CommissionTerms(
            daily_rate=Money(Decimal("500")),
            commission=Percentage(Decimal("10")),
            duration_months=12,
        ),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    at = datetime(2026, 1, 2, tzinfo=UTC)
    referral.qualify()
    referral.accept_as_referrer(at=at, signature="Jean")
    referral.accept_as_placed_person(at=at, signature="Dev")
    referral.dispute(at=datetime(2026, 3, 1, tzinfo=UTC), reason="Mars impayé", by=uuid4())
    return referral


def _timeline(referral: Referral) -> list[TimelineEntry]:
    return [
        TimelineEntry("created", referral.created_at),
        TimelineEntry("signed", datetime(2026, 1, 2, tzinfo=UTC)),
        TimelineEntry("disputed", datetime(2026, 3, 1, tzinfo=UTC), "Mars impayé"),
    ]


class TestHtmlEvidenceRenderer:
    def test_contains_parties_proof_reason_and_timeline(self) -> None:
        referral = _disputed_referral()
        html = HtmlEvidenceRenderer().render(
            referral,
            referrer_email="me@example.com",
            timeline=_timeline(referral),
            locale="fr",
        )
        assert "Dossier de preuve" in html
        assert "me@example.com" in html
        assert "dev@example.com" in html
        assert "Mars impayé" in html
        assert referral.attribution_hash is not None
        assert referral.attribution_hash in html
        assert "Jean" in html  # referrer signature
        assert "Litige déclaré" in html

    def test_localized_english(self) -> None:
        referral = _disputed_referral()
        html = HtmlEvidenceRenderer().render(
            referral,
            referrer_email="me@example.com",
            timeline=_timeline(referral),
            locale="en",
        )
        assert "Evidence pack" in html
        assert "Dispute raised" in html

    def test_escapes_html_in_dispute_reason(self) -> None:
        referral = _disputed_referral()
        referral.dispute_reason = "<script>x</script>"
        html = HtmlEvidenceRenderer().render(
            referral,
            referrer_email="m@e.com",
            timeline=_timeline(referral),
            locale="en",
        )
        assert "<script>x</script>" not in html
        assert "&lt;script&gt;" in html
