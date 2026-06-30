from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.playlist import PlaylistRepository
from app.services.playlist import PlaylistService


async def get_playlist_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaylistRepository:
    """Provide a PlaylistRepository bound to the current request session."""
    return PlaylistRepository(db)


async def get_playlist_service(
    repository: Annotated[PlaylistRepository, Depends(get_playlist_repository)],
) -> PlaylistService:
    """Provide a PlaylistService with injected repository."""
    return PlaylistService(repository)
