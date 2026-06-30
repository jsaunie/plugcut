"""Fallback :class:`EmailSender` used when no provider is configured.

Logs the message instead of sending it, so the app runs end to end in local/demo
environments without a Resend API key and no real mail leaves the machine.
"""

from __future__ import annotations

import logging

from app.application.notifications.ports import EmailMessage

logger = logging.getLogger(__name__)


class LoggingEmailSender:
    async def send(self, message: EmailMessage) -> None:
        logger.info(
            "EMAIL not sent (no provider configured) | to=%s | subject=%s",
            message.to,
            message.subject,
        )
