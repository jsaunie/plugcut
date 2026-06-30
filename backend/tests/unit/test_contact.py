"""Unit tests for the Contact aggregate."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from app.domain.contacts.entities import Contact, ContactNameRequired


def _contact(**overrides: Any) -> Contact:
    base: dict[str, Any] = {
        "id": uuid4(),
        "owner_id": uuid4(),
        "full_name": "Marie Coach",
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return Contact(**base)


class TestContact:
    def test_requires_a_name(self) -> None:
        with pytest.raises(ContactNameRequired):
            _contact(full_name="   ")

    def test_trims_name_and_cleans_tags(self) -> None:
        contact = _contact(full_name="  Marie  ", tags=["  dev ", "", "coach"])
        assert contact.full_name == "Marie"
        assert contact.tags == ["dev", "coach"]
