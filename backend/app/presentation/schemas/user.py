from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class SkillOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserSkillOut(BaseModel):
    skill_id: int
    skill_name: str
    experience_years: int | None

    model_config = {"from_attributes": True}


class UserPhotoOut(BaseModel):
    id: int
    photo_url: str
    position: int

    model_config = {"from_attributes": True}


class UserProfileOut(BaseModel):
    current_role: str | None = None
    company: str | None = None
    years_experience: int | None = None
    works_with_ai: bool = False
    works_with_backend: bool = False
    works_with_frontend: bool = False
    works_with_mobile: bool = False
    works_with_data_science: bool = False
    works_with_devops: bool = False
    works_with_cloud: bool = False
    works_with_cybersecurity: bool = False
    future_goals: str | None = None
    favorite_technologies: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    remote_only: bool = False
    open_to_partnerships: bool = False
    open_to_startups: bool = False

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    current_role: str | None = None
    company: str | None = None
    years_experience: int | None = Field(None, ge=0, le=60)
    works_with_ai: bool | None = None
    works_with_backend: bool | None = None
    works_with_frontend: bool | None = None
    works_with_mobile: bool | None = None
    works_with_data_science: bool | None = None
    works_with_devops: bool | None = None
    works_with_cloud: bool | None = None
    works_with_cybersecurity: bool | None = None
    future_goals: str | None = None
    favorite_technologies: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    remote_only: bool | None = None
    open_to_partnerships: bool | None = None
    open_to_startups: bool | None = None


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    birth_date: date | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    bio: str | None = Field(None, max_length=2000)


class UserMeUpdate(BaseModel):
    """Campos editáveis pelo usuário autenticado (sem nome)."""

    birth_date: date | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    bio: str | None = Field(None, max_length=2000)


class UserOut(BaseModel):
    id: int
    uuid: str
    name: str
    email: EmailStr
    birth_date: date | None
    city: str | None
    state: str | None
    country: str | None
    bio: str | None
    profile_picture: str | None
    photos: list[UserPhotoOut] = []
    profile: UserProfileOut | None = None
    skills: list[UserSkillOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublicOut(BaseModel):
    id: int
    uuid: str
    name: str
    birth_date: date | None
    city: str | None
    state: str | None
    country: str | None
    bio: str | None
    profile_picture: str | None
    photos: list[UserPhotoOut] = []
    profile: UserProfileOut | None = None
    skills: list[UserSkillOut] = []

    model_config = {"from_attributes": True}


class UserSkillSet(BaseModel):
    skill_id: int
    experience_years: int | None = Field(None, ge=0, le=50)


class RecentLikeOut(BaseModel):
    """Resumo mínimo — sem link para reabrir perfil no feed."""

    user_id: int
    name: str
    current_role: str | None = None
    profile_picture: str | None = None
    liked_at: datetime


class LikeResponse(BaseModel):
    liked: bool
    matched: bool
    match_id: int | None = None


class PassResponse(BaseModel):
    passed: bool


class MatchOut(BaseModel):
    id: int
    user_one_id: int
    user_two_id: int
    matched_at: datetime
    conversation_id: int | None = None
    other_user: UserPublicOut | None = None


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    message: str
    created_at: datetime
    read_at: datetime | None

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
