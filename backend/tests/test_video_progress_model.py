"""Tests for the VideoProgress model.

Tests cover:
- Model creation with default values
- Model creation with custom values
- Unique constraint enforcement
- Relationship integrity
- Enum status values
- String representation
"""

from datetime import UTC, datetime
from uuid import uuid4, UUID

import pytest
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database.base import Base
from app.models.enums import VideoProgressStatus
from app.models.video_progress import VideoProgress
from app.models.user import User
from app.models.video import Video
from app.models.playlist import Playlist
from app.models.enums import PlaylistStatus, SourceType


@pytest.mark.asyncio
async def test_create_video_progress_defaults(db_session: AsyncSession) -> None:
    """Test creating a VideoProgress record with default values."""
    user = User(
        full_name="Test User",
        email="test@example.com",
        password_hash="hash",
    )
    db_session.add(user)
    await db_session.flush()

    playlist = Playlist(
        user_id=user.id,
        title="Test Playlist",
        source_type=SourceType.YOUTUBE,
        status=PlaylistStatus.ACTIVE,
    )
    db_session.add(playlist)
    await db_session.flush()

    video = Video(
        playlist_id=playlist.id,
        youtube_video_id="abc123",
        title="Test Video",
    )
    db_session.add(video)
    await db_session.flush()

    progress = VideoProgress(
        user_id=user.id,
        video_id=video.id,
    )
    db_session.add(progress)
    await db_session.flush()

    assert progress.status == VideoProgressStatus.NOT_STARTED
    assert progress.completion_percentage == 0.0
    assert progress.last_position_seconds == 0
    assert progress.watch_time_seconds == 0
    assert progress.first_started_at is None
    assert progress.last_watched_at is None
    assert progress.completed_at is None
    assert progress.user_id == user.id
    assert progress.video_id == video.id


@pytest.mark.asyncio
async def test_create_video_progress_custom_values(db_session: AsyncSession) -> None:
    """Test creating a VideoProgress record with custom values."""
    user = User(
        full_name="Test User",
        email="test2@example.com",
        password_hash="hash",
    )
    db_session.add(user)
    await db_session.flush()

    playlist = Playlist(
        user_id=user.id,
        title="Test Playlist",
        source_type=SourceType.YOUTUBE,
        status=PlaylistStatus.ACTIVE,
    )
    db_session.add(playlist)
    await db_session.flush()

    video = Video(
        playlist_id=playlist.id,
        youtube_video_id="def456",
        title="Test Video 2",
    )
    db_session.add(video)
    await db_session.flush()

    now = datetime.now(UTC)
    progress = VideoProgress(
        user_id=user.id,
        video_id=video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        last_position_seconds=120,
        watch_time_seconds=120,
        first_started_at=now,
        last_watched_at=now,
    )
    db_session.add(progress)
    await db_session.flush()

    assert progress.status == VideoProgressStatus.IN_PROGRESS
    assert progress.completion_percentage == 50.0
    assert progress.last_position_seconds == 120
    assert progress.watch_time_seconds == 120


@pytest.mark.asyncio
async def test_video_progress_unique_constraint(db_session: AsyncSession) -> None:
    """Test that the unique constraint on (user_id, video_id) is enforced."""
    user = User(
        full_name="Test User",
        email="test3@example.com",
        password_hash="hash",
    )
    db_session.add(user)
    await db_session.flush()

    playlist = Playlist(
        user_id=user.id,
        title="Test Playlist",
        source_type=SourceType.YOUTUBE,
        status=PlaylistStatus.ACTIVE,
    )
    db_session.add(playlist)
    await db_session.flush()

    video = Video(
        playlist_id=playlist.id,
        youtube_video_id="ghi789",
        title="Test Video 3",
    )
    db_session.add(video)
    await db_session.flush()

    progress1 = VideoProgress(
        user_id=user.id,
        video_id=video.id,
    )
    db_session.add(progress1)
    await db_session.flush()

    # Attempt to create a duplicate record
    with pytest.raises(Exception):  # IntegrityError
        progress2 = VideoProgress(
            user_id=user.id,
            video_id=video.id,
        )
        db_session.add(progress2)
        await db_session.flush()
        await db_session.commit()


@pytest.mark.asyncio
async def test_video_progress_cascade_delete_user(db_session: AsyncSession) -> None:
    """Test that deleting a user cascades to VideoProgress records."""
    user = User(
        full_name="Test User",
        email="test4@example.com",
        password_hash="hash",
    )
    db_session.add(user)
    await db_session.flush()

    playlist = Playlist(
        user_id=user.id,
        title="Test Playlist",
        source_type=SourceType.YOUTUBE,
        status=PlaylistStatus.ACTIVE,
    )
    db_session.add(playlist)
    await db_session.flush()

    video = Video(
        playlist_id=playlist.id,
        youtube_video_id="jkl012",
        title="Test Video 4",
    )
    db_session.add(video)
    await db_session.flush()

    progress = VideoProgress(
        user_id=user.id,
        video_id=video.id,
    )
    db_session.add(progress)
    await db_session.flush()

    progress_id = progress.id

    # Delete the user (soft delete)
    await db_session.delete(user)
    await db_session.flush()

    # The progress record should also be deleted
    result = await db_session.execute(
        select(VideoProgress).where(VideoProgress.id == progress_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_video_progress_status_enum_values() -> None:
    """Test that VideoProgressStatus enum has the expected values."""
    assert VideoProgressStatus.NOT_STARTED.value == "not_started"
    assert VideoProgressStatus.IN_PROGRESS.value == "in_progress"
    assert VideoProgressStatus.COMPLETED.value == "completed"


@pytest.mark.asyncio
async def test_video_progress_repr(db_session: AsyncSession) -> None:
    """Test the string representation of VideoProgress."""
    user = User(
        full_name="Test User",
        email="test5@example.com",
        password_hash="hash",
    )
    db_session.add(user)
    await db_session.flush()

    playlist = Playlist(
        user_id=user.id,
        title="Test Playlist",
        source_type=SourceType.YOUTUBE,
        status=PlaylistStatus.ACTIVE,
    )
    db_session.add(playlist)
    await db_session.flush()

    video = Video(
        playlist_id=playlist.id,
        youtube_video_id="mno345",
        title="Test Video 5",
    )
    db_session.add(video)
    await db_session.flush()

    progress = VideoProgress(
        user_id=user.id,
        video_id=video.id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=42.5,
    )
    db_session.add(progress)
    await db_session.flush()

    repr_str = repr(progress)
    assert str(progress.id) in repr_str
    assert str(user.id) in repr_str
    assert str(video.id) in repr_str
    assert "in_progress" in repr_str
    assert "42.5" in repr_str