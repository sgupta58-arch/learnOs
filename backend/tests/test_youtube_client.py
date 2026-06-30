"""Tests for YouTube API client."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.platform.youtube.client import YouTubeClient
from app.platform.youtube.exceptions import (
    InvalidURLException,
    YouTubeAPIError,
    YouTubeAuthError,
    YouTubeQuotaExceededError,
)
from app.platform.youtube.schemas import YouTubePlaylistItem, YouTubePlaylistMetadata


class TestYouTubeClient:
    """Test suite for YouTubeClient."""

    @pytest.fixture
    def client(self) -> YouTubeClient:
        """Create a YouTubeClient instance for testing."""
        return YouTubeClient(api_key="test_key_123")

    def test_validate_playlist_url_valid(self, client: YouTubeClient) -> None:
        """Test validate_playlist_url with valid URL."""
        url = "https://www.youtube.com/playlist?list=PL123456789"
        assert client.validate_playlist_url(url) is True

    def test_validate_playlist_url_invalid(self, client: YouTubeClient) -> None:
        """Test validate_playlist_url with invalid URL."""
        url = "https://vimeo.com/playlist?list=123"
        assert client.validate_playlist_url(url) is False

    def test_validate_playlist_url_watch_url(self, client: YouTubeClient) -> None:
        """Test validate_playlist_url with watch URL (not playlist)."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert client.validate_playlist_url(url) is False

    def test_extract_playlist_id_success(self, client: YouTubeClient) -> None:
        """Test extract_playlist_id with valid URL."""
        url = "https://www.youtube.com/playlist?list=PL123456789"
        playlist_id = client.extract_playlist_id(url)
        assert playlist_id == "PL123456789"

    def test_extract_playlist_id_invalid_url(self, client: YouTubeClient) -> None:
        """Test extract_playlist_id with invalid URL raises exception."""
        url = "https://vimeo.com/playlist"
        
        with pytest.raises(ValueError):
            client.extract_playlist_id(url)

    def test_parse_duration_simple(self, client: YouTubeClient) -> None:
        """Test _parse_duration with simple duration."""
        duration = "PT1M30S"
        seconds = client._parse_duration(duration)
        assert seconds == 90

    def test_parse_duration_hours(self, client: YouTubeClient) -> None:
        """Test _parse_duration with hours."""
        duration = "PT1H2M3S"
        seconds = client._parse_duration(duration)
        assert seconds == 3723

    def test_parse_duration_only_seconds(self, client: YouTubeClient) -> None:
        """Test _parse_duration with only seconds."""
        duration = "PT45S"
        seconds = client._parse_duration(duration)
        assert seconds == 45

    def test_parse_duration_empty(self, client: YouTubeClient) -> None:
        """Test _parse_duration with empty string."""
        duration = ""
        seconds = client._parse_duration(duration)
        assert seconds == 0

    @pytest.mark.asyncio
    async def test_fetch_playlist_metadata_success(self, client: YouTubeClient) -> None:
        """Test fetch_playlist_metadata with successful API response."""
        # Mock the YouTube API client
        mock_youtube = MagicMock()
        mock_list_method = MagicMock()
        mock_execute_result = {
            "items": [
                {
                    "snippet": {
                        "title": "Test Playlist",
                        "description": "A test playlist",
                        "thumbnails": {"default": {"url": "https://example.com/thumb.jpg"}},
                        "channelTitle": "Test Channel",
                    },
                    "contentDetails": {"itemCount": 10},
                    "status": {"privacyStatus": "public"},
                }
            ]
        }
        mock_list_method.return_value.execute.return_value = mock_execute_result
        mock_youtube.playlists.return_value.list.return_value = mock_list_method
        
        with patch.object(client, "_get_client", return_value=mock_youtube):
            metadata = await client.fetch_playlist_metadata("PL123")
        
        assert metadata.id == "PL123"
        assert metadata.title == "Test Playlist"
        assert metadata.description == "A test playlist"
        assert metadata.video_count == 10
        assert metadata.status == "public"

    @pytest.mark.asyncio
    async def test_fetch_playlist_metadata_not_found(self, client: YouTubeClient) -> None:
        """Test fetch_playlist_metadata when playlist is not found."""
        mock_youtube = MagicMock()
        mock_list_method = MagicMock()
        mock_list_method.return_value.execute.return_value = {"items": []}
        mock_youtube.playlists.return_value.list.return_value = mock_list_method
        
        with patch.object(client, "_get_client", return_value=mock_youtube):
            with pytest.raises(YouTubeAPIError):
                await client.fetch_playlist_metadata("PL_INVALID")

    @pytest.mark.asyncio
    async def test_fetch_playlist_items_success(self, client: YouTubeClient) -> None:
        """Test fetch_playlist_items with successful API response."""
        mock_youtube = MagicMock()
        mock_list_method = MagicMock()
        mock_execute_result = {
            "items": [
                {
                    "snippet": {
                        "title": "Video 1",
                        "description": "First video",
                        "thumbnails": {"default": {"url": "https://example.com/thumb1.jpg"}},
                        "channelTitle": "Test Channel",
                        "position": "0",
                        "publishedAt": "2023-01-01T00:00:00Z",
                    },
                    "contentDetails": {
                        "videoId": "video1",
                        "duration": "PT5M30S",
                        "privacyStatus": "public",
                    },
                }
            ],
            "nextPageToken": None,
        }
        mock_list_method.return_value.execute.return_value = mock_execute_result
        mock_youtube.playlistItems.return_value.list.return_value = mock_list_method
        
        with patch.object(client, "_get_client", return_value=mock_youtube):
            items = await client.fetch_playlist_items("PL123")
        
        assert len(items) == 1
        assert items[0].video_id == "video1"
        assert items[0].title == "Video 1"
        assert items[0].duration_seconds == 330

    @pytest.mark.asyncio
    async def test_fetch_playlist_items_skips_private_videos(self, client: YouTubeClient) -> None:
        """Test fetch_playlist_items skips private videos."""
        mock_youtube = MagicMock()
        mock_list_method = MagicMock()
        mock_execute_result = {
            "items": [
                {
                    "snippet": {
                        "title": "Public Video",
                        "description": "Public video",
                        "thumbnails": {"default": {"url": "https://example.com/thumb1.jpg"}},
                        "channelTitle": "Test Channel",
                        "position": "0",
                        "publishedAt": "2023-01-01T00:00:00Z",
                    },
                    "contentDetails": {
                        "videoId": "video1",
                        "duration": "PT5M",
                        "privacyStatus": "public",
                    },
                },
                {
                    "snippet": {
                        "title": "Private Video",
                        "description": "Private video",
                        "thumbnails": {"default": {"url": "https://example.com/thumb2.jpg"}},
                        "channelTitle": "Test Channel",
                        "position": "1",
                        "publishedAt": "2023-01-02T00:00:00Z",
                    },
                    "contentDetails": {
                        "videoId": "video2",
                        "duration": "PT5M",
                        "privacyStatus": "private",
                    },
                },
            ],
            "nextPageToken": None,
        }
        mock_list_method.return_value.execute.return_value = mock_execute_result
        mock_youtube.playlistItems.return_value.list.return_value = mock_list_method
        
        with patch.object(client, "_get_client", return_value=mock_youtube):
            items = await client.fetch_playlist_items("PL123")
        
        # Only public video should be included
        assert len(items) == 1
        assert items[0].video_id == "video1"