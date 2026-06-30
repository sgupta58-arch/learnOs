"""Video service for business logic and orchestration."""

from uuid import UUID

from app.repositories.video import VideoRepository
from app.schemas.video import VideoCreateSchema, VideoUpdateSchema
from app.models.video import Video


class VideoService:
    """Service layer for video operations."""

    def __init__(self, repository: VideoRepository) -> None:
        self.repository = repository

    async def create(self, playlist_id: UUID, payload: VideoCreateSchema) -> Video:
        video = Video(
            playlist_id=playlist_id,
            youtube_video_id=payload.youtube_video_id,
            title=payload.title,
            description=payload.description,
            thumbnail_url=payload.thumbnail_url,
            channel_name=payload.channel_name,
            duration_seconds=payload.duration_seconds,
            position=payload.position,
            published_at=payload.published_at,
        )
        return await self.repository.create(video)

    async def update(self, video: Video, payload: VideoUpdateSchema) -> Video:
        update_data = payload.model_dump(exclude_unset=True)
        return await self.repository.update(video, **update_data)

    async def list_by_playlist(self, playlist_id: UUID) -> list[Video]:
        return list(await self.repository.list_by_playlist(playlist_id))
