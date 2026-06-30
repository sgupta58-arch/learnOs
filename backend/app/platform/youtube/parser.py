"""URL parsing utilities for YouTube content."""

from urllib.parse import parse_qs, urlparse
from typing import Tuple

from app.platform.youtube.exceptions import InvalidURLException


class YouTubeURLParser:
    """Parser for YouTube URLs to extract IDs and validate formats.
    
    This parser handles:
    - Playlist URLs: https://www.youtube.com/playlist?list=...
    - Video URLs: https://www.youtube.com/watch?v=...
    - Short URLs: https://youtu.be/...
    
    Why this layer exists: To centralize URL parsing logic and provide a clean interface
    for extracting IDs from various YouTube URL formats. This prevents URL parsing
    logic from spreading throughout the application.
    
    How future Transcript Generation will use it: Will parse video URLs to extract
    video IDs for transcript generation.
    
    How future AI Tutor will use it: Will parse content URLs to extract IDs for
    AI analysis and recommendations.
    """

    @staticmethod
    def parse_playlist_url(url: str) -> Tuple[str, str]:
        """Parse a YouTube playlist URL and extract playlist ID.
        
        Args:
            url: YouTube playlist URL
            
        Returns:
            Tuple of (playlist_id, source_url)
            
        Raises:
            InvalidURLException: If URL is not a valid YouTube playlist URL
            
        Why this method exists: To provide a robust way to extract playlist IDs
        from various URL formats, ensuring we only process valid playlist URLs.
        
        How future Transcript Generation will use it: Will extract playlist IDs
        to identify videos that need transcript generation.
        
        How future AI Tutor will use it: Will extract playlist IDs to analyze
        content for AI-powered learning recommendations.
        """
        parsed = urlparse(url)
        
        # Validate URL format
        if parsed.netloc not in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
            raise InvalidURLException(f"Unsupported YouTube domain: {parsed.netloc}")
        
        if not parsed.path.startswith("/playlist"):
            raise InvalidURLException(f"URL path is not a playlist: {parsed.path}")
        
        query = parse_qs(parsed.query)
        if "list" not in query or not query["list"][0]:
            raise InvalidURLException("Playlist ID not found in URL query parameters")
        
        playlist_id = query["list"][0]
        
        # Reconstruct the canonical URL
        source_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        
        return playlist_id, source_url

    @staticmethod
    def parse_video_url(url: str) -> Tuple[str, str]:
        """Parse a YouTube video URL and extract video ID.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Tuple of (video_id, source_url)
            
        Raises:
            InvalidURLException: If URL is not a valid YouTube video URL
            
        Why this method exists: To provide a robust way to extract video IDs
        from various URL formats, ensuring we only process valid video URLs.
        
        How future Transcript Generation will use it: Will extract video IDs
        to fetch transcripts for specific videos.
        
        How future AI Tutor will use it: Will extract video IDs to analyze
        individual videos for AI recommendations.
        """
        parsed = urlparse(url)
        
        # Validate URL format
        if parsed.netloc not in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
            if parsed.netloc != "youtu.be":
                raise InvalidURLException(f"Unsupported YouTube domain: {parsed.netloc}")
        
        query = parse_qs(parsed.query)
        video_id = None
        source_url = None
        
        if parsed.netloc in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
            if parsed.path.startswith("/watch"):
                if "v" not in query or not query["v"][0]:
                    raise InvalidURLException("Video ID not found in URL query parameters")
                video_id = query["v"][0]
                source_url = f"https://www.youtube.com/watch?v={video_id}"
        elif parsed.netloc == "youtu.be":
            path = parsed.path.lstrip("/")
            if not path:
                raise InvalidURLException("Video ID not found in URL path")
            video_id = path
            source_url = f"https://youtu.be/{video_id}"
        
        if not video_id:
            raise InvalidURLException("Unsupported YouTube video URL format")
        
        return video_id, source_url

    @staticmethod
    def is_playlist_url(url: str) -> bool:
        """Check if a URL is a YouTube playlist URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is a valid YouTube playlist URL, False otherwise
            
        Why this method exists: To provide a quick validation check before
        attempting to parse a URL as a playlist.
        
        How future Transcript Generation will use it: Will quickly identify
        playlist URLs to batch process transcript generation.
        
        How future AI Tutor will use it: Will quickly identify playlist URLs
        to analyze entire playlists for AI recommendations.
        """
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc in {"www.youtube.com", "youtube.com", "m.youtube.com"} and
                parsed.path.startswith("/playlist") and
                "list" in parse_qs(parsed.query)
            )
        except Exception:
            return False

    @staticmethod
    def is_video_url(url: str) -> bool:
        """Check if a URL is a YouTube video URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is a valid YouTube video URL, False otherwise
            
        Why this method exists: To provide a quick validation check before
        attempting to parse a URL as a video.
        
        How future Transcript Generation will use it: Will quickly identify
        video URLs to fetch transcripts for specific videos.
        
        How future AI Tutor will use it: Will quickly identify video URLs
        to analyze individual videos for AI recommendations.
        """
        try:
            parsed = urlparse(url)
            if parsed.netloc in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
                return parsed.path.startswith("/watch") and "v" in parse_qs(parsed.query)
            elif parsed.netloc == "youtu.be":
                return bool(parsed.path.lstrip("/"))
            return False
        except Exception:
            return False