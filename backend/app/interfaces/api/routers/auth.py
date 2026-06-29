"""Authentication routes — register, login, and the current-user endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.identity.dtos import AuthenticateUserCommand, RegisterUserCommand
from app.application.identity.use_cases import AuthenticateUser, RegisterUser
from app.interfaces.api.deps import (
    CurrentUser,
    get_authenticate_user,
    get_register_user,
    get_session,
)
from app.interfaces.api.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    use_case: Annotated[RegisterUser, Depends(get_register_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    user = await use_case.execute(RegisterUserCommand(payload.email, payload.password))
    await session.commit()
    return UserResponse.from_domain(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    use_case: Annotated[AuthenticateUser, Depends(get_authenticate_user)],
) -> TokenResponse:
    tokens = await use_case.execute(AuthenticateUserCommand(payload.email, payload.password))
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.from_domain(current_user)
