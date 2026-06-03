import time
from typing import TypeVar

T = TypeVar("T")

_skills_cache: tuple[float, list] | None = None
_SKILLS_TTL_SEC = 300


def get_skills_cache() -> list | None:
    global _skills_cache
    if _skills_cache is None:
        return None
    ts, data = _skills_cache
    if time.monotonic() - ts > _SKILLS_TTL_SEC:
        _skills_cache = None
        return None
    return data


def set_skills_cache(skills: list) -> None:
    global _skills_cache
    _skills_cache = (time.monotonic(), skills)
