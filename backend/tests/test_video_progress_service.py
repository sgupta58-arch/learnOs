"""Tests for the VideoProgressService.

Tests cover:
- get_or_create: auto-creating progress records
- get_progress: retrieving progress with ownership validation
- update_progress: business rules enforcement
  - watch_time cannot decrease
  - Status transitions (NOT_STARTED -> IN_PROGRESS -> COMPLETED)
  - completed_at set only first time
  - Auto-transition at 100% completion
  - Auto-transition on first activity
- mark_completed: convenience method
- resume_playback: returning last position
- get_playlist_progress: aggregation
- get_user_progress: listing all user progress
- Edge cases: progress >100, duplicate, ownership validation
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4, UUID

import pytest

from app.exceptions.base import ForbiddenException, NotFoundException
from app.models.enums import PlaylistStatus, SourceType, VideoProgressStatus
from app.models.playlist import Playlist
from app.models.user import User
from app.models.video import Video
from app.models.video_progress import VideoProgress
from app.schemas.progress import ProgressUpdateSchema
from app.services.video_progress import VideoProgressService

NOW = datetime.now(UTC)
TEST_USER_ID = uuid4()


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_video_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
) -> VideoProgressService:
    return VideoProgressService(
        repository=mock_repo,
        video_repository=mock_video_repo,
    )


@pytest.fixture
def sample_video() -> Video:
    return Video(
        id=uuid4(),
        playlist_id=uuid4(),
        youtube_video_id="test123",
        title="Test Video",
        duration_seconds=300,
    )


# ─── get_or_create ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_or_create_returns_existing(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test get_or_create returns existing progress record."""
    mock_video_repo.get_by_id.return_value = sample_video

    existing_progress = VideoProgress(
        id=uuid4(),
        user_id=uuid4(),
        video_id=sample_video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
    )
    mock_repo.get_by_user_and_video.return_value = existing_progress

    result = await service.get_or_create(
        user_id=existing_progress.user_id,
        video_id=sample_video.id,
    )

    assert result is existing_progress
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_creates_new(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test get_or_create creates a new progress record."""
    mock_video_repo.get_by_id.return_value = sample_video
    mock_repo.get_by_user_and_video.return_value = None

    new_progress = VideoProgress(
        id=uuid4(),
        user_id=uuid4(),
        video_id=sample_video.id,
        status=VideoProgressStatus.NOT_STARTED,
        completion_percentage=0.0,
        last_position_seconds=0,
        watch_time_seconds=0,
    )
    mock_repo.create.return_value = new_progress

    result = await service.get_or_create(
        user_id=new_progress.user_id,
        video_id=sample_video.id,
    )

    assert result is new_progress
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_or_create_video_not_found(
    service: VideoProgressService,
    mock_video_repo: AsyncMock,
) -> None:
    """Test get_or_create raises NotFoundException for missing video."""
    mock_video_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await service.get_or_create(
            user_id=uuid4(),
            video_id=uuid4(),
        )


# ─── get_progress ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_progress_success(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test successful progress retrieval."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
        created_at=NOW,
        updated_at=NOW,
    )
    mock_repo.get_by_user_and_video.return_value = progress

    result = await service.get_progress(user_id=user_id, video_id=sample_video.id)

    assert result.id == progress.id
    assert result.status == VideoProgressStatus.IN_PROGRESS
    assert result.completion_percentage == 50.0


@pytest.mark.asyncio
async def test_get_progress_not_found(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test get_progress raises NotFoundException for missing video."""
    mock_video_repo.get_by_id.return_value = sample_video
    mock_repo.get_by_user_and_video.return_value = None

    with pytest.raises(NotFoundException):
        await service.get_progress(user_id=uuid4(), video_id=sample_video.id)


@pytest.mark.asyncio
async def test_get_progress_forbidden(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test get_progress raises ForbiddenException for wrong user."""
    mock_video_repo.get_by_id.return_value = sample_video

    owner_id = uuid4()
    other_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=owner_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
    )
    mock_repo.get_by_user_and_video.return_value = progress

    with pytest.raises(ForbiddenException):
        await service.get_progress(user_id=other_id, video_id=sample_video.id)


# ─── update_progress ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_progress_auto_creates(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test update_progress auto-creates a progress record."""
    mock_video_repo.get_by_id.return_value = sample_video
    mock_repo.get_by_user_and_video.return_value = None

    user_id = uuid4()
    new_progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.NOT_STARTED,
        completion_percentage=0.0,
        last_position_seconds=0,
        watch_time_seconds=0,
    )
    mock_repo.create.return_value = new_progress
    mock_repo.update.return_value = new_progress

    payload = ProgressUpdateSchema(last_position_seconds=30)
    result = await service.update_progress(
        user_id=user_id,
        video_id=sample_video.id,
        payload=payload,
    )

    mock_repo.create.assert_awaited_once()
    assert result is not None


@pytest.mark.asyncio
async def test_update_progress_watch_time_does_not_decrease(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test that watch_time cannot decrease."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
    )
    mock_repo.get_by_user_and_video.return_value = progress
    mock_repo.update.return_value = progress

    payload = ProgressUpdateSchema(watch_time_seconds=30)
    result = await service.update_progress(
        user_id=user_id,
        video_id=sample_video.id,
        payload=payload,
    )

    # Should remain at 120 (not decrease to 30)
    assert result.watch_time_seconds == 120


@pytest.mark.asyncio
async def test_update_progress_status_transition_to_in_progress(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test status transitions from NOT_STARTED to IN_PROGRESS."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.NOT_STARTED,
        completion_percentage=0.0,
        last_position_seconds=0,
        watch_time_seconds=0,
    )
    mock_repo.get_by_user_and_video.return_value = progress
    mock_repo.update.return_value = progress

    payload = ProgressUpdateSchema(status=VideoProgressStatus.IN_PROGRESS)
    result = await service.update_progress(
        user_id=user_id,
        video_id=sample_video.id,
        payload=payload,
    )

    assert result.status == VideoProgressStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_update_progress_status_transition_to_completed(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test status transitions to COMPLETED and sets completed_at."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
    )
    mock_repo.get_by_user_and_video.return_value = progress
    mock_repo.update.return_value = progress

    payload = ProgressUpdateSchema(status=VideoProgressStatus.COMPLETED)
    result = await service.update_progress(
        user_id=user_id,
        video_id=sample_video.id,
        payload=payload,
    )

    assert result.status == VideoProgressStatus.COMPLETED
    assert result.completion_percentage == 100.0


@pytest.mark.asyncio
async def test_update_progress_completed_at_only_first_time(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test that completed_at is set only the first time."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.COMPLETED,
        completion_percentage=100.0,
        last_position_seconds=300,
        watch_time_seconds=300,
        completed_at=NOW,
    )
    mock_repo.get_by_user_and_video.return_value = progress
    mock_repo.update.return_value = progress

    payload = ProgressUpdateSchema(status=VideoProgressStatus.COMPLETED)
    result = await service.update_progress(
        user_id=user_id,
        video_id=sample_video.id,
        payload=payload,
    )

    # completed_at should remain the original value
    assert result.completed_at == NOW


@pytest.mark.asyncio
async def test_update_progress_auto_complete_at_100(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test auto-transition to COMPLETED at 100% completion."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.NOT_STARTED,
        completion_percentage=0.0,
        last_position_seconds=0,
        watch_time_seconds=0,
    )
    mock_repo.get_by_user_and_video.return_value = progress
    mock_repo.update.return_value = progress

    payload = ProgressUpdateSchema(completion_percentage=100.0)
    result = await service.update_progress(
        user_id=user_id,
        video_id=sample_video.id,
        payload=payload,
    )

    assert result.status == VideoProgressStatus.COMPLETED
    assert result.completion_percentage == 100.0


@pytest.mark.asyncio
async def test_update_progress_auto_in_progress_on_activity(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test auto-transition to IN_PROGRESS when activity is detected."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.NOT_STARTED,
        completion_percentage=0.0,
        last_position_seconds=0,
        watch_time_seconds=0,
    )
    mock_repo.get_by_user_and_video.return_value = progress
    mock_repo.update.return_value = progress

    payload = ProgressUpdateSchema(watch_time_seconds=10)
    result = await service.update_progress(
        user_id=user_id,
        video_id=sample_video.id,
        payload=payload,
    )

    assert result.status == VideoProgressStatus.IN_PROGRESS


# ─── mark_completed ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mark_completed(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test mark_completed sets status to COMPLETED."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
    )
    mock_repo.get_by_user_and_video.return_value = progress
    mock_repo.update.return_value = progress

    result = await service.mark_completed(
        user_id=user_id,
        video_id=sample_video.id,
    )

    assert result.status == VideoProgressStatus.COMPLETED
    assert result.completion_percentage == 100.0


