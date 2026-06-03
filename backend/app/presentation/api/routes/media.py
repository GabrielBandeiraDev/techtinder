from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.domain.exceptions import NotFoundError
from app.infrastructure.db.models.user import UserPhoto
from app.infrastructure.db.session import get_db

router = APIRouter(prefix="/media", tags=["media"])


@router.get("/photos/{photo_id}")
async def get_photo(
    photo_id: int,
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    photo = await session.get(UserPhoto, photo_id)
    if not photo:
        raise NotFoundError("Foto não encontrada.")

    if photo.content:
        return Response(
            content=bytes(photo.content),
            media_type=photo.content_type or "image/jpeg",
            headers={"Cache-Control": "public, max-age=31536000, immutable"},
        )

    if photo.photo_url.startswith("/uploads/"):
        relative = photo.photo_url.removeprefix("/uploads/")
        path = Path(settings.upload_dir) / relative
        if path.is_file():
            data = path.read_bytes()
            suffix = path.suffix.lower()
            mime = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
            }.get(suffix, "application/octet-stream")
            return Response(
                content=data,
                media_type=mime,
                headers={"Cache-Control": "public, max-age=86400"},
            )

    raise NotFoundError("Conteúdo da foto não disponível.")
