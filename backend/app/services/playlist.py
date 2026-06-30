from uuid import UUID

from app.exceptions.base import ConflictException, ForbiddenException, NotFoundException
from app.models.enums import PlaylistStatus
from app.models.playlist import Playlist
from app.repositories.playlist import PlaylistRepository
from app.schemas.playlist import (
    PlaylistCreateSchema,
    PlaylistListResponseSchema,
    PlaylistResponseSchema,
    PlaylistUpdateSchema,
)


class PlaylistService:
    """Business logic for playlist management.

    Enforces ownership, validation, and DTO mapping. Never accesses the
    database directly — uses `PlaylistRepository` for persistence.
    """

    def __init__(self, repository: PlaylistRepository) -> None:
        self.repository = repository

    def _to_response(self, playlist: Playlist) -> PlaylistResponseSchema:
        return PlaylistResponseSchema.model_validate(playlist)

    async def create_playlist(self, user_id: UUID, data: PlaylistCreateSchema) -> PlaylistResponseSchema:
        title = data.title.strip() if data.title else ""
        if not title:
            raise ConflictException(
                message="Title is required",
                errors=[{"field": "title", "message": "Title must not be empty"}],
            )

        playlist = Playlist(
            user_id=user_id,
            title=title,
            description=(data.description.strip() if data.description else None),
            source_type=data.source_type,
            source_url=(data.source_url.strip() if data.source_url else None),
            thumbnail_url=(data.thumbnail_url.strip() if data.thumbnail_url else None),
            target_completion_date=data.target_completion_date,
            status=PlaylistStatus.ACTIVE,
        )

        created = await self.repository.create(playlist)
        return self._to_response(created)

    async def get_playlist(self, user_id: UUID, playlist_id: UUID) -> PlaylistResponseSchema:
        playlist = await self.repository.get_by_id(playlist_id)
        if playlist is None:
            raise NotFoundException(message="Playlist not found")
        if playlist.user_id != user_id:
            raise ForbiddenException(message="Access denied to this playlist")
        return self._to_response(playlist)

    async def list_playlists(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> PlaylistListResponseSchema:
        items = await self.repository.list_user_playlists(user_id=user_id, skip=skip, limit=limit)
        total = await self.repository.count_user_playlists(user_id=user_id)
        return PlaylistListResponseSchema(
            items=[self._to_response(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def update_playlist(
        self,
        user_id: UUID,
        playlist_id: UUID,
        data: PlaylistUpdateSchema,
    ) -> PlaylistResponseSchema:
        playlist = await self.repository.get_by_id(playlist_id)
        if playlist is None:
            raise NotFoundException(message="Playlist not found")
        if playlist.user_id != user_id:
            raise ForbiddenException(message="Access denied to this playlist")

        update_data = data.model_dump(exclude_unset=True)
        if "title" in update_data and update_data.get("title") is not None:
            update_data["title"] = update_data["title"].strip()
            if not update_data["title"]:
                raise ConflictException(
                    message="Title is required",
                    errors=[{"field": "title", "message": "Title must not be empty"}],
                )

        updated = await self.repository.update(playlist, **update_data)
        return self._to_response(updated)

    async def archive_playlist(self, user_id: UUID, playlist_id: UUID) -> PlaylistResponseSchema:
        playlist = await self.repository.get_by_id(playlist_id)
        if playlist is None:
            raise NotFoundException(message="Playlist not found")
        if playlist.user_id != user_id:
            raise ForbiddenException(message="Access denied to this playlist")

        updated = await self.repository.update(playlist, status=PlaylistStatus.ARCHIVED)
        return self._to_response(updated)

    async def delete_playlist(self, user_id: UUID, playlist_id: UUID) -> PlaylistResponseSchema:
        playlist = await self.repository.get_by_id(playlist_id)
        if playlist is None:
            raise NotFoundException(message="Playlist not found")
        if playlist.user_id != user_id:
            raise ForbiddenException(message="Access denied to this playlist")
        if playlist.is_deleted:
            raise ConflictException(message="Playlist already deleted")

        deleted = await self.repository.soft_delete(playlist)
        return self._to_response(deleted)
