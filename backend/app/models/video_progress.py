"""VideoProgress persistence model.

Tracks per-user per-video learning progress. This is the foundational data
source for all future learning intelligence features including Learning
Sessions, AI Tutor, Adaptive Revision, and Analytics.

Architecture:
- One progress record per user per video (enforced by unique constraint).
- Business logic lives in VideoProgressService; this class only defines
  database columns, constraints, and relationships.
- Status transitions are managed by the service layer.
"""

import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel
from app.models.enums import VideoProgressStatus


class VideoProgress(BaseModel):
    """Per-user video progress record.

    Tracks where a user left off, how much they've watched, and their
    completion state for a single video.
    """

    __tablename__ = "video_progress"

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Progress Fields
    status: Mapped[VideoProgressStatus] = mapped_column(
        Enum(
            VideoProgressStatus,
            name="videoprogressstatus",
            native_enum=False,
        ),
        nullable=False,
        default=VideoProgressStatus.NOT_STARTED,
        index=True,
    )
    completion_percentage: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0,
    )
    last_position_seconds: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )
    watch_time_seconds: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    # Timestamps
    first_started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        default=None,
    )
    last_watched_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        default=None,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        default=None,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="video_progress",
    )
    video: Mapped["Video"] = relationship(
        "Video",
        foreign_keys=[video_id],
        back_populates="progress_records",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "video_id",
            name="uq_user_video_progress",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<VideoProgress(id={self.id}, user_id={self.user_id}, "
            f"video_id={self.video_id}, status='{self.status}', "
            f"completion={self.completion_percentage:.1f}%)>"
        )