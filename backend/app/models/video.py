"""Video persistence model.

Represents videos belonging to a playlist. This model is persistence-only;
business logic lives in VideoService and playlist import orchestration lives
in PlaylistImportService.
"""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel


class Video(BaseModel):
    """A video discovered within a playlist."""

    __tablename__ = "videos"

    playlist_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("playlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    youtube_video_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    channel_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    position: Mapped[int | None] = mapped_column(nullable=True, index=True)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)

    playlist: Mapped["Playlist"] = relationship(
        "Playlist",
        foreign_keys=[playlist_id],
        back_populates="videos",
    )
    progress_records: Mapped[list["VideoProgress"]] = relationship(
        "VideoProgress",
        back_populates="video",
        cascade="all, delete-orphan",
        foreign_keys="VideoProgress.video_id",
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, youtube_video_id='{self.youtube_video_id}', title='{self.title}')>"
