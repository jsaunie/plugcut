"""Unit tests for the HTML payment-reminder email renderer."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.domain.billing.entities import CommissionInstallment
from app.domain.referrals.entities import Referral
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.value_objects import Money, Percentage
from app.infrastructure.email.reminder_renderer import HtmlReminderEmailRenderer


def _referral() -> Referral:
    from datetime import UTC, datetime

    return Referral(
        id=uuid4(),
        referrer_id=uuid4(),
        placed_person_email="payer@example.com",
        client_reference="ACME (discreet)",
        terms=CommissionTerms(
            daily_rate=Money(Decimal("500")),
            commission=Percentage(Decimal("10")),
            duration_months=12,
        ),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _installment() -> CommissionInstallment:
    return CommissionInstallment(
        sequence=1,
        period_start=date(2026, 1, 1),
        period_end=date(2026, 1, 31),
        due_date=date(2026, 2, 15),
        expected_days=20,
        expected_amount=Money(Decimal("1000")),
    )


class TestHtmlReminderEmailRenderer:
    def test_addresses_the_placed_person_with_the_details(self) -> None:
        message = HtmlReminderEmailRenderer().render(
            _referral(), _installment(), referrer_email="me@example.com", locale="fr"
        )
        assert message.to == "payer@example.com"
        assert "Rappel" in message.subject
        assert "1000.00 EUR" in message.html
        assert "me@example.com" in message.html
        assert "ACME (discreet)" in message.html

    def test_localized_english(self) -> None:
        message = HtmlReminderEmailRenderer().render(
            _referral(), _installment(), referrer_email="me@example.com", locale="en"
        )
        assert "Reminder" in message.subject
        assert "Amount due" in message.html

    def test_escapes_html_in_client_reference(self) -> None:
        referral = _referral()
        referral.client_reference = "<script>x</script>"
        message = HtmlReminderEmailRenderer().render(
            referral, _installment(), referrer_email="m@e.com", locale="en"
        )
        assert "<script>x</script>" not in message.html
        assert "&lt;script&gt;" in message.html
