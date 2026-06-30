"""Playlist persistence model.

Represents the playlists table. Each playlist belongs to exactly one user.
Business logic lives in PlaylistService; this class only defines database
columns, constraints, and relationships.

Architecture:
- Clean separation: model defines structure, service handles logic
- Relationships configured here for SQLAlchemy ORM
- Soft delete support inherited from BaseModel
"""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel
from app.models.enums import PlaylistStatus, SourceType


class Playlist(BaseModel):
    """Playlist persistence model.

    Represents a learning playlist that belongs to a user.
    Supports various content sources (YouTube, PDF, etc.).
    Uses soft delete to preserve historical data.
    """

    __tablename__ = "playlists"

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core Fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Source Configuration
    source_type: Mapped[SourceType] = mapped_column(
        ENUM(SourceType, name="sourcetype", native_enum=False),
        nullable=False,
        default=SourceType.OTHER,
    )
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    # Status and Timeline
    status: Mapped[PlaylistStatus] = mapped_column(
        ENUM(PlaylistStatus, name="playliststatus", native_enum=False),
        nullable=False,
        default=PlaylistStatus.ACTIVE,
        index=True,
    )
    target_completion_date: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="playlists",
    )
    videos: Mapped[list["Video"]] = relationship(
        "Video",
        back_populates="playlist",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Playlist(id={self.id}, title='{self.title}', user_id={self.user_id})>"
