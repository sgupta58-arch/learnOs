"""Dependency factories for video-related components."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.video import VideoRepository
from app.services.video import VideoService


def get_video_repository(session: AsyncSession = Depends(get_db)) -> VideoRepository:
    return VideoRepository(session)


def get_video_service(
    repository: VideoRepository = Depends(get_video_repository),
) -> VideoService:
    return VideoService(repository)
