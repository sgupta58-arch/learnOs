from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.user import UserRepository
from app.services.user import UserService


async def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    """Provide a UserRepository bound to the current request session."""
    return UserRepository(db)


async def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Provide a UserService with injected repository."""
    return UserService(repository)
