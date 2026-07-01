from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenPayload, decode_access_token
from app.database.session import get_db
from app.exceptions.base import UnauthorizedException
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    auto_error=False,
)


async def get_current_user_token(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> TokenPayload:
    """Decode and validate the JWT token from the Authorization header."""
    if token is None:
        raise UnauthorizedException(message="Not authenticated")

    try:
        return decode_access_token(token)
    except ValueError as exc:
        raise UnauthorizedException(message="Invalid or expired token") from exc


async def get_current_user(
    token_payload: Annotated[TokenPayload, Depends(get_current_user_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Return the current authenticated user from the database."""
    try:
        user_id = UUID(token_payload.sub)
    except ValueError as exc:
        raise UnauthorizedException(message="Invalid token subject") from exc

    repository = UserRepository(db)
    user = await repository.get_by_id(user_id)
    if user is None:
        raise UnauthorizedException(message="User not found")
    return user


async def get_auth_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    """Provide a UserRepository bound to the current request session."""
    return UserRepository(db)


async def get_auth_service(
    repository: Annotated[UserRepository, Depends(get_auth_repository)],
) -> AuthService:
    """Provide an AuthService with injected repository."""
    return AuthService(repository)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Return the current active (non-deleted) user."""
    if not current_user.is_active:
        raise UnauthorizedException(message="User account is inactive")
    return current_user
