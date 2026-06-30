from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.playlist import Playlist
from app.repositories.base import BaseRepository


class PlaylistRepository(BaseRepository[Playlist]):
    """Repository for Playlist persistence operations.

    Only communicates with the database — no business logic.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Playlist)

    async def create(self, playlist: Playlist) -> Playlist:
        """Persist a new playlist entity."""
        return await super().create(playlist)

    async def update(self, playlist: Playlist, **kwargs) -> Playlist:
        """Update playlist fields."""
        return await super().update(playlist, **kwargs)

    async def delete(self, playlist: Playlist) -> None:
        """Permanently remove a playlist."""
        await super().hard_delete(playlist)

    async def get_by_id(self, playlist_id: UUID) -> Playlist | None:
        """Retrieve a playlist by ID (excluding soft-deleted)."""
        return await super().get_by_id(playlist_id)

    async def list_user_playlists(self, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Playlist]:
        """Return paginated list of a user's non-deleted playlists."""
        stmt = self._not_deleted_filter(
            select(Playlist).where(Playlist.user_id == user_id).offset(skip).limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_user_playlists(self, user_id: UUID) -> int:
        """Count non-deleted playlists for a given user."""
        stmt = select(func.count()).select_from(Playlist).where(Playlist.user_id == user_id)
        stmt = self._not_deleted_filter(stmt)
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def exists(self, playlist_id: UUID, user_id: UUID | None = None) -> bool:
        """Check whether a non-deleted playlist exists. Optionally filter by owner."""
        stmt = select(func.count()).select_from(Playlist).where(Playlist.id == playlist_id)
        if user_id is not None:
            stmt = stmt.where(Playlist.user_id == user_id)
        stmt = self._not_deleted_filter(stmt)
        result = await self.session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def soft_delete(self, playlist: Playlist) -> Playlist:
        """Soft delete a playlist by setting `deleted_at`."""
        return await super().soft_delete(playlist)
