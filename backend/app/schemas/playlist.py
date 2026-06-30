from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PlaylistStatus, SourceType


class PlaylistCreateSchema(BaseModel):
    """Schema for creating a playlist."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    source_type: SourceType = Field(default=SourceType.OTHER)
    source_url: str | None = Field(default=None, max_length=2048)
    thumbnail_url: str | None = Field(default=None, max_length=2048)
    target_completion_date: datetime | None = None


class PlaylistUpdateSchema(BaseModel):
    """Schema for updating a playlist. All fields optional."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    source_type: SourceType | None = None
    source_url: str | None = Field(default=None, max_length=2048)
    thumbnail_url: str | None = Field(default=None, max_length=2048)
    target_completion_date: datetime | None = None
    status: PlaylistStatus | None = None


class PlaylistResponseSchema(BaseModel):
    """Response schema for a single playlist."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    source_type: SourceType
    source_url: str | None
    thumbnail_url: str | None
    status: PlaylistStatus
    target_completion_date: datetime | None
    created_at: datetime
    updated_at: datetime


class PlaylistListResponseSchema(BaseModel):
    """Paginated list response for playlists."""

    items: list[PlaylistResponseSchema]
    total: int
    skip: int
    limit: int
