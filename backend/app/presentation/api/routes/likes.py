from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.match_service import MatchService
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.presentation.api.deps import get_current_user
from app.presentation.schemas.user import LikeResponse, PassResponse, RecentLikeOut

router = APIRouter(prefix="/swipes", tags=["swipes"])


@router.get("/likes/recent", response_model=list[RecentLikeOut])
async def recent_likes(
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 20,
):
    rows = await MatchService(session).list_recent_likes(current.id, limit=min(limit, 50))
    out: list[RecentLikeOut] = []
    for like, user in rows:
        if not user.is_active:
            continue
        picture = user.profile_picture
        if not picture and user.photos:
            picture = sorted(user.photos, key=lambda p: p.position)[0].photo_url
        out.append(
            RecentLikeOut(
                user_id=user.id,
                name=user.name,
                current_role=user.profile.current_role if user.profile else None,
                profile_picture=picture,
                liked_at=like.created_at,
            )
        )
    return out


@router.post("/like/{to_user_id}", response_model=LikeResponse)
async def like_user(
    to_user_id: int,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    result = await MatchService(session).like_user(current.id, to_user_id)
    return LikeResponse(**result)


@router.post("/dislike/{to_user_id}", response_model=PassResponse)
async def dislike_user(
    to_user_id: int,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    result = await MatchService(session).dislike_user(current.id, to_user_id)
    return PassResponse(**result)
