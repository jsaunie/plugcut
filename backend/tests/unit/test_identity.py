"""Unit tests for the identity domain and use cases."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.application.identity.dtos import AuthenticateUserCommand, RegisterUserCommand
from app.application.identity.errors import (
    EmailAlreadyRegistered,
    InactiveUser,
    InvalidCredentials,
)
from app.application.identity.use_cases import AuthenticateUser, RegisterUser
from app.domain.identity.entities import User
from app.domain.identity.errors import InvalidEmail, WeakPassword
from app.domain.identity.value_objects import Email
from tests.fakes import FakePasswordHasher, InMemoryUserRepository


def _now() -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC)


class TestEmail:
    def test_normalizes(self) -> None:
        assert Email("  Dev@Example.COM ").value == "dev@example.com"

    @pytest.mark.parametrize("bad", ["no-at", "a@b", "@b.com", "a@b."])
    def test_rejects_invalid(self, bad: str) -> None:
        with pytest.raises(InvalidEmail):
            Email(bad)


class TestUser:
    def test_register_hashes_password(self) -> None:
        user = User.register(
            id=uuid4(),
            email=Email("dev@example.com"),
            raw_password="supersecret",
            hasher=FakePasswordHasher(),
            now=_now(),
        )
        assert user.password_hash != "supersecret"
        assert user.verify_password("supersecret", FakePasswordHasher())

    def test_rejects_weak_password(self) -> None:
        with pytest.raises(WeakPassword):
            User.register(
                id=uuid4(),
                email=Email("dev@example.com"),
                raw_password="short",
                hasher=FakePasswordHasher(),
                now=_now(),
            )


class TestRegisterUser:
    async def test_creates_account(self) -> None:
        repo = InMemoryUserRepository()
        use_case = RegisterUser(repo, FakePasswordHasher(), now=_now)
        user = await use_case.execute(RegisterUserCommand("dev@example.com", "supersecret"))
        assert await repo.get_by_email(Email("dev@example.com")) is user

    async def test_rejects_duplicate_email(self) -> None:
        repo = InMemoryUserRepository()
        use_case = RegisterUser(repo, FakePasswordHasher(), now=_now)
        await use_case.execute(RegisterUserCommand("dev@example.com", "supersecret"))
        with pytest.raises(EmailAlreadyRegistered):
            await use_case.execute(RegisterUserCommand("DEV@example.com", "another-one"))


class _StubTokens:
    def create_access_token(self, subject: str) -> str:
        return f"access::{subject}"

    def create_refresh_token(self, subject: str) -> str:
        return f"refresh::{subject}"

    def decode(self, token: str) -> object:  # pragma: no cover - unused here
        raise NotImplementedError


class TestAuthenticateUser:
    async def _seed(self, repo: InMemoryUserRepository, *, active: bool = True) -> None:
        register = RegisterUser(repo, FakePasswordHasher(), now=_now)
        user = await register.execute(RegisterUserCommand("dev@example.com", "supersecret"))
        user.is_active = active

    async def test_issues_tokens_on_valid_credentials(self) -> None:
        repo = InMemoryUserRepository()
        await self._seed(repo)
        auth = AuthenticateUser(repo, FakePasswordHasher(), _StubTokens())
        tokens = await auth.execute(AuthenticateUserCommand("dev@example.com", "supersecret"))
        assert tokens.access_token.startswith("access::")
        assert tokens.token_type == "bearer"

    async def test_rejects_wrong_password(self) -> None:
        repo = InMemoryUserRepository()
        await self._seed(repo)
        auth = AuthenticateUser(repo, FakePasswordHasher(), _StubTokens())
        with pytest.raises(InvalidCredentials):
            await auth.execute(AuthenticateUserCommand("dev@example.com", "wrong-pass"))

    async def test_rejects_unknown_email(self) -> None:
        auth = AuthenticateUser(InMemoryUserRepository(), FakePasswordHasher(), _StubTokens())
        with pytest.raises(InvalidCredentials):
            await auth.execute(AuthenticateUserCommand("ghost@example.com", "supersecret"))

    async def test_rejects_inactive_user(self) -> None:
        repo = InMemoryUserRepository()
        await self._seed(repo, active=False)
        auth = AuthenticateUser(repo, FakePasswordHasher(), _StubTokens())
        with pytest.raises(InactiveUser):
            await auth.execute(AuthenticateUserCommand("dev@example.com", "supersecret"))


class TestAccountManagement:
    async def _seed(self) -> tuple[InMemoryUserRepository, User]:
        repo = InMemoryUserRepository()
        user = User.register(
            id=uuid4(),
            email=Email("dev@example.com"),
            raw_password="supersecret",
            hasher=FakePasswordHasher(),
            now=_now(),
        )
        await repo.add(user)
        return repo, user

    async def test_change_password(self) -> None:
        from app.application.identity.use_cases import ChangePassword

        repo, user = await self._seed()
        await ChangePassword(repo, FakePasswordHasher()).execute(
            user.id, current_password="supersecret", new_password="brandnewpass"
        )
        assert user.verify_password("brandnewpass", FakePasswordHasher())

    async def test_change_password_rejects_wrong_current(self) -> None:
        from app.application.identity.use_cases import ChangePassword

        repo, user = await self._seed()
        with pytest.raises(InvalidCredentials):
            await ChangePassword(repo, FakePasswordHasher()).execute(
                user.id, current_password="wrong", new_password="brandnewpass"
            )

    async def test_change_password_rejects_weak(self) -> None:
        from app.application.identity.use_cases import ChangePassword

        repo, user = await self._seed()
        with pytest.raises(WeakPassword):
            await ChangePassword(repo, FakePasswordHasher()).execute(
                user.id, current_password="supersecret", new_password="short"
            )

    async def test_change_email(self) -> None:
        from app.application.identity.use_cases import ChangeEmail

        repo, user = await self._seed()
        await ChangeEmail(repo, FakePasswordHasher()).execute(
            user.id, new_email="New@Example.com", current_password="supersecret"
        )
        assert user.email.value == "new@example.com"
        assert await repo.get_by_email(Email("new@example.com")) is not None

    async def test_change_email_rejects_taken(self) -> None:
        from app.application.identity.use_cases import ChangeEmail

        repo, user = await self._seed()
        await repo.add(
            User.register(
                id=uuid4(),
                email=Email("taken@example.com"),
                raw_password="supersecret",
                hasher=FakePasswordHasher(),
                now=_now(),
            )
        )
        with pytest.raises(EmailAlreadyRegistered):
            await ChangeEmail(repo, FakePasswordHasher()).execute(
                user.id, new_email="taken@example.com", current_password="supersecret"
            )

    async def test_delete_account_erases_after_password_check(self) -> None:
        from app.application.identity.use_cases import DeleteAccount
        from tests.fakes import InMemoryAccountEraser

        repo, user = await self._seed()
        eraser = InMemoryAccountEraser()
        await DeleteAccount(repo, FakePasswordHasher(), eraser).execute(
            user.id, current_password="supersecret"
        )
        assert eraser.erased == [user.id]

    async def test_delete_account_rejects_wrong_password(self) -> None:
        from app.application.identity.use_cases import DeleteAccount
        from tests.fakes import InMemoryAccountEraser

        repo, user = await self._seed()
        eraser = InMemoryAccountEraser()
        with pytest.raises(InvalidCredentials):
            await DeleteAccount(repo, FakePasswordHasher(), eraser).execute(
                user.id, current_password="nope"
            )
        assert eraser.erased == []
