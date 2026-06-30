"""Create video_progress table.

Revision ID: 005
Revises: 004
Create Date: 2026-06-30

This migration introduces the video_progress table, which is the foundation
for all user-specific learning progress tracking. It records per-user,
per-video progress including playback position, completion percentage,
watch time, and completion state.

Why this migration exists: Phase 5 introduces persistent user-specific
video progress tracking. This table stores the data that all future
learning intelligence features (Learning Sessions, AI Tutor, Analytics)
will consume.

Indexes:
- ix_video_progress_user_id: Fast lookup by user
- ix_video_progress_video_id: Fast lookup by video
- ix_video_progress_status: Fast filtering by status
- ix_video_progress_deleted_at: Soft delete support

Foreign Keys:
- user_id -> users.id (CASCADE on delete)
- video_id -> videos.id (CASCADE on delete)

Constraints:
- uq_user_video_progress: One progress record per user per video
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "video_progress",
        # Primary Key
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),

        # Foreign Keys
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("video_id", postgresql.UUID(as_uuid=True), nullable=False),

        # Progress Fields
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column(
            "completion_percentage",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0.0"),
        ),
        sa.Column(
            "last_position_seconds",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "watch_time_seconds",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),

        # Timestamps
        sa.Column("first_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_watched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),

        # Audit Fields (inherited from BaseModel)
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

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["video_id"],
            ["videos.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            "video_id",
            name="uq_user_video_progress",
        ),
    )

    # Indexes
    op.create_index(
        "ix_video_progress_user_id",
        "video_progress",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_video_progress_video_id",
        "video_progress",
        ["video_id"],
        unique=False,
    )
    op.create_index(
        "ix_video_progress_status",
        "video_progress",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_video_progress_deleted_at",
        "video_progress",
        ["deleted_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_video_progress_deleted_at", table_name="video_progress")
    op.drop_index("ix_video_progress_status", table_name="video_progress")
    op.drop_index("ix_video_progress_video_id", table_name="video_progress")
    op.drop_index("ix_video_progress_user_id", table_name="video_progress")
    op.drop_table("video_progress")