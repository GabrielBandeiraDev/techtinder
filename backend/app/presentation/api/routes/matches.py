from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.match_service import MatchService
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.presentation.api.deps import get_current_user, user_to_public
from app.presentation.schemas.user import MatchOut, UserPublicOut

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchOut])
async def list_matches(
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    rows = await MatchService(session).list_matches_with_users(current.id)
    return [
        MatchOut(
            id=m.id,
            user_one_id=m.user_one_id,
            user_two_id=m.user_two_id,
            matched_at=m.matched_at,
            conversation_id=conv_id,
            other_user=UserPublicOut.model_validate(user_to_public(other)),
        )
        for m, other, conv_id in rows
    ]
