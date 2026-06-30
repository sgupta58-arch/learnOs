from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.video import get_video_service
from app.models.video import Video
from app.schemas.video import VideoCreateSchema, VideoResponseSchema, VideoUpdateSchema
from app.services.video import VideoService

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("", response_model=VideoResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_video(
    playlist_id: UUID,
    payload: VideoCreateSchema,
    service: VideoService = Depends(get_video_service),
) -> Video:
    try:
        video = await service.create(playlist_id=playlist_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return video


@router.get("", response_model=list[VideoResponseSchema])
async def list_videos(
    playlist_id: UUID,
    service: VideoService = Depends(get_video_service),
) -> list[Video]:
    return await service.list_by_playlist(playlist_id)


@router.patch("/{video_id}", response_model=VideoResponseSchema)
async def update_video(
    video_id: UUID,
    payload: VideoUpdateSchema,
    service: VideoService = Depends(get_video_service),
) -> Video:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
