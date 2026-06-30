"""Progress schemas for request and response validation.

These schemas define the API contract for video progress tracking.
All business rules (e.g., completion_percentage <= 100) are validated
at the Pydantic level, while cross-field business logic lives in the
service layer.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import VideoProgressStatus


class ProgressBase(BaseModel):
    """Shared progress fields for create/update operations."""

    completion_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Percentage of video watched (0–100)",
    )
    last_position_seconds: int = Field(
        default=0,
        ge=0,
        description="Last playback position in seconds",
    )
    watch_time_seconds: int = Field(
        default=0,
        ge=0,
        description="Total watch time in seconds",
    )


class ProgressCreateSchema(ProgressBase):
    """Schema for creating a new progress record.

    Typically not used directly; the service auto-creates records
    on first interaction.
    """

    status: VideoProgressStatus = Field(
        default=VideoProgressStatus.NOT_STARTED,
        description="Current progress status",
    )


class ProgressUpdateSchema(BaseModel):
    """Schema for updating video progress.

    All fields are optional — only provided fields will be updated.
    Business rules (e.g., watch_time cannot decrease) are enforced
    in the service layer.
    """

    status: VideoProgressStatus | None = Field(
        default=None,
        description="Current progress status",
    )
    completion_percentage: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Percentage of video watched (0–100)",
    )
    last_position_seconds: int | None = Field(
        default=None,
        ge=0,
        description="Last playback position in seconds",
    )
    watch_time_seconds: int | None = Field(
        default=None,
        ge=0,
        description="Total watch time in seconds",
    )


class ProgressResponseSchema(BaseModel):
    """Response schema for a single progress record."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    video_id: UUID
    status: VideoProgressStatus
    completion_percentage: float
    last_position_seconds: int
    watch_time_seconds: int
    first_started_at: datetime | None = None
    last_watched_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProgressSummarySchema(BaseModel):
    """Aggregated progress summary for a playlist or user.

    This is NOT analytics — it returns raw computed summaries
    that future phases (Analytics, AI Tutor) will consume.
    """

    total_videos: int = Field(..., description="Total number of videos")
    completed_videos: int = Field(..., description="Number of completed videos")
    in_progress_videos: int = Field(..., description="Number of videos in progress")
    not_started_videos: int = Field(..., description="Number of videos not started")
    total_watch_time_seconds: int = Field(
        ...,
        description="Total watch time across all videos",
    )
    average_completion_percentage: float = Field(
        ...,
        description="Average completion percentage across all videos",
    )
    estimated_remaining_seconds: int = Field(
        ...,
        description="Estimated remaining watch time based on video durations",
    )