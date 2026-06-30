"""Unit tests for the HTML agreement renderer."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.domain.referrals.entities import Referral
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.value_objects import Money, Percentage
from app.infrastructure.agreements.html_renderer import HtmlAgreementRenderer


def _signed_referral() -> Referral:
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
    referral.accept_as_referrer(at=at)
    referral.accept_as_placed_person(at=at)
    return referral


class TestHtmlAgreementRenderer:
    def test_contains_parties_terms_and_attribution(self) -> None:
        referral = _signed_referral()
        html = HtmlAgreementRenderer().render(
            referral, referrer_email="me@example.com", locale="fr"
        )
        assert "Apporteur" in html
        assert "me@example.com" in html
        assert "dev@example.com" in html
        assert "ACME (discreet)" in html
        assert referral.attribution_hash is not None
        assert referral.attribution_hash in html

    def test_localized_english(self) -> None:
        html = HtmlAgreementRenderer().render(
            _signed_referral(), referrer_email="me@example.com", locale="en"
        )
        assert "Referral agreement" in html

    def test_escapes_html_in_client_reference(self) -> None:
        referral = _signed_referral()
        referral.client_reference = "<script>x</script>"
        html = HtmlAgreementRenderer().render(referral, referrer_email="m@e.com", locale="en")
        assert "<script>x</script>" not in html
        assert "&lt;script&gt;" in html
