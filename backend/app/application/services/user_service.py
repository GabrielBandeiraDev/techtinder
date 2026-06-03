from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.exceptions import NotFoundError, ValidationError
from app.infrastructure.db.models.skill import Skill, UserSkill
from app.infrastructure.db.models.user import User, UserPhoto, UserProfile


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User:
        user = await self._session.scalar(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.photos),
                selectinload(User.profile),
                selectinload(User.skills).selectinload(UserSkill.skill),
            )
        )
        if not user:
            raise NotFoundError("Usuário não encontrado.")
        return user

    async def get_many_by_ids(self, user_ids: list[int]) -> list[User]:
        if not user_ids:
            return []
        result = await self._session.scalars(
            select(User)
            .where(User.id.in_(user_ids))
            .options(
                selectinload(User.photos),
                selectinload(User.profile),
                selectinload(User.skills).selectinload(UserSkill.skill),
            )
        )
        return list(result.all())

    async def get_by_uuid(self, user_uuid: str) -> User:
        user = await self._session.scalar(
            select(User)
            .where(User.uuid == user_uuid)
            .options(
                selectinload(User.photos),
                selectinload(User.profile),
                selectinload(User.skills).selectinload(UserSkill.skill),
            )
        )
        if not user:
            raise NotFoundError("Usuário não encontrado.")
        return user

    async def update_user(
        self,
        user_id: int,
        **fields,
    ) -> User:
        user = await self.get_by_id(user_id)
        for key, value in fields.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def upsert_profile(self, user_id: int, data: dict) -> UserProfile:
        user = await self.get_by_id(user_id)
        if user.profile:
            for key, value in data.items():
                if hasattr(user.profile, key):
                    setattr(user.profile, key, value)
            profile = user.profile
        else:
            profile = UserProfile(user_id=user_id, **data)
            self._session.add(profile)
        await self._session.commit()
        await self._session.refresh(profile)
        return profile

    async def add_photo(
        self,
        user_id: int,
        photo_url: str,
        position: int | None = None,
    ) -> UserPhoto:
        count = await self._session.scalar(
            select(func.count())
            .select_from(UserPhoto)
            .where(UserPhoto.user_id == user_id)
        )
        if count and count >= 10:
            raise ValidationError("Máximo de 10 fotos por perfil.")

        if position is None:
            position = count or 0

        photo = UserPhoto(user_id=user_id, photo_url=photo_url, position=position)
        self._session.add(photo)
        await self._session.commit()
        await self._session.refresh(photo)
        return photo

    async def delete_photo(self, user_id: int, photo_id: int) -> tuple[User, str | None]:
        user = await self.get_by_id(user_id)
        photo = next((p for p in user.photos if p.id == photo_id), None)
        if not photo:
            raise NotFoundError("Foto não encontrada.")

        deleted_url = photo.photo_url
        await self._session.delete(photo)

        if user.profile_picture == deleted_url:
            remaining = sorted(
                (p for p in user.photos if p.id != photo_id),
                key=lambda p: p.position,
            )
            user.profile_picture = remaining[0].photo_url if remaining else None

        await self._session.commit()
        user = await self.get_by_id(user_id)
        return user, deleted_url

    async def set_primary_photo(self, user_id: int, photo_id: int) -> User:
        user = await self.get_by_id(user_id)
        photo = next((p for p in user.photos if p.id == photo_id), None)
        if not photo:
            raise NotFoundError("Foto não encontrada.")
        user.profile_picture = photo.photo_url
        await self._session.commit()
        return await self.get_by_id(user_id)

    async def set_skills(
        self,
        user_id: int,
        skills: list[tuple[int, int | None]],
    ) -> None:
        await self._session.execute(
            UserSkill.__table__.delete().where(UserSkill.user_id == user_id)
        )
        for skill_id, years in skills:
            self._session.add(
                UserSkill(
                    user_id=user_id,
                    skill_id=skill_id,
                    experience_years=years,
                )
            )
        await self._session.commit()

    async def list_skills(self) -> list[Skill]:
        result = await self._session.scalars(select(Skill).order_by(Skill.name))
        return list(result.all())
