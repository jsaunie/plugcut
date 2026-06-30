"""Ports for outbound notifications (email).

The application depends on these abstractions; concrete adapters (Resend, a logging
fallback, HTML renderers) live in infrastructure. Keeping the email body behind a
renderer port means content stays localized and testable, and the transport behind a
sender port means we can swap Resend for SMTP or a fake without touching use cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.domain.billing.entities import CommissionInstallment
    from app.domain.referrals.entities import Referral

__all__ = ["EmailMessage", "EmailSender", "ReminderEmailRenderer"]


@dataclass(frozen=True, slots=True)
class EmailMessage:
    """A ready-to-send email. The body is pre-rendered and localized."""

    to: str
    subject: str
    html: str


class EmailSender(Protocol):
    """Transports an :class:`EmailMessage`. Implemented by Resend (and a fallback)."""

    async def send(self, message: EmailMessage) -> None: ...


class ReminderEmailRenderer(Protocol):
    """Builds the localized payment-reminder email for one due installment."""

    def render(
        self,
        referral: Referral,
        installment: CommissionInstallment,
        *,
        referrer_email: str,
        locale: str,
    ) -> EmailMessage: ...
