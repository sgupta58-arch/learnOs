from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.database.session import get_db
from app.dependencies.playlist import get_playlist_repository
from app.dependencies.video import get_video_repository
from app.platform.youtube.client import YouTubeClient
from app.platform.youtube.parser import YouTubeURLParser
from app.repositories.playlist import PlaylistRepository
from app.repositories.video import VideoRepository
from app.services.youtube_import import YouTubePlaylistImportService


def get_youtube_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> YouTubeClient:
    """Provide a YouTubeClient with API key from configuration.
    
    Why this function exists: To inject the YouTube API client as a dependency,
    ensuring that API credentials are managed centrally through configuration.
    
    How future Transcript Generation will use it: Will use the client to fetch
    video metadata for transcript generation.
    
    How future AI Tutor will use it: Will use the client to fetch video metadata
    for AI-powered learning recommendations.
    """
    if not settings.YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY not configured in environment variables")
    return YouTubeClient(api_key=str(settings.YOUTUBE_API_KEY.get_secret_value()))


def get_url_parser() -> YouTubeURLParser:
    """Provide a YouTubeURLParser instance.
    
    Why this function exists: To provide a URL parser as a dependency for consistent
    URL handling throughout the application.
    
    How future Transcript Generation will use it: Will parse video URLs for
    transcript generation.
    
    How future AI Tutor will use it: Will parse video URLs for AI analysis.
    """
    return YouTubeURLParser()


async def get_youtube_import_service(
    playlist_repository: Annotated[PlaylistRepository, Depends(get_playlist_repository)],
    video_repository: Annotated[VideoRepository, Depends(get_video_repository)],
    youtube_client: Annotated[YouTubeClient, Depends(get_youtube_client)],
    url_parser: Annotated[YouTubeURLParser, Depends(get_url_parser)],
) -> YouTubePlaylistImportService:
    """Provide a YouTubePlaylistImportService with all dependencies injected.
    
    Why this function exists: To orchestrate dependency injection for the import service,
    ensuring all required components are properly wired.
    
    How future Transcript Generation will use it: Will use the service to orchestrate
    transcript generation for imported videos.
    
    How future AI Tutor will use it: Will use the service to orchestrate AI analysis
    of imported videos.
    """
    return YouTubePlaylistImportService(
        playlist_repository=playlist_repository,
        video_repository=video_repository,
        youtube_client=youtube_client,
        url_parser=url_parser,
    )
