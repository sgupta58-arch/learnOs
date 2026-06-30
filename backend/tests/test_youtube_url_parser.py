"""Tests for YouTube URL parser."""

import pytest

from app.platform.youtube.exceptions import InvalidURLException
from app.platform.youtube.parser import YouTubeURLParser


class TestYouTubeURLParser:
    """Test suite for YouTubeURLParser."""

    def test_parse_playlist_url_standard_format(self) -> None:
        """Test parsing standard YouTube playlist URL."""
        url = "https://www.youtube.com/playlist?list=PL123456789"
        playlist_id, source_url = YouTubeURLParser.parse_playlist_url(url)
        
        assert playlist_id == "PL123456789"
        assert source_url == "https://www.youtube.com/playlist?list=PL123456789"

    def test_parse_playlist_url_alternate_domain(self) -> None:
        """Test parsing YouTube playlist URL with alternate domain."""
        url = "https://youtube.com/playlist?list=PLabc123"
        playlist_id, source_url = YouTubeURLParser.parse_playlist_url(url)
        
        assert playlist_id == "PLabc123"
        assert source_url == "https://www.youtube.com/playlist?list=PLabc123"

    def test_parse_playlist_url_mobile_domain(self) -> None:
        """Test parsing YouTube playlist URL with mobile domain."""
        url = "https://m.youtube.com/playlist?list=PLtest789"
        playlist_id, source_url = YouTubeURLParser.parse_playlist_url(url)
        
        assert playlist_id == "PLtest789"
        assert source_url == "https://www.youtube.com/playlist?list=PLtest789"

    def test_parse_playlist_url_invalid_domain(self) -> None:
        """Test parsing URL with invalid domain raises exception."""
        url = "https://vimeo.com/playlist?list=123"
        
        with pytest.raises(InvalidURLException):
            YouTubeURLParser.parse_playlist_url(url)

    def test_parse_playlist_url_invalid_path(self) -> None:
        """Test parsing URL with invalid path raises exception."""
        url = "https://www.youtube.com/watch?v=123"
        
        with pytest.raises(InvalidURLException):
            YouTubeURLParser.parse_playlist_url(url)

    def test_parse_playlist_url_missing_list_param(self) -> None:
        """Test parsing URL with missing list parameter raises exception."""
        url = "https://www.youtube.com/playlist"
        
        with pytest.raises(InvalidURLException):
            YouTubeURLParser.parse_playlist_url(url)

    def test_parse_video_url_standard_format(self) -> None:
        """Test parsing standard YouTube video URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id, source_url = YouTubeURLParser.parse_video_url(url)
        
        assert video_id == "dQw4w9WgXcQ"
        assert source_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_parse_video_url_short_format(self) -> None:
        """Test parsing short YouTube video URL (youtu.be)."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id, source_url = YouTubeURLParser.parse_video_url(url)
        
        assert video_id == "dQw4w9WgXcQ"
        assert source_url == "https://youtu.be/dQw4w9WgXcQ"

    def test_parse_video_url_mobile_domain(self) -> None:
        """Test parsing video URL with mobile domain."""
        url = "https://m.youtube.com/watch?v=abc123def45"
        video_id, source_url = YouTubeURLParser.parse_video_url(url)
        
        assert video_id == "abc123def45"
        assert source_url == "https://www.youtube.com/watch?v=abc123def45"

    def test_parse_video_url_invalid_domain(self) -> None:
        """Test parsing video URL with invalid domain raises exception."""
        url = "https://vimeo.com/123456"
        
        with pytest.raises(InvalidURLException):
            YouTubeURLParser.parse_video_url(url)

    def test_parse_video_url_missing_video_id(self) -> None:
        """Test parsing video URL with missing video ID raises exception."""
        url = "https://www.youtube.com/watch"
        
        with pytest.raises(InvalidURLException):
            YouTubeURLParser.parse_video_url(url)

    def test_is_playlist_url_valid(self) -> None:
        """Test is_playlist_url returns True for valid playlist URL."""
        url = "https://www.youtube.com/playlist?list=PL123"
        assert YouTubeURLParser.is_playlist_url(url) is True

    def test_is_playlist_url_invalid_domain(self) -> None:
        """Test is_playlist_url returns False for invalid domain."""
        url = "https://vimeo.com/playlist?list=123"
        assert YouTubeURLParser.is_playlist_url(url) is False

    def test_is_playlist_url_missing_list_param(self) -> None:
        """Test is_playlist_url returns False for missing list parameter."""
        url = "https://www.youtube.com/playlist"
        assert YouTubeURLParser.is_playlist_url(url) is False

    def test_is_video_url_valid_standard_format(self) -> None:
        """Test is_video_url returns True for valid video URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert YouTubeURLParser.is_video_url(url) is True

    def test_is_video_url_valid_short_format(self) -> None:
        """Test is_video_url returns True for valid short video URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert YouTubeURLParser.is_video_url(url) is True

    def test_is_video_url_invalid_domain(self) -> None:
        """Test is_video_url returns False for invalid domain."""
        url = "https://vimeo.com/123456"
        assert YouTubeURLParser.is_video_url(url) is False

    def test_is_video_url_missing_video_id(self) -> None:
        """Test is_video_url returns False for missing video ID."""
        url = "https://www.youtube.com/watch"
        assert YouTubeURLParser.is_video_url(url) is False