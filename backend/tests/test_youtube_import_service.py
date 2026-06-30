from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.enums import PlaylistStatus, SourceType
from app.models.playlist import Playlist
from app.models.video import Video
from app.platform.youtube.client import YouTubeClient
from app.platform.youtube.parser import YouTubeURLParser
from app.services.youtube_import import YouTubePlaylistImportService


@pytest.fixture
def playlist_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def video_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def youtube_client() -> MagicMock:
    return MagicMock(spec=YouTubeClient)


@pytest.fixture
def url_parser() -> MagicMock:
    return MagicMock(spec=YouTubeURLParser)


@pytest.fixture
def service(
    playlist_repo: AsyncMock,
    video_repo: AsyncMock,
    youtube_client: MagicMock,
    url_parser: MagicMock,
) -> YouTubePlaylistImportService:
    return YouTubePlaylistImportService(playlist_repo, video_repo, youtube_client, url_parser)


def test_parse_playlist_id_accepts_playlist_url(service: YouTubePlaylistImportService) -> None:
    assert service.parse_playlist_id("https://www.youtube.com/playlist?list=PL123") == "PL123"


def test_parse_video_id_accepts_watch_url(service: YouTubePlaylistImportService) -> None:
    assert service.parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"


@pytest.mark.asyncio
async def test_import_playlist_validates_url(
    service: YouTubePlaylistImportService,
    url_parser: MagicMock,
) -> None:
    url_parser.is_playlist_url.return_value = True
    url_parser.parse_playlist_url.return_value = ("PL123", "https://www.youtube.com/playlist?list=PL123")
    
    # Mock the YouTube client methods
    service.youtube_client.fetch_playlist_metadata.return_value = MagicMock(
        title="Test Playlist",
        video_count=5,
    )
    service.youtube_client.fetch_playlist_items.return_value = [
        MagicMock(
            video_id="video1",
            title="Video 1",
            description="Description 1",
            thumbnail_url="https://example.com/thumb1.jpg",
            channel_title="Channel 1",
            duration_seconds=120,
            position=1,
            published_at="2023-01-01T00:00:00Z",
        ),
        MagicMock(
            video_id="video2",
            title="Video 2",
            description="Description 2",
            thumbnail_url="https://example.com/thumb2.jpg",
            channel_title="Channel 2",
            duration_seconds=180,
            position=2,
            published_at="2023-01-02T00:00:00Z",
        ),
    ]
    
    playlist_repo = service.playlist_repository
    video_repo = service.video_repository
    
    playlist_repo.create.return_value = Playlist(
        id=uuid4(),
        user_id=uuid4(),
        title="Test Playlist",
        source_type=SourceType.YOUTUBE,
        source_url="https://www.youtube.com/playlist?list=PL123",
        status=PlaylistStatus.ACTIVE,
    )
    
    created_playlist, videos = await service.import_playlist("user123", "https://www.youtube.com/playlist?list=PL123")
    
    # Verify URL validation
    url_parser.is_playlist_url.assert_called_once_with("https://www.youtube.com/playlist?list=PL123")
    url_parser.parse_playlist_url.assert_called_once_with("https://www.youtube.com/playlist?list=PL123")
    
    # Verify YouTube API calls
    service.youtube_client.fetch_playlist_metadata.assert_called_once_with("PL123")
    service.youtube_client.fetch_playlist_items.assert_called_once_with("PL123")
    
    # Verify playlist creation
    playlist_repo.create.assert_awaited_once()
    
    # Verify video creation
    assert len(videos) == 2
    assert video_repo.bulk_create.await_count == 1
