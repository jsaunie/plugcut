"""Intro use cases: request a warm intro, list your intros, respond to one."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.intros.errors import (
    IntroAlreadyPending,
    IntroForbidden,
    IntroNotFound,
    ProfileRequired,
)
from app.application.intros.ports import IntroRepository
from app.application.profiles.errors import ProfileNotFound
from app.application.profiles.ports import ProfileRepository
from app.domain.intros.entities import IntroRequest
from app.domain.profiles.entities import Profile


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class IntroView:
    """An intro paired with the counterpart's profile (the other party)."""

    intro: IntroRequest
    counterpart: Profile | None


class RequestIntro:
    """Ask to be introduced to a profile owner. Only network members may ask."""

    def __init__(
        self,
        intros: IntroRepository,
        profiles: ProfileRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
        id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._intros = intros
        self._profiles = profiles
        self._now = now
        self._id_factory = id_factory

    async def execute(
        self, from_user_id: UUID, handle: str, message: str
    ) -> IntroRequest:
        target = await self._profiles.get_by_handle(handle.strip().lower())
        if target is None:
            raise ProfileNotFound
        # Warm gate: you must be a member (have a profile) to reach into the network.
        if await self._profiles.get_by_owner(from_user_id) is None:
            raise ProfileRequired
        if await self._intros.pending_between(from_user_id, target.owner_id) is not None:
            raise IntroAlreadyPending
        intro = IntroRequest(
            id=self._id_factory(),
            from_user_id=from_user_id,
            to_user_id=target.owner_id,
            message=message,
            created_at=self._now(),
        )
        await self._intros.add(intro)
        return intro


class ListMyIntros:
    """Return the caller's inbound and outbound intros, enriched with the counterpart."""

    def __init__(self, intros: IntroRepository, profiles: ProfileRepository) -> None:
        self._intros = intros
        self._profiles = profiles

    async def execute(
        self, user_id: UUID
    ) -> tuple[list[IntroView], list[IntroView]]:
        inbound = [
            IntroView(intro=i, counterpart=await self._profiles.get_by_owner(i.from_user_id))
            for i in await self._intros.list_inbound(user_id)
        ]
        outbound = [
            IntroView(intro=i, counterpart=await self._profiles.get_by_owner(i.to_user_id))
            for i in await self._intros.list_outbound(user_id)
        ]
        return inbound, outbound


class RespondToIntro:
    """Accept or decline an inbound intro. Only the target may respond."""

    def __init__(
        self,
        intros: IntroRepository,
        *,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._intros = intros
        self._now = now

    async def execute(
        self, user_id: UUID, intro_id: UUID, *, accept: bool
    ) -> IntroRequest:
        intro = await self._intros.get(intro_id)
        if intro is None:
            raise IntroNotFound
        if intro.to_user_id != user_id:
            raise IntroForbidden
        if accept:
            intro.accept(at=self._now())
        else:
            intro.decline(at=self._now())
        await self._intros.save(intro)
        return intro
