"""Repository layer for video persistence.

Why this repository exists: To provide database access for Video entities, implementing
CRUD operations and playlist-specific queries. This layer isolates database operations
from business logic, following the Clean Architecture principle.

Why it belongs to the repositories layer: This is the data access layer that handles
persistence of Video records, communicating directly with the database through SQLAlchemy.

How future Transcript Generation will use it: Will query videos by playlist to
identify videos needing transcript generation, and will update transcript metadata
once generated.

How future AI Tutor will use it: Will query videos by playlist to analyze content
for AI-powered learning recommendations, and will update AI analysis metadata.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video import Video
from app.repositories.base import BaseRepository


class VideoRepository(BaseRepository[Video]):
    """Persistence operations for Video records.
    
    Why this class exists: To provide video-specific database operations beyond the
    generic CRUD operations provided by BaseRepository, including playlist-based queries
    and bulk operations.
    
    Why it belongs to the repositories layer: This is the data access layer that handles
    video persistence, implementing repository-specific methods for video operations.
    
    How future Transcript Generation will use it: Will query videos by playlist to
    identify videos needing transcript generation, and will bulk update transcript metadata.
    
    How future AI Tutor will use it: Will query videos by playlist to analyze content
    for AI-powered learning recommendations, and will bulk update AI analysis metadata.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Video)

    async def list_by_playlist(self, playlist_id: UUID) -> Sequence[Video]:
        """Retrieve all videos for a specific playlist.
        
        Why this method exists: To provide a convenient way to fetch all videos
        belonging to a playlist, ordered by position and creation time.
        
        How future Transcript Generation will use it: Will fetch videos by playlist
        to identify which videos need transcript generation.
        
        How future AI Tutor will use it: Will fetch videos by playlist to analyze
        content for AI-powered learning recommendations.
        """
        result = await self.session.execute(
            select(Video).where(Video.playlist_id == playlist_id).order_by(Video.position.asc().nulls_last(), Video.created_at.asc())
        )
        return result.scalars().all()

    async def bulk_create(self, entities: list[Video]) -> list[Video]:
        """Bulk insert multiple video entities.
        
        Why this method exists: To efficiently insert multiple videos at once,
        which is needed when importing entire playlists from YouTube.
        
        How future Transcript Generation will use it: Will bulk insert videos
        when importing playlists for transcript generation.
        
        How future AI Tutor will use it: Will bulk insert videos when importing
        playlists for AI analysis.
        """
        self.session.add_all(entities)
        await self.session.flush()
        for entity in entities:
            await self.session.refresh(entity)
        return entities

    async def get_by_playlist(self, playlist_id: UUID) -> Sequence[Video]:
        """Alias for list_by_playlist for consistency with other repositories.
        
        Why this method exists: To provide a consistent interface across repositories,
        where some repositories use get_by_* and others use list_by_*.
        
        How future Transcript Generation will use it: Will fetch videos by playlist
        to identify videos needing transcript generation.
        
        How future AI Tutor will use it: Will fetch videos by playlist to analyze
        content for AI-powered learning recommendations.
        """
        return await self.list_by_playlist(playlist_id)

    async def delete(self, entity: Video) -> None:
        """Permanently delete a video from the database.
        
        Why this method exists: To provide a hard delete operation for videos,
        which may be needed for administrative purposes or data cleanup.
        
        How future Transcript Generation will use it: Will delete videos
        when removing content that doesn't need transcript generation.
        
        How future AI Tutor will use it: Will delete videos when removing
        content that doesn't need AI analysis.
        """
        await self.hard_delete(entity)

    async def exists(self, entity_id: UUID) -> bool:
        """Check if a video exists by ID.
        
        Why this method exists: To provide a simple existence check for videos,
        which is useful for validation and business logic.
        
        How future Transcript Generation will use it: Will check if videos
        exist before attempting transcript generation.
        
        How future AI Tutor will use it: Will check if videos exist before
        performing AI analysis.
        """
        return await self.get_by_id(entity_id) is not None
