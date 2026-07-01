"""Unit tests for the IntroRequest entity."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.intros.entities import (
    CannotIntroSelf,
    IntroAlreadyResolved,
    IntroRequest,
    IntroStatus,
)
from app.domain.shared.errors import InvariantViolation


def make_intro(**overrides: object) -> IntroRequest:
    defaults: dict[str, object] = {
        "id": uuid4(),
        "from_user_id": uuid4(),
        "to_user_id": uuid4(),
        "message": "On a un client commun, on se cale ?",
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    defaults.update(overrides)
    return IntroRequest(**defaults)  # type: ignore[arg-type]


class TestIntroRequest:
    def test_starts_pending(self) -> None:
        assert make_intro().status is IntroStatus.PENDING

    def test_cannot_intro_yourself(self) -> None:
        me = uuid4()
        with pytest.raises(CannotIntroSelf):
            make_intro(from_user_id=me, to_user_id=me)

    def test_rejects_overlong_message(self) -> None:
        with pytest.raises(InvariantViolation):
            make_intro(message="x" * 1001)

    def test_accept_resolves(self) -> None:
        intro = make_intro()
        at = datetime(2026, 1, 2, tzinfo=UTC)
        intro.accept(at=at)
        assert intro.status is IntroStatus.ACCEPTED
        assert intro.responded_at == at

    def test_decline_resolves(self) -> None:
        intro = make_intro()
        intro.decline(at=datetime(2026, 1, 2, tzinfo=UTC))
        assert intro.status is IntroStatus.DECLINED

    def test_cannot_resolve_twice(self) -> None:
        intro = make_intro()
        intro.accept(at=datetime(2026, 1, 2, tzinfo=UTC))
        with pytest.raises(IntroAlreadyResolved):
            intro.decline(at=datetime(2026, 1, 3, tzinfo=UTC))
