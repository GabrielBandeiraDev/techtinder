from fastapi import APIRouter

from app.presentation.api.routes import (
    auth,
    conversations,
    feed,
    likes,
    matches,
    skills,
    users,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(likes.router)
api_router.include_router(matches.router)
api_router.include_router(feed.router)
api_router.include_router(skills.router)
api_router.include_router(conversations.router)
