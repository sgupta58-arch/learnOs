"""Repository layer for video progress persistence.

Why this repository exists: To provide database access for VideoProgress
entities, implementing CRUD operations and progress-specific queries.
This layer isolates database operations from business logic, following
the Clean Architecture principle.

Why it belongs to the repositories layer: This is the data access layer
that handles persistence of VideoProgress records, communicating directly
with the database through SQLAlchemy.

How future Learning Sessions will use it: Will query progress records
to determine where a user left off and resume playback from that position.

How future Analytics will use it: Will query aggregated progress data
to compute learning insights and generate reports.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video import Video
from app.models.video_progress import VideoProgress
from app.models.enums import VideoProgressStatus
from app.repositories.base import BaseRepository


class VideoProgressRepository(BaseRepository[VideoProgress]):
    """Persistence operations for VideoProgress records.

    Why this class exists: To provide video progress-specific database
    operations beyond the generic CRUD, including lookup by user/video,
    playlist-level progress queries, and aggregation queries.

    Why it belongs to the repositories layer: This is the data access layer
    that handles video progress persistence, implementing repository-specific
    methods for progress operations.

    How future Learning Sessions will use it: Will query progress records
    to determine where a user left off and resume playback.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, VideoProgress)

    async def get_by_user_and_video(
        self,
        user_id: UUID,
        video_id: UUID,
    ) -> VideoProgress | None:
        """Get a single progress record by user and video.

        Why this method exists: The unique constraint is (user_id, video_id),
        so this is the natural lookup key. Used by the service to check if
        a progress record already exists before creating or updating.

        How future Learning Sessions will use it: Will fetch the user's
        current progress to resume playback from the last position.
        """
        stmt = self._not_deleted_filter(
            select(VideoProgress).where(
                and_(
                    VideoProgress.user_id == user_id,
                    VideoProgress.video_id == video_id,
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_playlist(
        self,
        user_id: UUID,
        playlist_id: UUID,
    ) -> Sequence[VideoProgress]:
        """Get all progress records for a user's playlist.

        Why this method exists: Provides a complete view of the user's
        progress across all videos in a playlist. Used by the service
        to compute playlist-level progress summaries.

        How future Analytics will use it: Will aggregate progress data
        across playlists to compute learning insights.
        """
        stmt = (
            self._not_deleted_filter(
                select(VideoProgress)
                .join(Video, VideoProgress.video_id == Video.id)
                .where(
                    and_(
                        VideoProgress.user_id == user_id,
                        Video.playlist_id == playlist_id,
                        Video.deleted_at.is_(None),
                    ),
                ),
            )
            .order_by(Video.position.asc().nulls_last(), Video.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_user(self, user_id: UUID) -> Sequence[VideoProgress]:
        """Get all progress records for a user.

        Why this method exists: Provides a complete view of a user's
        progress across all videos. Used for user-level progress summaries.

        How future Analytics will use it: Will aggregate progress data
        across all user content to compute overall learning metrics.
        """
        stmt = self._not_deleted_filter(
            select(VideoProgress).where(VideoProgress.user_id == user_id),
        ).order_by(VideoProgress.updated_at.desc().nulls_last())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_completed(self, user_id: UUID, playlist_id: UUID) -> int:
        """Count completed videos in a playlist for a user.

        Why this method exists: Provides a quick count of completed videos
        without loading all records. Used by the service to compute
        playlist completion summaries.
        """
        stmt = (
            select(func.count())
            .select_from(VideoProgress)
            .join(Video, VideoProgress.video_id == Video.id)
            .where(
                and_(
                    VideoProgress.user_id == user_id,
                    Video.playlist_id == playlist_id,
                    VideoProgress.status == VideoProgressStatus.COMPLETED,
                    Video.deleted_at.is_(None),
                    VideoProgress.deleted_at.is_(None),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_in_progress(self, user_id: UUID, playlist_id: UUID) -> int:
        """Count in-progress videos in a playlist for a user."""
        stmt = (
            select(func.count())
            .select_from(VideoProgress)
            .join(Video, VideoProgress.video_id == Video.id)
            .where(
                and_(
                    VideoProgress.user_id == user_id,
                    Video.playlist_id == playlist_id,
                    VideoProgress.status == VideoProgressStatus.IN_PROGRESS,
                    Video.deleted_at.is_(None),
                    VideoProgress.deleted_at.is_(None),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def sum_watch_time(self, user_id: UUID, playlist_id: UUID) -> int:
        """Sum total watch time for a user's playlist.

        Why this method exists: Provides aggregated watch time without
        loading all records. Used by the service to compute playlist
        watch time summaries.
        """
        stmt = (
            select(func.coalesce(func.sum(VideoProgress.watch_time_seconds), 0))
            .select_from(VideoProgress)
            .join(Video, VideoProgress.video_id == Video.id)
            .where(
                and_(
                    VideoProgress.user_id == user_id,
                    Video.playlist_id == playlist_id,
                    Video.deleted_at.is_(None),
                    VideoProgress.deleted_at.is_(None),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def avg_completion(self, user_id: UUID, playlist_id: UUID) -> float:
        """Average completion percentage for a user's playlist.

        Why this method exists: Provides aggregated completion percentage
        without loading all records. Used by the service to compute
        playlist-level completion averages.
        """
        stmt = (
            select(func.coalesce(func.avg(VideoProgress.completion_percentage), 0.0))
            .select_from(VideoProgress)
            .join(Video, VideoProgress.video_id == Video.id)
            .where(
                and_(
                    VideoProgress.user_id == user_id,
                    Video.playlist_id == playlist_id,
                    Video.deleted_at.is_(None),
                    VideoProgress.deleted_at.is_(None),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return float(result.scalar() or 0.0)

    async def exists_by_user_and_video(self, user_id: UUID, video_id: UUID) -> bool:
        """Check if a progress record exists for a user/video pair.

        Why this method exists: Provides an efficient existence check
        without loading the entire record.
        """
        return await self.get_by_user_and_video(user_id, video_id) is not None