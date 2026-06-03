from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.services.auth_service import AuthService
from app.config import Settings, get_settings
from app.infrastructure.db.models.skill import UserSkill
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.infrastructure.security.jwt import safe_decode

security = HTTPBearer(auto_error=False)

_USER_FULL_LOAD = (
    selectinload(User.photos),
    selectinload(User.profile),
    selectinload(User.skills).selectinload(UserSkill.skill),
)


def _decode_user_id(
    credentials: HTTPAuthorizationCredentials | None,
    settings: Settings,
) -> int:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido.",
        )
    payload = safe_decode(credentials.credentials, settings)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")
    return int(user_id)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """Auth leve — só valida token e carrega linha do user (sem joins)."""
    user_id = _decode_user_id(credentials, settings)
    user = await session.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inativo.")
    return user


async def get_current_user_full(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """Perfil completo em 1 query (fotos, skills, profile)."""
    user_id = _decode_user_id(credentials, settings)
    user = await session.scalar(
        select(User).where(User.id == user_id).options(*_USER_FULL_LOAD)
    )
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inativo.")
    return user


def _gallery_photos_out(user: User) -> list[dict]:
    gallery = sorted(
        (p for p in user.photos if p.kind == "gallery"),
        key=lambda p: p.position,
    )
    return [
        {"id": p.id, "photo_url": p.photo_url, "position": p.position}
        for p in gallery
    ]


def user_to_public(user: User) -> dict:
    skills = [
        {
            "skill_id": us.skill_id,
            "skill_name": us.skill.name if us.skill else "",
            "experience_years": us.experience_years,
        }
        for us in user.skills
    ]
    return {
        "id": user.id,
        "uuid": user.uuid,
        "name": user.name,
        "birth_date": user.birth_date,
        "city": user.city,
        "state": user.state,
        "country": user.country,
        "bio": user.bio,
        "profile_picture": user.profile_picture,
        "photos": _gallery_photos_out(user),
        "profile": user.profile,
        "skills": skills,
    }
