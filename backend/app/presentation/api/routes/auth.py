from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.auth_service import AuthService
from app.config import Settings, get_settings
from app.infrastructure.db.session import get_db
from app.presentation.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.presentation.schemas.user import UserOut
from app.presentation.api.deps import user_to_public

router = APIRouter(prefix="/auth", tags=["auth"])


def _serialize_user(user) -> UserOut:
    data = user_to_public(user)
    data["email"] = user.email
    data["created_at"] = user.created_at
    return UserOut.model_validate(data)


@router.post("/register", response_model=UserOut, status_code=201)
async def register(
    body: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    service = AuthService(session, settings)
    user = await service.register(body.name, body.email, body.password)
    from app.application.services.user_service import UserService

    user = await UserService(session).get_by_id(user.id)
    return _serialize_user(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    service = AuthService(session, settings)
    user = await service.authenticate(body.email, body.password)
    tokens = await service.issue_tokens(user)
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    service = AuthService(session, settings)
    tokens = await service.refresh_access_token(body.refresh_token)
    return TokenResponse(**tokens)


@router.post("/logout", status_code=204)
async def logout(
    body: LogoutRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    service = AuthService(session, settings)
    await service.logout(body.refresh_token)
