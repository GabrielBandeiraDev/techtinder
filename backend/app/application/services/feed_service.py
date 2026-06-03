from sqlalchemy import exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models.like import Like, Pass
from app.infrastructure.db.models.skill import Skill, UserSkill
from app.infrastructure.db.models.user import User

_USER_LOAD = (
    selectinload(User.photos),
    selectinload(User.profile),
    selectinload(User.skills).selectinload(UserSkill.skill),
)


class FeedService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _exclude_swiped(self, current_user_id: int):
        liked = exists(
            select(1).where(
                Like.from_user_id == current_user_id,
                Like.to_user_id == User.id,
            )
        )
        passed = exists(
            select(1).where(
                Pass.from_user_id == current_user_id,
                Pass.to_user_id == User.id,
            )
        )
        return liked, passed

    def _base_query(self, current_user_id: int):
        liked, passed = self._exclude_swiped(current_user_id)
        return (
            select(User)
            .where(
                User.id != current_user_id,
                User.is_active.is_(True),
                ~liked,
                ~passed,
            )
            .options(*_USER_LOAD)
        )

    async def get_recommendations(
        self,
        current_user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[User]:
        stmt = (
            self._base_query(current_user_id)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.scalars(stmt)
        return list(result.all())

    async def search_profiles(
        self,
        current_user_id: int,
        q: str | None = None,
        city: str | None = None,
        skill_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[User]:
        stmt = self._base_query(current_user_id)

        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    User.name.ilike(pattern),
                    User.bio.ilike(pattern),
                )
            )
        if city:
            stmt = stmt.where(
                or_(
                    User.city.ilike(f"%{city}%"),
                    User.state.ilike(f"%{city}%"),
                )
            )
        if skill_name:
            stmt = (
                stmt.join(User.skills)
                .join(Skill)
                .where(Skill.name.ilike(f"%{skill_name}%"))
            )

        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.unique().all())

    async def registered_count(self) -> int:
        return await self._session.scalar(
            select(func.count()).select_from(User).where(User.is_active.is_(True))
        ) or 0
