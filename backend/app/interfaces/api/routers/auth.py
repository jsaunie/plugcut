"""Authentication routes — register, login, and the current-user endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.identity.dtos import AuthenticateUserCommand, RegisterUserCommand
from app.application.identity.use_cases import (
    AuthenticateUser,
    ChangeEmail,
    ChangePassword,
    DeleteAccount,
    RefreshAccessToken,
    RegisterUser,
)
from app.interfaces.api.deps import (
    CurrentUser,
    get_authenticate_user,
    get_change_email,
    get_change_password,
    get_delete_account,
    get_refresh_access_token,
    get_register_user,
    get_session,
)
from app.interfaces.api.schemas import (
    ChangeEmailRequest,
    ChangePasswordRequest,
    DeleteAccountRequest,
    LoginRequest,
    RefreshRequest,
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    use_case: Annotated[RefreshAccessToken, Depends(get_refresh_access_token)],
) -> TokenResponse:
    tokens = await use_case.execute(payload.refresh_token)
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.from_domain(current_user)


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUser,
    use_case: Annotated[ChangePassword, Depends(get_change_password)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    await use_case.execute(
        current_user.id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    await session.commit()


@router.put("/me/email", response_model=UserResponse)
async def change_email(
    payload: ChangeEmailRequest,
    current_user: CurrentUser,
    use_case: Annotated[ChangeEmail, Depends(get_change_email)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    user = await use_case.execute(
        current_user.id,
        new_email=payload.new_email,
        current_password=payload.current_password,
    )
    await session.commit()
    return UserResponse.from_domain(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    payload: DeleteAccountRequest,
    current_user: CurrentUser,
    use_case: Annotated[DeleteAccount, Depends(get_delete_account)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    await use_case.execute(current_user.id, current_password=payload.current_password)
    await session.commit()
