from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.security import TokenPayload
from app.dependencies.auth import get_current_user_token
from app.dependencies.playlist import get_playlist_service
from app.dependencies.youtube_import import get_youtube_import_service
from app.schemas.common import success_response
from app.schemas.playlist import PlaylistCreateSchema, PlaylistUpdateSchema
from app.services.playlist import PlaylistService
from app.services.youtube_import import YouTubePlaylistImportService

router = APIRouter(prefix="/playlists", tags=["playlists"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_playlist(
    data: PlaylistCreateSchema,
    token_payload: TokenPayload = Depends(get_current_user_token),
    service: PlaylistService = Depends(get_playlist_service),
):
    """Create a new playlist belonging to the current user."""
    user_id = UUID(token_payload.sub)
    playlist = await service.create_playlist(user_id, data)
    return success_response(data=playlist.model_dump(), message="Playlist created")


@router.get("")
async def list_playlists(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    token_payload: TokenPayload = Depends(get_current_user_token),
    service: PlaylistService = Depends(get_playlist_service),
):
    """List playlists for the current user."""
    user_id = UUID(token_payload.sub)
    result = await service.list_playlists(user_id=user_id, skip=skip, limit=limit)
    return success_response(data=result.model_dump(), message="Playlists retrieved")


@router.get("/{playlist_id}")
async def get_playlist(
    playlist_id: UUID,
    token_payload: TokenPayload = Depends(get_current_user_token),
    service: PlaylistService = Depends(get_playlist_service),
):
    user_id = UUID(token_payload.sub)
    playlist = await service.get_playlist(user_id=user_id, playlist_id=playlist_id)
    return success_response(data=playlist.model_dump(), message="Playlist retrieved")


@router.patch("/{playlist_id}")
async def update_playlist(
    playlist_id: UUID,
    data: PlaylistUpdateSchema,
    token_payload: TokenPayload = Depends(get_current_user_token),
    service: PlaylistService = Depends(get_playlist_service),
):
    user_id = UUID(token_payload.sub)
    playlist = await service.update_playlist(user_id=user_id, playlist_id=playlist_id, data=data)
    return success_response(data=playlist.model_dump(), message="Playlist updated")


@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: UUID,
    token_payload: TokenPayload = Depends(get_current_user_token),
    service: PlaylistService = Depends(get_playlist_service),
):
    user_id = UUID(token_payload.sub)
    playlist = await service.delete_playlist(user_id=user_id, playlist_id=playlist_id)
    return success_response(data=playlist.model_dump(), message="Playlist deleted")


@router.post("/import/youtube", status_code=status.HTTP_201_CREATED)
async def import_youtube_playlist(
    source_url: str,
    token_payload: TokenPayload = Depends(get_current_user_token),
    service: YouTubePlaylistImportService = Depends(get_youtube_import_service),
):
    """Import a YouTube playlist from a URL.
    
    This route:
    1. Validates the YouTube URL
    2. Extracts the playlist ID
    3. Fetches metadata from YouTube API
    4. Creates a local playlist record
    5. Fetches all videos from the playlist
    6. Bulk inserts videos into the database
    
    Why this route is thin: All business logic is delegated to YouTubePlaylistImportService.
    This route only handles HTTP concerns: authentication, parsing the request,
    and formatting the response.
    
    How future Transcript Generation will use it: Will trigger transcript generation
    for all imported videos.
    
    How future AI Tutor will use it: Will trigger AI analysis for all imported videos.
    """
    user_id = UUID(token_payload.sub)
    playlist, videos = await service.import_playlist(user_id=user_id, url=source_url)
    return success_response(
        data={
            "playlist_id": str(playlist.id),
            "title": playlist.title,
            "videos_imported": len(videos),
        },
        message="YouTube playlist imported successfully",
    )
