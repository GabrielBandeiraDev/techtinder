from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.user_service import UserService
from app.infrastructure.cache import get_skills_cache, set_skills_cache
from app.infrastructure.db.session import get_db
from app.presentation.schemas.user import SkillOut

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillOut])
async def list_skills(session: Annotated[AsyncSession, Depends(get_db)]):
    cached = get_skills_cache()
    if cached is not None:
        return cached
    skills = await UserService(session).list_skills()
    out = [SkillOut.model_validate(s) for s in skills]
    set_skills_cache(out)
    return out
