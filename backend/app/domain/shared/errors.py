"""Base domain errors.

Domain errors carry a stable ``code`` so the API layer can translate them into
localized (i18n) messages instead of leaking raw English strings to users.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain rule violations.

    ``code`` is a stable, machine-readable identifier (e.g. ``"money.currency_mismatch"``)
    used as an i18n key at the edge. The message is a developer-facing fallback only.
    """

    code: str = "domain.error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.code)


class InvariantViolation(DomainError):
    """A value object or entity was constructed in an invalid state."""

    code = "domain.invariant_violation"


class IllegalStateTransition(DomainError):
    """An aggregate was asked to move to a state it cannot reach from its current one."""

    code = "domain.illegal_state_transition"
