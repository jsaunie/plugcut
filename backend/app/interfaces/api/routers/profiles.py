"""Profile routes: manage your own profile, view anyone's public profile + trust."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.profiles.use_cases import (
    GetMyProfile,
    GetPublicProfile,
    ProfileData,
    SearchProfiles,
    UpsertMyProfile,
)
from app.domain.profiles.entities import Profile
from app.interfaces.api.deps import (
    CurrentUser,
    get_my_profile,
    get_public_profile,
    get_search_profiles,
    get_session,
    get_upsert_profile,
)
from app.interfaces.api.routers.reputation import ReputationResponse

router = APIRouter(tags=["profiles"])


class ProfileResponse(BaseModel):
    id: UUID
    handle: str
    display_name: str
    headline: str
    skills: list[str]
    bio: str
    available: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, profile: Profile) -> ProfileResponse:
        return cls(
            id=profile.id,
            handle=profile.handle,
            display_name=profile.display_name,
            headline=profile.headline,
            skills=profile.skills,
            bio=profile.bio,
            available=profile.available,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )


class ProfileUpsertRequest(BaseModel):
    handle: str
    display_name: str
    headline: str = ""
    bio: str = ""
    available: bool = True
    skills: list[str] = Field(default_factory=list)


class PublicProfileResponse(BaseModel):
    profile: ProfileResponse
    reputation: ReputationResponse


@router.get("/profiles", response_model=list[PublicProfileResponse])
async def search_profiles(
    current_user: CurrentUser,
    use_case: Annotated[SearchProfiles, Depends(get_search_profiles)],
    skill: Annotated[str | None, Query(max_length=40)] = None,
    available: bool = True,
) -> list[PublicProfileResponse]:
    ranked = await use_case.execute(skill=skill, available_only=available)
    return [
        PublicProfileResponse(
            profile=ProfileResponse.from_domain(item.profile),
            reputation=ReputationResponse.from_domain(item.reputation),
        )
        for item in ranked
    ]


@router.get("/profile/me", response_model=ProfileResponse)
async def get_own_profile(
    current_user: CurrentUser,
    use_case: Annotated[GetMyProfile, Depends(get_my_profile)],
) -> ProfileResponse:
    profile = await use_case.execute(current_user.id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return ProfileResponse.from_domain(profile)


@router.put("/profile/me", response_model=ProfileResponse)
async def upsert_own_profile(
    payload: ProfileUpsertRequest,
    current_user: CurrentUser,
    use_case: Annotated[UpsertMyProfile, Depends(get_upsert_profile)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileResponse:
    profile = await use_case.execute(
        current_user.id,
        ProfileData(
            handle=payload.handle,
            display_name=payload.display_name,
            headline=payload.headline,
            bio=payload.bio,
            available=payload.available,
            skills=payload.skills,
        ),
    )
    await session.commit()
    return ProfileResponse.from_domain(profile)


@router.get("/profiles/{handle}", response_model=PublicProfileResponse)
async def public_profile(
    handle: str,
    use_case: Annotated[GetPublicProfile, Depends(get_public_profile)],
) -> PublicProfileResponse:
    profile, reputation = await use_case.execute(handle)
    return PublicProfileResponse(
        profile=ProfileResponse.from_domain(profile),
        reputation=ReputationResponse.from_domain(reputation),
    )
