"""Identity value objects."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.identity.errors import InvalidEmail

# Pragmatic email shape check — deliverability is verified out of band, not by regex.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Email:
    """A normalized (trimmed, lower-cased) email address."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise InvalidEmail
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
