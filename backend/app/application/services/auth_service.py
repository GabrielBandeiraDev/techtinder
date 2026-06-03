from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.domain.exceptions import ConflictError, UnauthorizedError
from app.infrastructure.db.models.refresh_token import RefreshToken
from app.infrastructure.db.models.user import User
from app.infrastructure.security.jwt import (
    create_access_token,
    create_refresh_token,
    safe_decode,
)
from app.infrastructure.security.password import hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings

    async def register(
        self,
        name: str,
        email: str,
        password: str,
    ) -> User:
        existing = await self._session.scalar(
            select(User).where(User.email == email.lower())
        )
        if existing:
            raise ConflictError("E-mail já cadastrado.")

        user = User(
            name=name,
            email=email.lower(),
            password_hash=hash_password(password),
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self._session.scalar(
            select(User).where(User.email == email.lower(), User.is_active.is_(True))
        )
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("E-mail ou senha inválidos.")
        return user

    async def issue_tokens(self, user: User) -> dict[str, str]:
        access = create_access_token(str(user.id), self._settings)
        refresh, jti, expires = create_refresh_token(str(user.id), self._settings)
        self._session.add(
            RefreshToken(user_id=user.id, token_jti=jti, expires_at=expires)
        )
        await self._session.commit()
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        payload = safe_decode(refresh_token, self._settings)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Refresh token inválido.")

        jti = payload.get("jti")
        user_id = payload.get("sub")
        if not jti or not user_id:
            raise UnauthorizedError("Refresh token inválido.")

        stored = await self._session.scalar(
            select(RefreshToken).where(
                RefreshToken.token_jti == jti,
                RefreshToken.revoked_at.is_(None),
            )
        )
        if not stored or stored.expires_at < datetime.now(UTC):
            raise UnauthorizedError("Refresh token expirado ou revogado.")

        user = await self._session.get(User, int(user_id))
        if not user or not user.is_active:
            raise UnauthorizedError("Usuário inválido.")

        access = create_access_token(str(user.id), self._settings)
        return {
            "access_token": access,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def logout(self, refresh_token: str) -> None:
        payload = safe_decode(refresh_token, self._settings)
        if not payload:
            return
        jti = payload.get("jti")
        if not jti:
            return
        stored = await self._session.scalar(
            select(RefreshToken).where(RefreshToken.token_jti == jti)
        )
        if stored and stored.revoked_at is None:
            stored.revoked_at = datetime.now(UTC)
            await self._session.commit()
