"""Video schemas for request and response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VideoBase(BaseModel):
    youtube_video_id: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    thumbnail_url: str | None = Field(default=None, max_length=2048)
    channel_name: str | None = Field(default=None, max_length=255)
    duration_seconds: int | None = Field(default=None, ge=0)
    position: int | None = Field(default=None, ge=0)
    published_at: datetime | None = None


class VideoCreateSchema(VideoBase):
    pass


class VideoUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    thumbnail_url: str | None = Field(default=None, max_length=2048)
    channel_name: str | None = Field(default=None, max_length=255)
    duration_seconds: int | None = Field(default=None, ge=0)
    position: int | None = Field(default=None, ge=0)
    published_at: datetime | None = None


class VideoResponseSchema(VideoBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    playlist_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