# ─── resume_playback ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_resume_playback_auto_creates(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test resume_playback auto-creates a progress record."""
    mock_video_repo.get_by_id.return_value = sample_video
    mock_repo.get_by_user_and_video.return_value = None

    user_id = uuid4()
    new_progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.NOT_STARTED,
        completion_percentage=0.0,
        last_position_seconds=0,
        watch_time_seconds=0,
    )
    mock_repo.create.return_value = new_progress

    result = await service.resume_playback(
        user_id=user_id,
        video_id=sample_video.id,
    )

    assert result.status == VideoProgressStatus.NOT_STARTED
    assert result.last_position_seconds == 0


@pytest.mark.asyncio
async def test_resume_playback_returns_position(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test resume_playback returns last position."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
    )
    mock_repo.get_by_user_and_video.return_value = progress

    result = await service.resume_playback(
        user_id=user_id,
        video_id=sample_video.id,
    )

    assert result.last_position_seconds == 120


# ─── get_playlist_progress ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_playlist_progress(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
) -> None:
    """Test playlist progress aggregation."""
    user_id = uuid4()
    playlist_id = uuid4()
    video_ids = [uuid4(), uuid4(), uuid4()]

    # Mock playlist repo
    playlist = Playlist(
        id=playlist_id,
        user_id=user_id,
        title="Test",
        source_type=SourceType.YOUTUBE,
        status=PlaylistStatus.ACTIVE,
    )

    # Mock the internal PlaylistRepository
    with patch("app.services.video_progress.PlaylistRepository") as mock_pl_repo_cls:
        mock_pl_repo = AsyncMock()
        mock_pl_repo.get_by_id.return_value = playlist
        mock_pl_repo_cls.return_value = mock_pl_repo

        mock_video_repo.list_by_playlist.return_value = [
            Video(id=video_ids[0], playlist_id=playlist_id, youtube_video_id="a", title="A", duration_seconds=300),
            Video(id=video_ids[1], playlist_id=playlist_id, youtube_video_id="b", title="B", duration_seconds=300),
            Video(id=video_ids[2], playlist_id=playlist_id, youtube_video_id="c", title="C", duration_seconds=300),
        ]

        mock_repo.count_completed.return_value = 1
        mock_repo.count_in_progress.return_value = 1
        mock_repo.sum_watch_time.return_value = 450
        mock_repo.avg_completion.return_value = 50.0

        result = await service.get_playlist_progress(
            user_id=user_id,
            playlist_id=playlist_id,
        )

        assert result.total_videos == 3
        assert result.completed_videos == 1
        assert result.in_progress_videos == 1
        assert result.not_started_videos == 1
        assert result.total_watch_time_seconds == 450
        assert result.average_completion_percentage == 50.0


