"""Tests for the VideoProgressRepository.

Tests cover:
- Creating and retrieving progress records
- Lookup by user and video
- Listing by playlist
- Listing by user
- Aggregation queries (count_completed, sum_watch_time, avg_completion)
- Existence checks
- Soft delete filtering
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PlaylistStatus, SourceType, VideoProgressStatus
from app.models.playlist import Playlist
from app.models.user import User
from app.models.video import Video
from app.models.video_progress import VideoProgress
from app.repositories.video_progress import VideoProgressRepository


@pytest.fixture
async def setup_data(db_session: AsyncSession) -> dict:
    """Create test data: user, playlist, videos, and progress records."""
    user = User(
        full_name="Test User",
        email="test_repo@example.com",
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

    videos = []
    for i in range(3):
        video = Video(
            playlist_id=playlist.id,
            youtube_video_id=f"repo_test_{i}",
            title=f"Video {i}",
            position=i,
            duration_seconds=300,
        )
        db_session.add(video)
        await db_session.flush()
        videos.append(video)

    # Create progress records
    # Video 0: COMPLETED
    progress0 = VideoProgress(
        user_id=user.id,
        video_id=videos[0].id,
        status=VideoProgressStatus.COMPLETED,
        completion_percentage=100.0,
        watch_time_seconds=300,
        last_position_seconds=300,
    )
    db_session.add(progress0)

    # Video 1: IN_PROGRESS
    progress1 = VideoProgress(
        user_id=user.id,
        video_id=videos[1].id,
        status=VideoProgressStatus.IN_PROGRESS,
        completion_percentage=50.0,
        watch_time_seconds=150,
        last_position_seconds=150,
    )
    db_session.add(progress1)

    # Video 2: no progress record (NOT_STARTED implicitly)
    await db_session.flush()

    return {
        "user": user,
        "playlist": playlist,
        "videos": videos,
        "progress0": progress0,
        "progress1": progress1,
    }


@pytest.mark.asyncio
async def test_create_progress(db_session: AsyncSession) -> None:
    """Test creating a new progress record."""
    user = User(full_name="Test", email="test_create@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.flush()

    playlist = Playlist(user_id=user.id, title="Test", source_type=SourceType.YOUTUBE, status=PlaylistStatus.ACTIVE)
    db_session.add(playlist)
    await db_session.flush()

    video = Video(playlist_id=playlist.id, youtube_video_id="create_test", title="Test")
    db_session.add(video)
    await db_session.flush()

    repo = VideoProgressRepository(db_session)
    progress = VideoProgress(user_id=user.id, video_id=video.id)
    created = await repo.create(progress)

    assert created.id is not None
    assert created.user_id == user.id
    assert created.video_id == video.id
    assert created.status == VideoProgressStatus.NOT_STARTED


@pytest.mark.asyncio
async def test_get_by_user_and_video(db_session: AsyncSession, setup_data: dict) -> None:
    """Test retrieving a progress record by user and video."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]
    video = setup_data["videos"][0]

    result = await repo.get_by_user_and_video(user.id, video.id)
    assert result is not None
    assert result.user_id == user.id
    assert result.video_id == video.id
    assert result.status == VideoProgressStatus.COMPLETED


@pytest.mark.asyncio
async def test_get_by_user_and_video_not_found(db_session: AsyncSession, setup_data: dict) -> None:
    """Test retrieving a non-existent progress record."""
    repo = VideoProgressRepository(db_session)
    result = await repo.get_by_user_and_video(uuid4(), uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_list_by_playlist(db_session: AsyncSession, setup_data: dict) -> None:
    """Test listing all progress records for a playlist."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]
    playlist = setup_data["playlist"]

    results = await repo.list_by_playlist(user.id, playlist.id)
    assert len(results) == 2  # Only videos with progress records


@pytest.mark.asyncio
async def test_list_by_user(db_session: AsyncSession, setup_data: dict) -> None:
    """Test listing all progress records for a user."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]

    results = await repo.list_by_user(user.id)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_count_completed(db_session: AsyncSession, setup_data: dict) -> None:
    """Test counting completed videos in a playlist."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]
    playlist = setup_data["playlist"]

    count = await repo.count_completed(user.id, playlist.id)
    assert count == 1


@pytest.mark.asyncio
async def test_count_in_progress(db_session: AsyncSession, setup_data: dict) -> None:
    """Test counting in-progress videos in a playlist."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]
    playlist = setup_data["playlist"]

    count = await repo.count_in_progress(user.id, playlist.id)
    assert count == 1


@pytest.mark.asyncio
async def test_sum_watch_time(db_session: AsyncSession, setup_data: dict) -> None:
    """Test summing watch time for a playlist."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]
    playlist = setup_data["playlist"]

    total = await repo.sum_watch_time(user.id, playlist.id)
    assert total == 450  # 300 (completed) + 150 (in_progress)


@pytest.mark.asyncio
async def test_avg_completion(db_session: AsyncSession, setup_data: dict) -> None:
    """Test average completion percentage for a playlist."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]
    playlist = setup_data["playlist"]

    avg = await repo.avg_completion(user.id, playlist.id)
    assert avg == 75.0  # (100 + 50) / 2


@pytest.mark.asyncio
async def test_exists_by_user_and_video(db_session: AsyncSession, setup_data: dict) -> None:
    """Test existence check for a user/video pair."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]
    video = setup_data["videos"][0]

    exists = await repo.exists_by_user_and_video(user.id, video.id)
    assert exists is True

    not_exists = await repo.exists_by_user_and_video(user.id, uuid4())
    assert not_exists is False


@pytest.mark.asyncio
async def test_soft_delete_filters_out(db_session: AsyncSession, setup_data: dict) -> None:
    """Test that soft-deleted progress records are excluded."""
    repo = VideoProgressRepository(db_session)
    user = setup_data["user"]
    video = setup_data["videos"][0]

    progress = setup_data["progress0"]
    await repo.soft_delete(progress)

    result = await repo.get_by_user_and_video(user.id, video.id)
    assert result is None