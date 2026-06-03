from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.match_service import MatchService
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.presentation.api.deps import get_current_user
from app.presentation.schemas.user import MessageCreate, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conversation_id: int,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    messages = await MatchService(session).list_messages(
        current.id, conversation_id, limit, offset
    )
    return [MessageOut.model_validate(m) for m in messages]


@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
    conversation_id: int,
    body: MessageCreate,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    msg = await MatchService(session).send_message(
        current.id, conversation_id, body.message
    )
    return MessageOut.model_validate(msg)
