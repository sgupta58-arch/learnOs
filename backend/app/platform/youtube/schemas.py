"""Pydantic schemas for YouTube API data structures."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class YouTubePlaylistMetadata(BaseModel):
    """Schema for YouTube playlist metadata.
    
    Why this schema exists: To define the structure of data retrieved from YouTube's
    playlist API, providing type safety and validation for playlist information.
    
    Why it belongs to the schemas layer: This is a data transfer object that represents
    YouTube API response data, separate from our domain models.
    
    How future Transcript Generation will use it: Will contain playlist metadata
    needed to identify videos for transcript generation.
    
    How future AI Tutor will use it: Will contain playlist metadata needed to
    analyze content for AI-powered learning recommendations.
    """
    
    id: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    thumbnail_url: Optional[str] = Field(default=None, max_length=2048)
    channel_title: Optional[str] = Field(default=None, max_length=255)
    video_count: int = Field(..., ge=0)
    status: str = Field(default="public", max_length=50)


class YouTubePlaylistItem(BaseModel):
    """Schema for YouTube playlist item (video) data.
    
    Why this schema exists: To define the structure of data retrieved from YouTube's
    playlistItems API, providing type safety and validation for video information.
    
    Why it belongs to the schemas layer: This is a data transfer object that represents
    YouTube API response data, separate from our domain models.
    
    How future Transcript Generation will use it: Will contain video metadata
    needed to fetch transcripts for specific videos.
    
    How future AI Tutor will use it: Will contain video metadata needed to
    analyze individual videos for AI recommendations.
    """
    
    playlist_id: str = Field(..., min_length=1, max_length=64)
    video_id: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    thumbnail_url: Optional[str] = Field(default=None, max_length=2048)
    channel_title: Optional[str] = Field(default=None, max_length=255)
    duration_seconds: int = Field(default=0, ge=0)
    position: int = Field(..., ge=0)
    published_at: datetime