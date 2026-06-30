"""YouTube playlist import orchestration and parsing helpers."""

from __future__ import annotations

from typing import Tuple

from app.models.enums import PlaylistStatus, SourceType
from app.models.playlist import Playlist
from app.models.video import Video
from app.platform.youtube.client import YouTubeClient
from app.platform.youtube.parser import YouTubeURLParser
from app.platform.youtube.schemas import YouTubePlaylistItem, YouTubePlaylistMetadata
from app.repositories.playlist import PlaylistRepository
from app.repositories.video import VideoRepository


class YouTubePlaylistImportService:
    """Orchestrate importing a YouTube playlist into local playlist/video records.
    
    Why this service exists: To coordinate the entire import process from URL validation
    through YouTube API interaction to local database storage. This service acts as the
    facade for the import functionality, keeping the API routes thin and focused.
    
    Why it belongs to the services layer: This is the business logic layer that orchestrates
    the import process, validating inputs, calling platform clients, and persisting data.
    
    How future Transcript Generation will use it: Will orchestrate transcript generation
    for imported videos by calling the YouTube client to fetch video metadata and then
    triggering transcript generation services.
    
    How future AI Tutor will use it: Will orchestrate AI analysis of imported videos
    by calling the YouTube client to fetch video metadata and then triggering AI
    recommendation services.
    """

    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        video_repository: VideoRepository,
        youtube_client: YouTubeClient,
        url_parser: YouTubeURLParser,
    ) -> None:
        self.playlist_repository = playlist_repository
        self.video_repository = video_repository
        self.youtube_client = youtube_client
        self.url_parser = url_parser

    async def import_playlist(self, user_id: str, url: str) -> Tuple[Playlist, list[Video]]:
        """Import a YouTube playlist from a URL.
        
        Why this method exists: To provide the main entry point for importing YouTube playlists,
        validating the URL, extracting the playlist ID, fetching data from YouTube API,
        and persisting it to the local database.
        
        How future Transcript Generation will use it: Will orchestrate transcript generation
        for all imported videos by calling the YouTube client to fetch video metadata
        and then triggering transcript generation services.
        
        How future AI Tutor will use it: Will orchestrate AI analysis of all imported videos
        by calling the YouTube client to fetch video metadata and then triggering AI
        recommendation services.
        """
        # Validate URL and extract playlist ID
        if not self.url_parser.is_playlist_url(url):
            raise ValueError("Invalid YouTube playlist URL")
        
        playlist_id, source_url = self.url_parser.parse_playlist_url(url)
        
        # Fetch playlist metadata from YouTube API
        metadata = await self.youtube_client.fetch_playlist_metadata(playlist_id)
        
        # Create local playlist record
        playlist = Playlist(
            user_id=user_id,
            title=metadata.title,
            source_type=SourceType.YOUTUBE,
            source_url=source_url,
            status=PlaylistStatus.ACTIVE,
        )
        created_playlist = await self.playlist_repository.create(playlist)
        
        # Fetch playlist items from YouTube API
        youtube_items = await self.youtube_client.fetch_playlist_items(playlist_id)
        
        # Convert YouTube items to local Video models
        videos = []
        for item in youtube_items:
            video = Video(
                playlist_id=created_playlist.id,
                youtube_video_id=item.video_id,
                title=item.title,
                description=item.description,
                thumbnail_url=item.thumbnail_url,
                channel_name=item.channel_title,
                duration_seconds=item.duration_seconds,
                position=item.position,
                published_at=item.published_at,
            )
            videos.append(video)
        
        # Bulk insert videos
        await self.video_repository.bulk_create(videos)
        
        return created_playlist, videos

    @staticmethod
    def parse_playlist_id(url: str) -> str:
        """Parse a YouTube playlist URL and extract the playlist ID.
        
        Why this method exists: To provide a simple interface for extracting playlist IDs
        from URLs, used by external callers who need the playlist ID directly.
        
        How future Transcript Generation will use it: Will extract playlist IDs
        to identify videos that need transcript generation.
        
        How future AI Tutor will use it: Will extract playlist IDs to analyze
        content for AI-powered learning recommendations.
        """
        return YouTubeURLParser.parse_playlist_url(url)[0]

    @staticmethod
    def parse_video_id(url: str) -> str:
        """Parse a YouTube video URL and extract the video ID.
        
        Why this method exists: To provide a simple interface for extracting video IDs
        from URLs, used by external callers who need the video ID directly.
        
        How future Transcript Generation will use it: Will extract video IDs
        to fetch transcripts for specific videos.
        
        How future AI Tutor will use it: Will extract video IDs to analyze
        individual videos for AI recommendations.
        """
        return YouTubeURLParser.parse_video_url(url)[0]
