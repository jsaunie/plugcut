"""Unit tests for the HTML invoice renderer."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from app.domain.billing.services import CommissionScheduleService
from app.domain.referrals.entities import Referral
from app.domain.referrals.value_objects import CommissionTerms
from app.domain.shared.value_objects import Money, Percentage
from app.infrastructure.invoices.html_renderer import HtmlInvoiceRenderer


def _referral_and_first_installment() -> tuple[Referral, object]:
    referral = Referral(
        id=uuid4(),
        referrer_id=uuid4(),
        placed_person_email="dev@example.com",
        client_reference="ACME",
        terms=CommissionTerms(
            daily_rate=Money(Decimal("500")),
            commission=Percentage(Decimal("10")),
            duration_months=12,
        ),
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    schedule = CommissionScheduleService().generate(referral.terms, start_date=date(2026, 1, 1))
    return referral, schedule.installments[0]


class TestHtmlInvoiceRenderer:
    def test_contains_number_parties_and_amount(self) -> None:
        referral, installment = _referral_and_first_installment()
        html = HtmlInvoiceRenderer().render(
            referral, installment, referrer_email="me@example.com", locale="fr"
        )
        assert "Facture de commission" in html
        assert "me@example.com" in html
        assert "dev@example.com" in html
        assert "PLG-" in html
        assert "1000.00" in html  # 500 x 20 days x 10%

    def test_localized_english(self) -> None:
        referral, installment = _referral_and_first_installment()
        html = HtmlInvoiceRenderer().render(
            referral, installment, referrer_email="m@e.com", locale="en"
        )
        assert "Referral commission invoice" in html
