"""Profile use cases: manage your own profile, view anyone's public profile."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.profiles.errors import ProfileNotFound
from app.application.profiles.ports import ProfileRepository
from app.application.referrals.ports import ReferralRepository
from app.domain.profiles.entities import HandleTaken, Profile, normalize_handle
from app.domain.reputation.entities import Reputation
from app.domain.reputation.service import ReputationService


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class ProfileData:
    """Fields a user may set on their own profile."""

    handle: str
    display_name: str
    headline: str = ""
    bio: str = ""
    available: bool = True
    skills: list[str] = field(default_factory=list)


class UpsertMyProfile:
    """Create or replace the caller's profile, enforcing a globally unique handle."""

    def __init__(
        self,
        profiles: ProfileRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
        id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._profiles = profiles
        self._now = now
        self._id_factory = id_factory

    async def execute(self, owner_id: UUID, data: ProfileData) -> Profile:
        handle = normalize_handle(data.handle)
        clash = await self._profiles.get_by_handle(handle)
        if clash is not None and clash.owner_id != owner_id:
            raise HandleTaken
        now = self._now()
        existing = await self._profiles.get_by_owner(owner_id)
        if existing is None:
            profile = Profile(
                id=self._id_factory(),
                owner_id=owner_id,
                handle=handle,
                display_name=data.display_name,
                created_at=now,
                updated_at=now,
                headline=data.headline,
                skills=list(data.skills),
                bio=data.bio,
                available=data.available,
            )
            await self._profiles.add(profile)
            return profile
        existing.handle = handle
        existing.update(
            display_name=data.display_name,
            headline=data.headline,
            skills=list(data.skills),
            bio=data.bio,
            available=data.available,
            at=now,
        )
        await self._profiles.save(existing)
        return existing


class GetMyProfile:
    def __init__(self, profiles: ProfileRepository) -> None:
        self._profiles = profiles

    async def execute(self, owner_id: UUID) -> Profile | None:
        return await self._profiles.get_by_owner(owner_id)


@dataclass(frozen=True, slots=True)
class RankedProfile:
    """A directory entry: a profile with its computed trust standing."""

    profile: Profile
    reputation: Reputation


class SearchProfiles:
    """Browse the trust network: profiles filtered by skill, ranked by trust score.

    Reputation is computed per profile from sealed deals; the demo scale keeps this
    simple (one lookup per profile). A denormalized trust score would remove the
    per-profile query once the network grows.
    """

    def __init__(
        self,
        profiles: ProfileRepository,
        referrals: ReferralRepository,
        service: ReputationService | None = None,
    ) -> None:
        self._profiles = profiles
        self._referrals = referrals
        self._service = service or ReputationService()

    async def execute(
        self, *, skill: str | None = None, available_only: bool = True
    ) -> list[RankedProfile]:
        profiles = await self._profiles.list_all(available_only=available_only)
        needle = skill.strip().lower() if skill else None
        ranked: list[RankedProfile] = []
        for profile in profiles:
            if needle is not None and not any(needle in s.lower() for s in profile.skills):
                continue
            deals = await self._referrals.list_for_user(profile.owner_id)
            reputation = self._service.compute(deals, subject_id=profile.owner_id)
            ranked.append(RankedProfile(profile=profile, reputation=reputation))
        ranked.sort(key=lambda r: r.reputation.trust_score, reverse=True)
        return ranked


class GetPublicProfile:
    """View a profile by handle, with its trust standing computed from sealed deals."""

    def __init__(
        self,
        profiles: ProfileRepository,
        referrals: ReferralRepository,
        service: ReputationService | None = None,
    ) -> None:
        self._profiles = profiles
        self._referrals = referrals
        self._service = service or ReputationService()

    async def execute(self, handle: str) -> tuple[Profile, Reputation]:
        profile = await self._profiles.get_by_handle(handle.strip().lower())
        if profile is None:
            raise ProfileNotFound
        deals = await self._referrals.list_for_user(profile.owner_id)
        reputation = self._service.compute(deals, subject_id=profile.owner_id)
        return profile, reputation
