"""Enums for the LearnOS domain models."""

from enum import Enum


class PlaylistStatus(str, Enum):
    """Playlist lifecycle statuses.
    
    States:
    - ACTIVE: Playlist is currently being used
    - COMPLETED: User finished all content in the playlist
    - ARCHIVED: Playlist is archived but not deleted (soft delete)
    - PAUSED: Playlist is paused temporarily
    """

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    PAUSED = "paused"


class SourceType(str, Enum):
    """Content source types for playlists.
    
    Types:
    - YOUTUBE: YouTube playlist
    - PDF: PDF document collection
    - DOCUMENTATION: API or technical documentation
    - BLOG: Blog post collection
    - OTHER: Other content types
    """

    YOUTUBE = "youtube"
    PDF = "pdf"
    DOCUMENTATION = "documentation"
    BLOG = "blog"
    OTHER = "other"


class VideoProgressStatus(str, Enum):
    """Video progress lifecycle statuses.
    
    States:
    - NOT_STARTED: User has not watched the video
    - IN_PROGRESS: User has started watching but not finished
    - COMPLETED: User has finished watching the video
    """

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"