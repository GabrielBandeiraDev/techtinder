from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.user_service import UserService
from app.config import Settings, get_settings
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import get_db
from app.infrastructure.storage.file_upload import delete_upload_file, validate_and_save_image
from app.presentation.api.deps import get_current_user, get_current_user_full, user_to_public
from app.presentation.schemas.user import (
    UserMeUpdate,
    UserOut,
    UserProfileUpdate,
    UserPublicOut,
    UserSkillSet,
)

router = APIRouter(prefix="/users", tags=["users"])


def _full_user(user: User) -> UserOut:
    data = user_to_public(user)
    data["email"] = user.email
    data["created_at"] = user.created_at
    return UserOut.model_validate(data)


@router.get("/me", response_model=UserOut)
async def get_me(current: Annotated[User, Depends(get_current_user_full)]):
    return _full_user(current)


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserMeUpdate,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = UserService(session)
    user = await service.update_user(
        current.id,
        **body.model_dump(exclude_unset=True),
    )
    user = await service.get_by_id(user.id)
    return _full_user(user)


@router.put("/me/profile", response_model=UserOut)
async def upsert_profile(
    body: UserProfileUpdate,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = UserService(session)
    await service.upsert_profile(
        current.id,
        body.model_dump(exclude_unset=True),
    )
    user = await service.get_by_id(current.id)
    return _full_user(user)


@router.put("/me/skills", response_model=UserOut)
async def set_skills(
    skills: list[UserSkillSet],
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = UserService(session)
    await service.set_skills(
        current.id,
        [(s.skill_id, s.experience_years) for s in skills],
    )
    user = await service.get_by_id(current.id)
    return _full_user(user)


@router.post("/me/photos", status_code=201)
async def upload_photo(
    file: UploadFile,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    url = await validate_and_save_image(file, settings)
    photo = await UserService(session).add_photo(current.id, url)
    return {"id": photo.id, "photo_url": photo.photo_url, "position": photo.position}


@router.delete("/me/photos/{photo_id}", response_model=UserOut)
async def delete_photo(
    photo_id: int,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    service = UserService(session)
    user, deleted_url = await service.delete_photo(current.id, photo_id)
    delete_upload_file(deleted_url, settings)
    return _full_user(user)


@router.post("/me/photos/{photo_id}/primary", response_model=UserOut)
async def set_primary_photo(
    photo_id: int,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    service = UserService(session)
    user = await service.set_primary_photo(current.id, photo_id)
    return _full_user(user)


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile,
    current: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    url = await validate_and_save_image(file, settings, subdirectory="avatars")
    service = UserService(session)
    await service.update_user(current.id, profile_picture=url)
    user = await service.get_by_id(current.id)
    return _full_user(user)


@router.get("/{user_uuid}", response_model=UserPublicOut)
async def get_user(
    user_uuid: str,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    user = await UserService(session).get_by_uuid(user_uuid)
    return UserPublicOut.model_validate(user_to_public(user))
