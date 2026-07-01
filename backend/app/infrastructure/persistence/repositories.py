"""SQLAlchemy implementation of the identity repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.identity.entities import User
from app.domain.identity.value_objects import Email
from app.infrastructure.persistence.models import UserModel


def _to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=Email(model.email),
        password_hash=model.password_hash,
        created_at=model.created_at,
        is_active=model.is_active,
        email_verified=model.email_verified,
    )


def _to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        email=user.email.value,
        password_hash=user.password_hash,
        created_at=user.created_at,
        is_active=user.is_active,
        email_verified=user.email_verified,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: Email) -> User | None:
        model = await self._session.scalar(
            select(UserModel).where(UserModel.email == email.value)
        )
        return _to_domain(model) if model is not None else None

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_domain(model) if model is not None else None

    async def add(self, user: User) -> None:
        self._session.add(_to_model(user))

    async def save(self, user: User) -> None:
        await self._session.merge(_to_model(user))
