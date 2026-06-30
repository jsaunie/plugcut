"""Resend adapter for the :class:`EmailSender` port.

Sends transactional email through the Resend HTTP API. Provider failures are wrapped in
:class:`EmailDeliveryFailed` so the API layer can map them to a localized error instead
of leaking an httpx exception.
"""

from __future__ import annotations

import logging

import httpx

from app.application.notifications.errors import EmailDeliveryFailed
from app.application.notifications.ports import EmailMessage

logger = logging.getLogger(__name__)


class ResendEmailSender:
    _ENDPOINT = "https://api.resend.com/emails"

    def __init__(self, api_key: str, sender: str, *, timeout: float = 10.0) -> None:
        self._api_key = api_key
        self._sender = sender
        self._timeout = timeout

    async def send(self, message: EmailMessage) -> None:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    self._ENDPOINT,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "from": self._sender,
                        "to": [message.to],
                        "subject": message.subject,
                        "html": message.html,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Resend delivery failed for %s: %s", message.to, exc)
            raise EmailDeliveryFailed from exc
