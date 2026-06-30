from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel


class User(BaseModel):
    """User persistence model.

    Represents the users table. Business logic lives in UserService;
    this class only defines database columns and constraints.
    """

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    profile_picture: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Relationships
    playlists: Mapped[list["Playlist"]] = relationship(
        "Playlist",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Playlist.user_id",
    )
    video_progress: Mapped[list["VideoProgress"]] = relationship(
        "VideoProgress",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="VideoProgress.user_id",
    )
