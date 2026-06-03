from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.feed_service import FeedService
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.presentation.api.deps import get_current_user, user_to_public
from app.presentation.schemas.user import UserPublicOut

router = APIRouter(tags=["feed"])


@router.get("/feed", response_model=list[UserPublicOut])
async def get_feed(
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    users = await FeedService(session).get_recommendations(current.id, limit, offset)
    return [UserPublicOut.model_validate(user_to_public(u)) for u in users]


@router.get("/search", response_model=list[UserPublicOut])
async def search(
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = None,
    city: str | None = None,
    skill: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    users = await FeedService(session).search_profiles(
        current.id, q=q, city=city, skill_name=skill, limit=limit, offset=offset
    )
    return [UserPublicOut.model_validate(user_to_public(u)) for u in users]


@router.get("/stats/registered-count")
async def registered_count(session: Annotated[AsyncSession, Depends(get_db)]):
    count = await FeedService(session).registered_count()
    return {"count": count}
