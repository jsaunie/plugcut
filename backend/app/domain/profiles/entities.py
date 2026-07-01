"""Profile entity and its invariants."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.shared.errors import DomainError, InvariantViolation

_HANDLE_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,38}[a-z0-9])$")
_MAX_SKILLS = 20
_MAX_SKILL_LEN = 40
_MAX_HEADLINE = 160
_MAX_DISPLAY_NAME = 120
_MAX_BIO = 2000


class InvalidHandle(DomainError):
    """The handle is not a valid public slug (3-40 chars, a-z, 0-9, hyphen)."""

    code = "profile.invalid_handle"


class HandleTaken(DomainError):
    """Another user already owns this handle."""

    code = "profile.handle_taken"


def normalize_handle(raw: str) -> str:
    """Lowercase and validate a handle, raising :class:`InvalidHandle` if malformed."""
    handle = raw.strip().lower()
    if not _HANDLE_RE.match(handle):
        raise InvalidHandle
    return handle


@dataclass(slots=True)
class Profile:
    """A freelancer's public identity, owned by exactly one user."""

    id: UUID
    owner_id: UUID
    handle: str
    display_name: str
    created_at: datetime
    updated_at: datetime
    headline: str = ""
    skills: list[str] = field(default_factory=list)
    bio: str = ""
    available: bool = True

    def __post_init__(self) -> None:
        self.handle = normalize_handle(self.handle)
        self.display_name = self.display_name.strip()
        if not self.display_name:
            raise InvariantViolation("display_name is required")
        if len(self.display_name) > _MAX_DISPLAY_NAME:
            raise InvariantViolation("display_name is too long")
        if len(self.headline) > _MAX_HEADLINE:
            raise InvariantViolation("headline is too long")
        if len(self.bio) > _MAX_BIO:
            raise InvariantViolation("bio is too long")
        if len(self.skills) > _MAX_SKILLS:
            raise InvariantViolation("too many skills")
        cleaned: list[str] = []
        for skill in self.skills:
            s = skill.strip()
            if not s:
                continue
            if len(s) > _MAX_SKILL_LEN:
                raise InvariantViolation("a skill label is too long")
            cleaned.append(s)
        self.skills = cleaned

    def update(
        self,
        *,
        display_name: str,
        headline: str,
        skills: list[str],
        bio: str,
        available: bool,
        at: datetime,
    ) -> None:
        self.display_name = display_name
        self.headline = headline
        self.skills = skills
        self.bio = bio
        self.available = available
        self.updated_at = at
        self.__post_init__()
