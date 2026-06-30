from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.models.video import Video
from app.schemas.video import VideoCreateSchema, VideoUpdateSchema
from app.services.video import VideoService


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repo: AsyncMock) -> VideoService:
    return VideoService(mock_repo)


@pytest.mark.asyncio
async def test_create_adds_video_to_playlist(service: VideoService, mock_repo: AsyncMock) -> None:
    playlist_id = uuid4()
    mock_repo.create.return_value = Video(
        id=uuid4(),
        playlist_id=playlist_id,
        youtube_video_id="abc123",
        title="Intro",
        description="Demo",
        thumbnail_url="https://example.com/thumb.jpg",
        channel_name="Example",
        duration_seconds=120,
        position=1,
    )

    payload = VideoCreateSchema(
        youtube_video_id="abc123",
        title="Intro",
        description="Demo",
        thumbnail_url="https://example.com/thumb.jpg",
        channel_name="Example",
        duration_seconds=120,
        position=1,
    )

    created = await service.create(playlist_id, payload)

    mock_repo.create.assert_awaited_once()
    assert created.playlist_id == playlist_id
    assert created.title == "Intro"


@pytest.mark.asyncio
async def test_list_by_playlist_uses_repository(service: VideoService, mock_repo: AsyncMock) -> None:
    playlist_id = uuid4()
    mock_repo.list_by_playlist.return_value = [
        Video(id=uuid4(), playlist_id=playlist_id, youtube_video_id="abc123", title="Intro")
    ]

    videos = await service.list_by_playlist(playlist_id)

    mock_repo.list_by_playlist.assert_awaited_once_with(playlist_id)
    assert len(videos) == 1
    assert videos[0].youtube_video_id == "abc123"