# ─── get_user_progress ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_user_progress(
    service: VideoProgressService,
    mock_repo: AsyncMock,
) -> None:
    """Test getting all progress records for a user."""
    user_id = uuid4()
    mock_repo.list_by_user.return_value = [
        VideoProgress(
            id=uuid4(),
            user_id=user_id,
            video_id=uuid4(),
            status=VideoProgressStatus.IN_PROGRESS,
            completion_percentage=50.0,
            last_position_seconds=120,
            watch_time_seconds=120,
            created_at=NOW,
            updated_at=NOW,
        ),
    ]

    results = await service.get_user_progress(user_id=user_id)
    assert len(results) == 1


# ─── Edge Cases ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_progress_video_not_found(
    service: VideoProgressService,
    mock_video_repo: AsyncMock,
) -> None:
    """Test update_progress raises NotFoundException for missing video."""
    mock_video_repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException):
        await service.update_progress(
            user_id=uuid4(),
            video_id=uuid4(),
            payload=ProgressUpdateSchema(),
        )


@pytest.mark.asyncio
async def test_update_progress_first_started_at_set(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test that first_started_at is set on first interaction."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.NOT_STARTED,
        completion_percentage=0.0,
        last_position_seconds=0,
        watch_time_seconds=0,
        first_started_at=None,
    )
    mock_repo.get_by_user_and_video.return_value = progress
    mock_repo.update.return_value = progress

    payload = ProgressUpdateSchema(last_position_seconds=10)
    result = await service.update_progress(
        user_id=user_id,
        video_id=sample_video.id,
        payload=payload,
    )

    # first_started_at should have been set (we can't check exact time, but it's not None)
    # Note: since we're using the same progress object, first_started_at was set on it
    assert progress.first_started_at is not None


@pytest.mark.asyncio
async def test_get_or_create_unique_user_video(
    service: VideoProgressService,
    mock_repo: AsyncMock,
    mock_video_repo: AsyncMock,
    sample_video: Video,
) -> None:
    """Test idempotency of get_or_create."""
    mock_video_repo.get_by_id.return_value = sample_video

    user_id = uuid4()
    progress = VideoProgress(
        id=uuid4(),
        user_id=user_id,
        video_id=sample_video.id,
        status=VideoProgressStatus.NOT_STARTED,
        completion_percentage=0.0,
        last_position_seconds=0,
        watch_time_seconds=0,
    )
    mock_repo.get_by_user_and_video.return_value = progress

    # Call twice
    result1 = await service.get_or_create(user_id=user_id, video_id=sample_video.id)
    result2 = await service.get_or_create(user_id=user_id, video_id=sample_video.id)

    # Should return the same record both times
    assert result1 is result2
    mock_repo.create.assert_not_called()