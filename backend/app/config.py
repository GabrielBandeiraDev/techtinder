from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "TechMatchmakers API"
    debug: bool = False

    # SQLite local (legado) — deixe vazio se usar Supabase
    database_url: str = ""

    # Supabase — preencha no .env (Settings → API + Database password)
    supabase_project_id: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_db_password: str = ""
    # Host opcional (padrão: db.{project_id}.supabase.co)
    supabase_db_host: str = ""
    # Transaction pooler (porta 6543) — mais rápido no Supabase com FastAPI
    supabase_use_pooler: bool = False
    supabase_pooler_host: str = ""

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_recycle: int = 300

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: str = (
        "http://localhost:8080,http://localhost:5173,http://localhost:3000,"
        "http://127.0.0.1:8080"
    )
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 5
    rate_limit_default: str = "100/minute"
    algorithm: str = "HS256"

    @property
    def is_postgres(self) -> bool:
        url = self.resolved_database_url
        return url.startswith("postgresql")

    @property
    def resolved_database_url(self) -> str:
        """URL async para SQLAlchemy (Supabase/Postgres ou SQLite local)."""
        explicit = (self.database_url or "").strip()
        if explicit:
            return explicit

        project_id = self.supabase_project_id.strip()
        db_password = self.supabase_db_password
        if project_id and db_password:
            password = quote_plus(db_password)
            if self.supabase_use_pooler and self.supabase_pooler_host.strip():
                host = self.supabase_pooler_host.strip()
                user = f"postgres.{project_id}"
                return (
                    f"postgresql+asyncpg://{user}:{password}@{host}:6543/postgres"
                    f"?ssl=require"
                )
            host = (self.supabase_db_host or f"db.{project_id}.supabase.co").strip()
            return (
                f"postgresql+asyncpg://postgres:{password}@{host}:5432/postgres"
                f"?ssl=require"
            )

        return "sqlite+aiosqlite:///./data/app.db"

    @property
    def uses_supabase_db(self) -> bool:
        return self.is_postgres

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def allowed_image_extensions(self) -> frozenset[str]:
        return frozenset({".jpg", ".jpeg", ".png", ".webp"})

    @property
    def allowed_image_mimes(self) -> frozenset[str]:
        return frozenset(
            {"image/jpeg", "image/png", "image/webp"}
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
