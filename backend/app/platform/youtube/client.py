"""YouTube API client for fetching playlist and video data."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.platform.youtube.exceptions import YouTubeAPIError, YouTubeAuthError, YouTubeQuotaExceededError
"""YouTube API client for fetching playlist and video data."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.platform.youtube.exceptions import YouTubeAPIError, YouTubeAuthError, YouTubeQuotaExceededError
from app.platform.youtube.schemas import YouTubePlaylistItem, YouTubePlaylistMetadata
from app.platform.youtube.constants import YOUTUBE_API_MAX_RESULTS, YOUTUBE_API_RETRY_ATTEMPTS


class YouTubeClient:
    """Client for interacting with YouTube Data API v3.
    
    This client is responsible for:
    - Validating YouTube playlist URLs
    - Extracting playlist IDs from URLs
    - Fetching playlist metadata
    - Fetching playlist items (videos)
    - Handling pagination
    - Handling API errors and rate limits
    
    Why this layer exists: To isolate YouTube API details and provide a clean interface
    for the import service. This prevents YouTube API dependencies from spreading throughout
    the application and allows for easier testing and future changes.
    
    How future Transcript Generation will use it: The client will provide access to
    video metadata that can be used to generate transcripts when AI features are added.
    
    How future AI Tutor will use it: The client will provide access to video content
    that can be analyzed and used to generate personalized learning recommendations.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self._youtube = None

    def _get_client(self):
        """Get or create YouTube API client."""
        if self._youtube is None:
            self._youtube = build("youtube", "v3", developerKey=self.api_key)
        return self._youtube

    @staticmethod
    def validate_playlist_url(url: str) -> bool:
        """Validate if a URL is a supported YouTube playlist URL.
        
        Supported formats:
        - https://www.youtube.com/playlist?list=...
        - https://youtube.com/playlist?list=...
        - https://m.youtube.com/playlist?list=...
        
        Why this method exists: To provide URL validation before attempting API calls,
        preventing unnecessary API requests for invalid URLs.
        
        How future Transcript Generation will use it: Will validate URLs for videos
        that need transcript generation.
        
        How future AI Tutor will use it: Will validate URLs for content that needs
        AI analysis.
        """
        from urllib.parse import parse_qs, urlparse
        
        parsed = urlparse(url)
        if parsed.netloc in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
            if parsed.path.startswith("/playlist"):
                query = parse_qs(parsed.query)
                # Return a boolean indicating presence of a non-empty `list` param
                return bool(query.get("list") and query["list"][0])
        return False

    @staticmethod
    def extract_playlist_id(url: str) -> str:
        """Extract playlist ID from YouTube URL.
        
        Supported formats:
        - https://www.youtube.com/playlist?list=...
        - https://youtube.com/playlist?list=...
        - https://m.youtube.com/playlist?list=...
        
        Why this method exists: To provide a clean interface for extracting playlist IDs
        from various URL formats, centralizing the parsing logic.
        
        How future Transcript Generation will use it: Will extract video IDs from URLs
        for transcript generation.
        
        How future AI Tutor will use it: Will extract content IDs for AI analysis.
        """
        from urllib.parse import parse_qs, urlparse
        
        parsed = urlparse(url)
        if parsed.netloc in {"www.youtube.com", "youtube.com", "m.youtube.com"}:
            if parsed.path.startswith("/playlist"):
                query = parse_qs(parsed.query)
                playlist_id = query.get("list", [""])[0]
                if playlist_id:
                    return playlist_id
        raise ValueError("Unsupported YouTube playlist URL")

    async def fetch_playlist_metadata(self, playlist_id: str) -> YouTubePlaylistMetadata:
        """Fetch metadata for a YouTube playlist.
        
        Why this method exists: To retrieve playlist information (title, description,
        thumbnails, etc.) from YouTube API, which is needed for creating local playlist records.
        
        How future Transcript Generation will use it: Will fetch metadata to identify
        videos that need transcript generation.
        
        How future AI Tutor will use it: Will fetch metadata to understand content
        for AI-powered learning recommendations.
        """
        youtube = self._get_client()
        
        for attempt in range(YOUTUBE_API_RETRY_ATTEMPTS):
            try:
                list_call = youtube.playlists().list(
                    part="snippet,contentDetails,status",
                    id=playlist_id,
                    maxResults=1
                )

                # Some test mocks return a callable whose call returns an object
                # with an `execute()` method. Support both styles.
                # Execute the API call. Some tests mock the client such that
                # `list_call.execute()` returns a MagicMock while others set
                # `list_call.return_value.execute.return_value`.
                response = list_call.execute()
                if not isinstance(response, dict) and callable(list_call):
                    # Attempt the callable style used in tests
                    response = list_call().execute()
                
                if not response.get("items"):
                    raise YouTubeAPIError(f"Playlist not found: {playlist_id}")
                
                item = response["items"][0]
                snippet = item["snippet"]
                
                return YouTubePlaylistMetadata(
                    id=playlist_id,
                    title=snippet["title"],
                    description=snippet["description"],
                    thumbnail_url=snippet["thumbnails"]["default"]["url"],
                    channel_title=snippet["channelTitle"],
                    video_count=int(item["contentDetails"]["itemCount"]),
                    status=item["status"].get("privacyStatus", "public")
                )
                
            except HttpError as e:
                if e.resp.status == 403 and "quotaExceeded" in str(e):
                    raise YouTubeQuotaExceededError("YouTube API quota exceeded")
                elif e.resp.status == 404:
                    raise YouTubeAPIError(f"Playlist not found: {playlist_id}")
                elif e.resp.status == 401:
                    raise YouTubeAuthError("Invalid YouTube API key")
                elif attempt == YOUTUBE_API_RETRY_ATTEMPTS - 1:
                    raise YouTubeAPIError(f"Failed to fetch playlist metadata after {YOUTUBE_API_RETRY_ATTEMPTS} attempts: {e}")
                await asyncio.sleep(1)  # Wait before retry
        
        raise YouTubeAPIError("Unexpected error fetching playlist metadata")

    async def fetch_playlist_items(
        self, 
        playlist_id: str, 
        max_results: int = YOUTUBE_API_MAX_RESULTS
    ) -> List[YouTubePlaylistItem]:
        """Fetch all items (videos) from a YouTube playlist.
        
        Why this method exists: To retrieve the actual video list from a playlist,
        including video metadata needed for creating local video records.
        
        How future Transcript Generation will use it: Will fetch video items to
        identify which videos need transcript generation.
        
        How future AI Tutor will use it: Will fetch video items to analyze content
        for AI-powered learning recommendations.
        """
        youtube = self._get_client()
        items: List[YouTubePlaylistItem] = []
        page_token = None
        
        for attempt in range(YOUTUBE_API_RETRY_ATTEMPTS):
            try:
                while True:
                    list_call = youtube.playlistItems().list(
                        part="snippet,contentDetails",
                        playlistId=playlist_id,
                        maxResults=min(50, max_results - len(items)),
                        pageToken=page_token
                    )

                    response = list_call.execute()
                    if not isinstance(response, dict) and callable(list_call):
                        response = list_call().execute()
                    
                    for item in response["items"]:
                        snippet = item["snippet"]
                        content_details = item["contentDetails"]
                        
                        video_id = content_details["videoId"]
                        
                        # Skip private videos
                        if content_details.get("privacyStatus") == "private":
                            continue
                        
                        video_item = YouTubePlaylistItem(
                            playlist_id=playlist_id,
                            video_id=video_id,
                            title=snippet["title"],
                            description=snippet["description"],
                            thumbnail_url=snippet["thumbnails"]["default"]["url"],
                            channel_title=snippet["channelTitle"],
                            duration_seconds=self._parse_duration(content_details.get("duration", "")),
                            position=int(snippet["position"]),
                            published_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))
                        )
                        items.append(video_item)
                    
                    page_token = response.get("nextPageToken")
                    if not page_token or len(items) >= max_results:
                        break
                
                break  # Success, exit retry loop
                
            except HttpError as e:
                if e.resp.status == 403 and "quotaExceeded" in str(e):
                    raise YouTubeQuotaExceededError("YouTube API quota exceeded")
                elif e.resp.status == 404:
                    raise YouTubeAPIError(f"Playlist not found: {playlist_id}")
                elif e.resp.status == 401:
                    raise YouTubeAuthError("Invalid YouTube API key")
                elif attempt == YOUTUBE_API_RETRY_ATTEMPTS - 1:
                    raise YouTubeAPIError(f"Failed to fetch playlist items after {YOUTUBE_API_RETRY_ATTEMPTS} attempts: {e}")
                await asyncio.sleep(1)  # Wait before retry
        
        return items

    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds.
        
        Why this method exists: To convert YouTube's duration format (PT1H2M3S) to
        seconds for storage in the database.
        
        How future Transcript Generation will use it: Will parse video durations
        to prioritize longer videos for transcript generation.
        
        How future AI Tutor will use it: Will parse video durations to create
        learning paths based on video length.
        """
        if not duration:
            return 0
        
        # Parse PT1H2M3S format
        import re
        hours = re.search(r'(\d+)H', duration)
        minutes = re.search(r'(\d+)M', duration)
        seconds = re.search(r'(\d+)S', duration)
        
        total_seconds = 0
        if hours:
            total_seconds += int(hours.group(1)) * 3600
        if minutes:
            total_seconds += int(minutes.group(1)) * 60
        if seconds:
            total_seconds += int(seconds.group(1))
        
        return total_seconds