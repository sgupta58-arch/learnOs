"""Dependency factories for video progress components.

Why this file exists: Provides dependency injection for VideoProgressRepository
and VideoProgressService following the same pattern as other dependency files
(e.g., video.py, playlist.py). This maintains consistent DI throughout the
application.

How future phases will use it: Any future component that needs progress data
(such as Learning Sessions, AI Tutor, Analytics) will inject VideoProgressService
through these same dependency factories.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.video import VideoRepository
from app.repositories.video_progress import VideoProgressRepository
from app.services.video_progress import VideoProgressService


def get_video_progress_repository(
    session: AsyncSession = Depends(get_db),
) -> VideoProgressRepository:
    """Provide a VideoProgressRepository instance.

    Why this factory exists: Creates a repository with the current request's
    database session, following the unit-of-work pattern.
    """
    return VideoProgressRepository(session)


def get_video_progress_service(
    repository: VideoProgressRepository = Depends(get_video_progress_repository),
) -> VideoProgressService:
    """Provide a VideoProgressService instance.

    Why this factory exists: Creates a service with its required repository
    dependencies injected automatically. Both VideoProgressRepository and
    VideoRepository are wired to the same database session.
    """
    video_repository = VideoRepository(repository.session)
    return VideoProgressService(
        repository=repository,
        video_repository=video_repository,
    )