"""bcrypt-based password hasher — the concrete PasswordHasher adapter."""

from __future__ import annotations

import bcrypt

# bcrypt only consumes the first 72 bytes of the password; longer inputs are truncated
# by the algorithm. We hard-cap explicitly so behaviour is obvious rather than silent.
_BCRYPT_MAX_BYTES = 72


class BcryptPasswordHasher:
    def __init__(self, rounds: int = 12) -> None:
        self._rounds = rounds

    def hash(self, raw: str) -> str:
        return bcrypt.hashpw(self._encode(raw), bcrypt.gensalt(self._rounds)).decode()

    def verify(self, raw: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(self._encode(raw), hashed.encode())
        except ValueError:
            # Malformed stored hash — treat as a failed verification, never crash auth.
            return False

    @staticmethod
    def _encode(raw: str) -> bytes:
        return raw.encode("utf-8")[:_BCRYPT_MAX_BYTES]
