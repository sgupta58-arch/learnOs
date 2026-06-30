"""VideoProgress service for business logic and orchestration.

Why this service exists: All business rules for video progress tracking
belong here. The service ensures data integrity by enforcing:
- completion_percentage cannot exceed 100
- watch_time cannot decrease
- completed_at is set only the first time
- status transitions follow: NOT_STARTED -> IN_PROGRESS -> COMPLETED
- Auto-creation of progress records on first interaction
- Ownership validation before any operation

Why it belongs to the services layer: Business logic must be isolated
from both routes and repositories. This service enforces all progress
business rules and orchestrates repository calls.

How future Learning Sessions will use it: Will call resume_playback()
and update_progress() to track ongoing learning sessions.

How future AI Tutor will use it: Will query progress summaries to
personalize tutoring sessions based on what the user has watched.
"""

from datetime import UTC, datetime
from uuid import UUID

from app.exceptions.base import ForbiddenException, NotFoundException
from app.models.enums import VideoProgressStatus
from app.models.video import Video
from app.models.video_progress import VideoProgress
from app.repositories.playlist import PlaylistRepository
from app.repositories.video import VideoRepository
from app.repositories.video_progress import VideoProgressRepository
from app.schemas.progress import (
    ProgressResponseSchema,
    ProgressSummarySchema,
    ProgressUpdateSchema,
)


