"""Identity domain errors (coded for i18n at the API edge)."""

from __future__ import annotations

from app.domain.shared.errors import InvariantViolation


class InvalidEmail(InvariantViolation):
    code = "identity.invalid_email"


class WeakPassword(InvariantViolation):
    code = "identity.weak_password"
