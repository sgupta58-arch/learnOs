"""Video progress API routes.

Thin routes that delegate all business logic to VideoProgressService.
No SQL, no business logic — just request parsing, auth checks, and
response serialization.

Routes:
- PATCH  /videos/{video_id}/progress  — Update video progress
- GET    /videos/{video_id}/progress  — Get video progress
- GET    /playlists/{playlist_id}/progress — Get playlist progress summary
- GET    /users/me/progress           — Get all progress for current user
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies.video_progress import get_video_progress_service
from app.schemas.progress import (
    ProgressResponseSchema,
    ProgressSummarySchema,
    ProgressUpdateSchema,
)
from app.services.video_progress import VideoProgressService

router = APIRouter(tags=["progress"])


def _get_current_user_id(request: Request) -> UUID:
    """Extract the current user ID from the request.

    TODO: Replace with proper auth dependency once auth is wired.
    Current implementation:
    - In production/staging: placeholder until auth is implemented.
    - In testing: the test can override this dependency.

    Returns:
        UUID: The authenticated user's ID.
    """
    # Allow dependency override for testing
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return UUID(user_id)
    return UUID("00000000-0000-0000-0000-000000000001")


@router.patch(
    "/videos/{video_id}/progress",
    response_model=ProgressResponseSchema,
    summary="Update video progress",
    description=(
        "Update the current user's progress for a specific video. "
        "Auto-creates a progress record if none exists. "
        "Business rules (watch_time cannot decrease, status transitions) "
        "are enforced by the service layer."
    ),
)
async def update_video_progress(
    video_id: UUID,
    payload: ProgressUpdateSchema,
    service: VideoProgressService = Depends(get_video_progress_service),
    user_id: UUID = Depends(_get_current_user_id),
) -> ProgressResponseSchema:
    """Update the authenticated user's progress for a video."""
    try:
        return await service.update_progress(
            user_id=user_id,
            video_id=video_id,
            payload=payload,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/videos/{video_id}/progress",
    response_model=ProgressResponseSchema,
    summary="Get video progress",
    description=(
        "Get the current user's progress for a specific video. "
        "Returns 404 if no progress record exists."
    ),
)
async def get_video_progress(
    video_id: UUID,
    service: VideoProgressService = Depends(get_video_progress_service),
    user_id: UUID = Depends(_get_current_user_id),
) -> ProgressResponseSchema:
    """Get the authenticated user's progress for a video."""
    try:
        return await service.get_progress(
            user_id=user_id,
            video_id=video_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/playlists/{playlist_id}/progress",
    response_model=ProgressSummarySchema,
    summary="Get playlist progress summary",
    description=(
        "Get an aggregated progress summary for a playlist. "
        "Returns completion counts, watch time, and estimated remaining time. "
        "This is NOT analytics — it returns raw computed summaries."
    ),
)
async def get_playlist_progress(
    playlist_id: UUID,
    service: VideoProgressService = Depends(get_video_progress_service),
    user_id: UUID = Depends(_get_current_user_id),
) -> ProgressSummarySchema:
    """Get aggregated progress for a playlist."""
    try:
        return await service.get_playlist_progress(
            user_id=user_id,
            playlist_id=playlist_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/users/me/progress",
    response_model=list[ProgressResponseSchema],
    summary="Get all user progress",
    description=(
        "Get all progress records for the current user. "
        "Returns progress across all videos in all playlists."
    ),
)
async def get_user_progress(
    service: VideoProgressService = Depends(get_video_progress_service),
    user_id: UUID = Depends(_get_current_user_id),
) -> list[ProgressResponseSchema]:
    """Get all progress records for the authenticated user."""
    try:
        return await service.get_user_progress(user_id=user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc