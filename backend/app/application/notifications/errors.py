"""Application-level notification errors (coded for i18n)."""

from __future__ import annotations

from app.domain.shared.errors import DomainError


class EmailDeliveryFailed(DomainError):
    """The email provider rejected or failed to accept the message."""

    code = "email.delivery_failed"
