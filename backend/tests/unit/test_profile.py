"""Unit tests for the Profile entity and handle rules."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.profiles.entities import (
    InvalidHandle,
    Profile,
    normalize_handle,
)
from app.domain.shared.errors import InvariantViolation


def make_profile(**overrides: object) -> Profile:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "owner_id": uuid4(),
        "handle": "jean-dev",
        "display_name": "Jean Dev",
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return Profile(**defaults)  # type: ignore[arg-type]


class TestHandle:
    def test_lowercases_and_accepts_valid(self) -> None:
        assert normalize_handle("Jean-Dev") == "jean-dev"

    @pytest.mark.parametrize("bad", ["ab", "-jean", "jean-", "jean dev", "jean_dev", "a" * 41])
    def test_rejects_malformed(self, bad: str) -> None:
        with pytest.raises(InvalidHandle):
            normalize_handle(bad)

    def test_profile_normalizes_its_handle(self) -> None:
        assert make_profile(handle="ACME-Corp").handle == "acme-corp"


class TestProfileInvariants:
    def test_requires_display_name(self) -> None:
        with pytest.raises(InvariantViolation):
            make_profile(display_name="   ")

    def test_rejects_too_many_skills(self) -> None:
        with pytest.raises(InvariantViolation):
            make_profile(skills=[f"skill{i}" for i in range(21)])

    def test_drops_blank_skills(self) -> None:
        profile = make_profile(skills=["Vue", "  ", "FastAPI"])
        assert profile.skills == ["Vue", "FastAPI"]

    def test_update_revalidates(self) -> None:
        profile = make_profile()
        later = datetime(2026, 2, 1, tzinfo=UTC)
        profile.update(
            display_name="Jean R.",
            headline="Backend freelance",
            skills=["Python"],
            bio="10 ans d'XP",
            available=False,
            at=later,
        )
        assert profile.display_name == "Jean R."
        assert profile.available is False
        assert profile.updated_at == later
        with pytest.raises(InvariantViolation):
            profile.update(
                display_name="",
                headline="",
                skills=[],
                bio="",
                available=True,
                at=later,
            )
