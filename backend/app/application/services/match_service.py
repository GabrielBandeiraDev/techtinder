from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.services.user_service import UserService
from app.domain.exceptions import ChatRequiresMatchError, ConflictError, NotFoundError
from app.infrastructure.db.models.like import Like, Pass
from app.infrastructure.db.models.match import Conversation, Match
from app.infrastructure.db.models.message import Message
from app.infrastructure.db.models.user import User


def _ordered_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


class MatchService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def like_user(self, from_user_id: int, to_user_id: int) -> dict:
        if from_user_id == to_user_id:
            raise ConflictError("Não é possível curtir a si mesmo.")

        target = await self._session.get(User, to_user_id)
        if not target or not target.is_active:
            raise NotFoundError("Usuário não encontrado.")

        existing = await self._session.scalar(
            select(Like).where(
                Like.from_user_id == from_user_id,
                Like.to_user_id == to_user_id,
            )
        )
        if existing:
            return {"liked": True, "matched": False, "match_id": None}

        self._session.add(Like(from_user_id=from_user_id, to_user_id=to_user_id))
        await self._session.flush()

        reciprocal = await self._session.scalar(
            select(Like).where(
                Like.from_user_id == to_user_id,
                Like.to_user_id == from_user_id,
            )
        )
        if not reciprocal:
            await self._session.commit()
            return {"liked": True, "matched": False, "match_id": None}

        u1, u2 = _ordered_pair(from_user_id, to_user_id)
        match = await self._session.scalar(
            select(Match).where(Match.user_one_id == u1, Match.user_two_id == u2)
        )
        if not match:
            match = Match(user_one_id=u1, user_two_id=u2)
            self._session.add(match)
            await self._session.flush()

        conv = await self._session.scalar(
            select(Conversation).where(Conversation.match_id == match.id)
        )
        if not conv:
            self._session.add(Conversation(match_id=match.id))

        await self._session.commit()
        await self._session.refresh(match)
        return {"liked": True, "matched": True, "match_id": match.id}

    async def list_recent_likes(
        self,
        from_user_id: int,
        limit: int = 20,
    ) -> list[tuple[Like, User]]:
        result = await self._session.scalars(
            select(Like)
            .where(Like.from_user_id == from_user_id)
            .order_by(Like.created_at.desc())
            .limit(limit)
        )
        likes = list(result.all())
        if not likes:
            return []

        target_ids = [like.to_user_id for like in likes]
        users_result = await self._session.scalars(
            select(User)
            .where(User.id.in_(target_ids))
            .options(
                selectinload(User.profile),
                selectinload(User.photos),
            )
        )
        users_by_id = {u.id: u for u in users_result.all()}
        return [(like, users_by_id[like.to_user_id]) for like in likes if like.to_user_id in users_by_id]

    async def dislike_user(self, from_user_id: int, to_user_id: int) -> dict:
        if from_user_id == to_user_id:
            raise ConflictError("Ação inválida.")

        existing = await self._session.scalar(
            select(Pass).where(
                Pass.from_user_id == from_user_id,
                Pass.to_user_id == to_user_id,
            )
        )
        if not existing:
            self._session.add(
                Pass(from_user_id=from_user_id, to_user_id=to_user_id)
            )
            await self._session.commit()
        return {"passed": True}

    async def list_matches(self, user_id: int) -> list[Match]:
        result = await self._session.scalars(
            select(Match)
            .where(
                or_(Match.user_one_id == user_id, Match.user_two_id == user_id)
            )
            .options(selectinload(Match.conversation))
            .order_by(Match.matched_at.desc())
        )
        return list(result.all())

    async def list_matches_with_users(
        self, user_id: int
    ) -> list[tuple[Match, User, int | None]]:
        """Uma query de matches + uma batch de usuários (evita N+1)."""
        matches = await self.list_matches(user_id)
        if not matches:
            return []

        other_ids = [
            m.user_two_id if m.user_one_id == user_id else m.user_one_id for m in matches
        ]
        users = await UserService(self._session).get_many_by_ids(other_ids)
        by_id = {u.id: u for u in users}

        out: list[tuple[Match, User, int | None]] = []
        for m in matches:
            oid = m.user_two_id if m.user_one_id == user_id else m.user_one_id
            other = by_id.get(oid)
            if not other:
                continue
            conv_id = m.conversation.id if m.conversation else None
            out.append((m, other, conv_id))
        return out

    async def get_match_for_users(self, user_a: int, user_b: int) -> Match | None:
        u1, u2 = _ordered_pair(user_a, user_b)
        return await self._session.scalar(
            select(Match).where(Match.user_one_id == u1, Match.user_two_id == u2)
        )

    async def ensure_match_access(self, user_id: int, other_user_id: int) -> Match:
        match = await self.get_match_for_users(user_id, other_user_id)
        if not match:
            raise ChatRequiresMatchError()
        return match

    async def get_conversation_by_match(self, match_id: int) -> Conversation:
        conv = await self._session.scalar(
            select(Conversation)
            .where(Conversation.match_id == match_id)
            .options(selectinload(Conversation.messages))
        )
        if not conv:
            raise NotFoundError("Conversa não encontrada.")
        return conv

    async def user_in_match(self, user_id: int, match_id: int) -> Match:
        match = await self._session.get(Match, match_id)
        if not match or user_id not in (match.user_one_id, match.user_two_id):
            raise NotFoundError("Match não encontrado.")
        return match

    async def send_message(
        self,
        sender_id: int,
        conversation_id: int,
        text: str,
    ) -> Message:
        conv = await self._session.scalar(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.match))
        )
        if not conv or not conv.match:
            raise NotFoundError("Conversa não encontrada.")

        match = conv.match
        if sender_id not in (match.user_one_id, match.user_two_id):
            raise ChatRequiresMatchError()

        msg = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            message=text,
        )
        self._session.add(msg)
        await self._session.commit()
        await self._session.refresh(msg)
        return msg

    async def list_messages(
        self,
        user_id: int,
        conversation_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        conv = await self._session.scalar(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.match))
        )
        if not conv or not conv.match:
            raise NotFoundError("Conversa não encontrada.")
        if user_id not in (conv.match.user_one_id, conv.match.user_two_id):
            raise ChatRequiresMatchError()

        result = await self._session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.all())
