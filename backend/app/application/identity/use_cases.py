"""Identity use cases: registration and authentication."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from app.application.identity.dtos import (
    AuthenticateUserCommand,
    RegisterUserCommand,
    TokenPair,
)
from app.application.identity.errors import (
    EmailAlreadyRegistered,
    InactiveUser,
    InvalidCredentials,
    InvalidToken,
)
from app.application.identity.ports import TokenService, UserRepository
from app.domain.identity.entities import User
from app.domain.identity.ports import PasswordHasher
from app.domain.identity.value_objects import Email


class RegisterUser:
    """Create a new account, rejecting duplicate emails."""

    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        *,
        now: Callable[[], datetime],
        id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._now = now
        self._id_factory = id_factory

    async def execute(self, command: RegisterUserCommand) -> User:
        email = Email(command.email)
        if await self._users.get_by_email(email) is not None:
            raise EmailAlreadyRegistered
        user = User.register(
            id=self._id_factory(),
            email=email,
            raw_password=command.password,
            hasher=self._hasher,
            now=self._now(),
        )
        await self._users.add(user)
        return user


class AuthenticateUser:
    """Verify credentials and issue an access/refresh token pair."""

    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenService,
    ) -> None:
        self._users = users
        self._hasher = hasher
        self._tokens = tokens

    async def execute(self, command: AuthenticateUserCommand) -> TokenPair:
        user = await self._users.get_by_email(Email(command.email))
        # Verify against a candidate even when the user is missing would be ideal to
        # avoid timing leaks; kept simple here, hardened at the API rate-limit layer.
        if user is None or not user.verify_password(command.password, self._hasher):
            raise InvalidCredentials
        if not user.is_active:
            raise InactiveUser
        return TokenPair(
            access_token=self._tokens.create_access_token(str(user.id)),
            refresh_token=self._tokens.create_refresh_token(str(user.id)),
        )


class RefreshAccessToken:
    """Exchange a valid refresh token for a fresh access/refresh pair."""

    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self._users = users
        self._tokens = tokens

    async def execute(self, refresh_token: str) -> TokenPair:
        claims = self._tokens.decode(refresh_token)
        if claims.token_type != "refresh":
            raise InvalidToken
        user = await self._users.get_by_id(UUID(claims.subject))
        if user is None or not user.is_active:
            raise InvalidToken
        return TokenPair(
            access_token=self._tokens.create_access_token(str(user.id)),
            refresh_token=self._tokens.create_refresh_token(str(user.id)),
        )
