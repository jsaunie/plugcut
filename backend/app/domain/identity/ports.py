"""Ports (interfaces) the identity domain depends on, implemented by infrastructure."""

from __future__ import annotations

from typing import Protocol


class PasswordHasher(Protocol):
    """Hashes and verifies passwords. The domain never sees the algorithm."""

    def hash(self, raw: str) -> str: ...

    def verify(self, raw: str, hashed: str) -> bool: ...
