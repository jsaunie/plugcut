"""SQLAlchemy implementation of the profile repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.profiles.entities import Profile
from app.infrastructure.persistence.models import ProfileModel


def _to_domain(model: ProfileModel) -> Profile:
    return Profile(
        id=model.id,
        owner_id=model.owner_id,
        handle=model.handle,
        display_name=model.display_name,
        created_at=model.created_at,
        updated_at=model.updated_at,
        headline=model.headline,
        skills=list(model.skills),
        bio=model.bio,
        available=model.available,
    )


def _to_model(profile: Profile) -> ProfileModel:
    return ProfileModel(
        id=profile.id,
        owner_id=profile.owner_id,
        handle=profile.handle,
        display_name=profile.display_name,
        headline=profile.headline,
        skills=list(profile.skills),
        bio=profile.bio,
        available=profile.available,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


class SqlAlchemyProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, profile: Profile) -> None:
        self._session.add(_to_model(profile))

    async def save(self, profile: Profile) -> None:
        await self._session.merge(_to_model(profile))

    async def get_by_owner(self, owner_id: UUID) -> Profile | None:
        model = await self._session.scalar(
            select(ProfileModel).where(ProfileModel.owner_id == owner_id)
        )
        return _to_domain(model) if model is not None else None

    async def get_by_handle(self, handle: str) -> Profile | None:
        model = await self._session.scalar(
            select(ProfileModel).where(ProfileModel.handle == handle)
        )
        return _to_domain(model) if model is not None else None

    async def list_all(self, *, available_only: bool = False) -> list[Profile]:
        # Skill filtering is done in the use-case (portable across SQLite/Postgres
        # JSON columns); availability is a plain column, so filter it here.
        stmt = select(ProfileModel).order_by(ProfileModel.display_name)
        if available_only:
            stmt = stmt.where(ProfileModel.available.is_(True))
        result = await self._session.scalars(stmt)
        return [_to_domain(model) for model in result.all()]
