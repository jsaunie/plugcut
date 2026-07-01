"""Intro routes: request a warm intro, read your inbox, accept/decline."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.intros.use_cases import (
    IntroView,
    ListMyIntros,
    RequestIntro,
    RespondToIntro,
)
from app.interfaces.api.deps import (
    CurrentUser,
    get_list_intros,
    get_request_intro,
    get_respond_intro,
    get_session,
)

router = APIRouter(tags=["intros"])


class IntroRequestBody(BaseModel):
    message: str = Field(default="", max_length=1000)


class IntroRespondBody(BaseModel):
    accept: bool


class CounterpartSummary(BaseModel):
    handle: str
    display_name: str


class IntroResponse(BaseModel):
    id: UUID
    message: str
    status: str
    created_at: datetime
    responded_at: datetime | None
    counterpart: CounterpartSummary | None

    @classmethod
    def from_view(cls, view: IntroView) -> IntroResponse:
        counterpart = None
        if view.counterpart is not None:
            counterpart = CounterpartSummary(
                handle=view.counterpart.handle,
                display_name=view.counterpart.display_name,
            )
        return cls(
            id=view.intro.id,
            message=view.intro.message,
            status=view.intro.status.value,
            created_at=view.intro.created_at,
            responded_at=view.intro.responded_at,
            counterpart=counterpart,
        )


class IntroInbox(BaseModel):
    inbound: list[IntroResponse]
    outbound: list[IntroResponse]


@router.post(
    "/profiles/{handle}/intro",
    status_code=status.HTTP_201_CREATED,
)
async def request_intro(
    handle: str,
    payload: IntroRequestBody,
    current_user: CurrentUser,
    use_case: Annotated[RequestIntro, Depends(get_request_intro)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    intro = await use_case.execute(current_user.id, handle, payload.message)
    await session.commit()
    return {"id": str(intro.id), "status": intro.status.value}


@router.get("/intros", response_model=IntroInbox)
async def list_intros(
    current_user: CurrentUser,
    use_case: Annotated[ListMyIntros, Depends(get_list_intros)],
) -> IntroInbox:
    inbound, outbound = await use_case.execute(current_user.id)
    return IntroInbox(
        inbound=[IntroResponse.from_view(v) for v in inbound],
        outbound=[IntroResponse.from_view(v) for v in outbound],
    )


@router.post("/intros/{intro_id}/respond", response_model=IntroResponse)
async def respond_intro(
    intro_id: UUID,
    payload: IntroRespondBody,
    current_user: CurrentUser,
    use_case: Annotated[RespondToIntro, Depends(get_respond_intro)],
    list_use_case: Annotated[ListMyIntros, Depends(get_list_intros)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IntroResponse:
    intro = await use_case.execute(current_user.id, intro_id, accept=payload.accept)
    await session.commit()
    # Re-read inbound to attach the counterpart for a consistent response shape.
    inbound, _ = await list_use_case.execute(current_user.id)
    for view in inbound:
        if view.intro.id == intro.id:
            return IntroResponse.from_view(view)
    return IntroResponse.from_view(IntroView(intro=intro, counterpart=None))