class VideoProgressService:
    """Service layer for video progress operations.

    All business rules for tracking learning progress are enforced here.
    The service never accesses the database directly — it uses
    VideoProgressRepository for persistence and VideoRepository for
    video lookups.
    """

    def __init__(
        self,
        repository: VideoProgressRepository,
        video_repository: VideoRepository,
    ) -> None:
        self.repository = repository
        self.video_repository = video_repository

    def _to_response(self, progress: VideoProgress) -> ProgressResponseSchema:
        """Convert a VideoProgress model to its response schema."""
        return ProgressResponseSchema.model_validate(progress)

    async def _get_video_or_raise(self, video_id: UUID) -> Video:
        """Get a video or raise NotFoundException."""
        video = await self.video_repository.get_by_id(video_id)
        if video is None:
            raise NotFoundException(message="Video not found")
        return video

    async def _get_progress_or_raise(
        self,
        user_id: UUID,
        video_id: UUID,
    ) -> VideoProgress:
        """Get a progress record or raise NotFoundException."""
        progress = await self.repository.get_by_user_and_video(user_id, video_id)
        if progress is None:
            raise NotFoundException(message="Progress record not found")
        return progress

    def _verify_ownership(self, progress: VideoProgress, user_id: UUID) -> None:
        """Verify that the progress record belongs to the given user."""
        if progress.user_id != user_id:
            raise ForbiddenException(message="Access denied to this progress record")

    async def get_or_create(
        self,
        user_id: UUID,
        video_id: UUID,
    ) -> VideoProgress:
        """Get existing progress or create a new one.

        Why this method exists: Users may not have a progress record for
        every video. This method ensures a record always exists, enabling
        seamless first-time interactions.

        Business rules:
        - If a record exists, return it as-is.
        - If no record exists, create one with NOT_STARTED status.
        """
        await self._get_video_or_raise(video_id)

        existing = await self.repository.get_by_user_and_video(user_id, video_id)
        if existing is not None:
            return existing

        progress = VideoProgress(
            user_id=user_id,
            video_id=video_id,
            status=VideoProgressStatus.NOT_STARTED,
            completion_percentage=0.0,
            last_position_seconds=0,
            watch_time_seconds=0,
        )
        return await self.repository.create(progress)

    async def get_progress(
        self,
        user_id: UUID,
        video_id: UUID,
    ) -> ProgressResponseSchema:
        """Get progress for a specific video.

        Raises NotFoundException if the video or progress record doesn't exist.
        """
        await self._get_video_or_raise(video_id)
        progress = await self._get_progress_or_raise(user_id, video_id)
        self._verify_ownership(progress, user_id)
        return self._to_response(progress)

    async def update_progress(
        self,
        user_id: UUID,
        video_id: UUID,
        payload: ProgressUpdateSchema,
    ) -> ProgressResponseSchema:
        """Update video progress with business rule enforcement.

        Business rules enforced:
        1. Video must exist.
        2. Progress record is auto-created if it doesn't exist.
        3. watch_time_seconds cannot decrease (prevents replay manipulation).
        4. completion_percentage is clamped to 0–100 (already validated by Pydantic).
        5. Status transitions follow: NOT_STARTED -> IN_PROGRESS -> COMPLETED.
        6. completed_at is set only the first time a video is completed.
        7. first_started_at is set on first interaction.
        8. last_watched_at is updated on every interaction.

        How future Learning Sessions will use it: Will call this method
        periodically during a learning session to persist progress.
        """
        await self._get_video_or_raise(video_id)

        progress = await self.get_or_create(user_id, video_id)
        now = datetime.now(UTC)

        # Track whether this is the first interaction
        is_first_interaction = progress.first_started_at is None

        # Update timestamps
        if is_first_interaction:
            progress.first_started_at = now
        progress.last_watched_at = now

        # Update watch_time: never decrease
        if (
            payload.watch_time_seconds is not None
            and payload.watch_time_seconds > progress.watch_time_seconds
        ):
            progress.watch_time_seconds = payload.watch_time_seconds

        # Update completion_percentage
        if payload.completion_percentage is not None:
            progress.completion_percentage = payload.completion_percentage

        # Update last_position
        if payload.last_position_seconds is not None:
            progress.last_position_seconds = payload.last_position_seconds

        # Handle status transitions
        if payload.status is not None:
            if (
                payload.status == VideoProgressStatus.IN_PROGRESS
                and progress.status == VideoProgressStatus.NOT_STARTED
            ):
                progress.status = VideoProgressStatus.IN_PROGRESS
            elif payload.status == VideoProgressStatus.COMPLETED:
                # Only set completed_at on the first time
                if progress.status != VideoProgressStatus.COMPLETED:
                    progress.completed_at = now
                    progress.completion_percentage = 100.0
                progress.status = VideoProgressStatus.COMPLETED

        # Auto-transition to COMPLETED if completion_percentage reaches 100
        if (
            progress.completion_percentage >= 100.0
            and progress.status != VideoProgressStatus.COMPLETED
        ):
            progress.status = VideoProgressStatus.COMPLETED
            if progress.completed_at is None:
                progress.completed_at = now

        # Auto-transition to IN_PROGRESS if there's activity but still NOT_STARTED
        if (
            progress.status == VideoProgressStatus.NOT_STARTED
            and progress.watch_time_seconds > 0
        ):
            progress.status = VideoProgressStatus.IN_PROGRESS

        updated = await self.repository.update(progress)
        return self._to_response(updated)

    async def mark_completed(
        self,
        user_id: UUID,
        video_id: UUID,
    ) -> ProgressResponseSchema:
        """Mark a video as completed.

        Why this method exists: Provides a convenience method for the
        common operation of marking a video as finished. Sets completion
        to 100% and status to COMPLETED.

        Business rules:
        - completed_at is set only the first time.
        - Prevents overwriting an existing completion timestamp.

        How future Learning Sessions will use it: Will call this when
        the user finishes a video.
        """
        payload = ProgressUpdateSchema(
            status=VideoProgressStatus.COMPLETED,
            completion_percentage=100.0,
        )
        return await self.update_progress(user_id, video_id, payload)

    async def resume_playback(
        self,
        user_id: UUID,
        video_id: UUID,
    ) -> ProgressResponseSchema:
        """Get the last playback position for a video.

        Why this method exists: Allows the frontend to resume playback
        from where the user left off, including position and status context.

        Business rules:
        - Auto-creates a progress record if none exists.
        - Returns current position and status.

        How future Learning Sessions will use it: Will call this at the
        start of a learning session to restore playback state.
        """
        progress = await self.get_or_create(user_id, video_id)
        return self._to_response(progress)

    async def get_playlist_progress(
        self,
        user_id: UUID,
        playlist_id: UUID,
    ) -> ProgressSummarySchema:
        """Get aggregated progress summary for a playlist.

        Why this method exists: Provides a complete picture of the user's
        progress across all videos in a playlist. This is used by the
        frontend to show playlist completion status and by future phases
        to compute learning recommendations.

        This is NOT analytics — it returns raw computed summaries.

        How future Analytics will use it: Will consume this data to
        compute learning insights and generate reports.

        How future AI Tutor will use it: Will use completion data to
        determine which topics need reinforcement.
        """
        # Get playlist and verify ownership
        playlist_repo = PlaylistRepository(self.repository.session)
        playlist = await playlist_repo.get_by_id(playlist_id)
        if playlist is None:
            raise NotFoundException(message="Playlist not found")
        if playlist.user_id != user_id:
            raise ForbiddenException(message="Access denied to this playlist")

        # Get all videos in the playlist
        videos = await self.video_repository.list_by_playlist(playlist_id)
        total_videos = len(videos)

        # Get aggregated data from repository
        completed = await self.repository.count_completed(user_id, playlist_id)
        in_progress = await self.repository.count_in_progress(user_id, playlist_id)
        not_started = total_videos - completed - in_progress
        total_watch_time = await self.repository.sum_watch_time(user_id, playlist_id)
        avg_completion = await self.repository.avg_completion(user_id, playlist_id)

        # Estimate remaining time based on video durations minus completed
        total_duration = sum(
            (v.duration_seconds or 0) for v in videos
        )
        estimated_remaining = max(
            0,
            total_duration - total_watch_time,
        )

        return ProgressSummarySchema(
            total_videos=total_videos,
            completed_videos=completed,
            in_progress_videos=in_progress,
            not_started_videos=not_started,
            total_watch_time_seconds=total_watch_time,
            average_completion_percentage=round(avg_completion, 1),
            estimated_remaining_seconds=estimated_remaining,
        )

    async def get_user_progress(
        self,
        user_id: UUID,
    ) -> list[ProgressResponseSchema]:
        """Get all progress records for a user.

        Why this method exists: Provides a complete view of a user's
        progress across all videos. Used for user-level progress summaries.

        How future Analytics will use it: Will aggregate progress data
        across all user content to compute overall learning metrics.
        """
        records = await self.repository.list_by_user(user_id)
        return [self._to_response(record) for record in records]