"""Create videos table.

Revision ID: 004
Revises: 003
Create Date: 2026-06-29

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("playlist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("youtube_video_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.String(length=5000), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=2048), nullable=True),
        sa.Column("channel_name", sa.String(length=255), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["playlist_id"], ["playlists.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_videos_playlist_id", "videos", ["playlist_id"], unique=False)
    op.create_index("ix_videos_youtube_video_id", "videos", ["youtube_video_id"], unique=False)
    op.create_index("ix_videos_position", "videos", ["position"], unique=False)
    op.create_index("ix_videos_deleted_at", "videos", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_videos_deleted_at", table_name="videos")
    op.drop_index("ix_videos_position", table_name="videos")
    op.drop_index("ix_videos_youtube_video_id", table_name="videos")
    op.drop_index("ix_videos_playlist_id", table_name="videos")
    op.drop_table("videos")
