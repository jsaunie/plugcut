"""Intro request entity and its small state machine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.shared.errors import (
    IllegalStateTransition,
    InvariantViolation,
)

_MAX_MESSAGE = 1000


class IntroStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class CannotIntroSelf(InvariantViolation):
    code = "intro.cannot_self"


class IntroAlreadyResolved(IllegalStateTransition):
    """The request was already accepted or declined; it cannot change again."""

    code = "intro.already_resolved"


@dataclass(slots=True)
class IntroRequest:
    """A warm introduction request from one member to a profile owner."""

    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    message: str
    created_at: datetime
    status: IntroStatus = IntroStatus.PENDING
    responded_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.from_user_id == self.to_user_id:
            raise CannotIntroSelf
        self.message = self.message.strip()
        if len(self.message) > _MAX_MESSAGE:
            raise InvariantViolation("intro message is too long")

    @property
    def is_pending(self) -> bool:
        return self.status is IntroStatus.PENDING

    def accept(self, *, at: datetime) -> None:
        self._resolve(IntroStatus.ACCEPTED, at=at)

    def decline(self, *, at: datetime) -> None:
        self._resolve(IntroStatus.DECLINED, at=at)

    def _resolve(self, to: IntroStatus, *, at: datetime) -> None:
        if self.status is not IntroStatus.PENDING:
            raise IntroAlreadyResolved
        self.status = to
        self.responded_at = at
