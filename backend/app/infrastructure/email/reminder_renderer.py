"""Builds the localized payment-reminder email for a due commission installment.

Pure string templating (no I/O), FR/EN, all user-provided values HTML-escaped. The
recipient is the placed person (the payer); the email reminds them to settle the
commission owed to the referrer for one period.
"""

from __future__ import annotations

from html import escape

from app.application.notifications.ports import EmailMessage
from app.domain.billing.entities import CommissionInstallment
from app.domain.referrals.entities import Referral
from app.domain.shared.value_objects import Money

_LABELS: dict[str, dict[str, str]] = {
    "fr": {
        "subject": "Rappel : commission d'apport à régler",
        "greeting": "Bonjour,",
        "intro": (
            "Une commission d'apport arrive à échéance pour le deal référencé "
            "ci-dessous. Merci de procéder au règlement directement auprès de l'apporteur."
        ),
        "deal": "Référence",
        "period": "Période",
        "due": "Échéance",
        "amount": "Montant dû",
        "payTo": "À régler à",
        "outro": (
            "Le paiement se fait de particulier à particulier. Une fois réglé, "
            "l'apporteur marquera l'échéance comme payée dans Plugcut."
        ),
        "footer": "Email envoyé par Plugcut. Projet de démonstration.",
    },
    "en": {
        "subject": "Reminder: referral commission to settle",
        "greeting": "Hello,",
        "intro": (
            "A referral commission is coming due for the deal referenced below. "
            "Please settle it directly with the referrer."
        ),
        "deal": "Reference",
        "period": "Period",
        "due": "Due date",
        "amount": "Amount due",
        "payTo": "Pay to",
        "outro": (
            "Payment happens peer to peer. Once settled, the referrer will mark the "
            "installment as paid in Plugcut."
        ),
        "footer": "Email sent by Plugcut. Demonstration project.",
    },
}


def _money(value: Money) -> str:
    return f"{value.amount} {value.currency}"


class HtmlReminderEmailRenderer:
    def render(
        self,
        referral: Referral,
        installment: CommissionInstallment,
        *,
        referrer_email: str,
        locale: str,
    ) -> EmailMessage:
        labels = _LABELS.get(locale, _LABELS["en"])
        period = (
            f"{installment.period_start.isoformat()} - {installment.period_end.isoformat()}"
        )
        html = f"""<!doctype html>
<html lang="{escape(locale)}">
<head><meta charset="utf-8" /></head>
<body style="font-family: -apple-system, system-ui, sans-serif; color: #16140f;
             max-width: 560px; margin: 0 auto; padding: 1.5rem; line-height: 1.55;">
  <p style="font-weight: 700; letter-spacing: 0.05em; color: #6b7a00;">PLUGCUT</p>
  <p>{escape(labels['greeting'])}</p>
  <p style="color: #555;">{escape(labels['intro'])}</p>
  <table style="width: 100%; border-collapse: collapse; margin: 1.2rem 0;">
    <tr><td style="color:#666; padding:0.3rem 0;">{escape(labels['deal'])}</td>
        <td style="font-weight:600; text-align:right;">
          {escape(referral.client_reference)}</td></tr>
    <tr><td style="color:#666; padding:0.3rem 0;">{escape(labels['period'])}</td>
        <td style="font-weight:600; text-align:right;">{escape(period)}</td></tr>
    <tr><td style="color:#666; padding:0.3rem 0;">{escape(labels['due'])}</td>
        <td style="font-weight:600; text-align:right;">
          {escape(installment.due_date.isoformat())}</td></tr>
    <tr><td style="color:#666; padding:0.3rem 0;">{escape(labels['amount'])}</td>
        <td style="font-weight:700; text-align:right;">
          {escape(_money(installment.amount_due))}</td></tr>
    <tr><td style="color:#666; padding:0.3rem 0;">{escape(labels['payTo'])}</td>
        <td style="font-weight:600; text-align:right;">{escape(referrer_email)}</td></tr>
  </table>
  <p style="color: #555;">{escape(labels['outro'])}</p>
  <p style="margin-top: 2rem; font-size: 0.78rem; color: #999;">
    {escape(labels['footer'])}</p>
</body>
</html>"""
        return EmailMessage(
            to=referral.placed_person_email,
            subject=labels["subject"],
            html=html,
        )
