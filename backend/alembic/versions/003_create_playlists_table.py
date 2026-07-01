"""Create playlists table.

Revision ID: 003
Revises: 002
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()

    playliststatus = postgresql.ENUM(
        "ACTIVE",
        "COMPLETED",
        "ARCHIVED",
        "PAUSED",
        name="playliststatus",
        create_type=False,
    )

    sourcetype = postgresql.ENUM(
        "YOUTUBE",
        "PDF",
        "DOCUMENTATION",
        "BLOG",
        "OTHER",
        name="sourcetype",
        create_type=False,
    )

    playliststatus.create(bind, checkfirst=True)
    sourcetype.create(bind, checkfirst=True)

    op.create_table(
        "playlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column("source_type", sourcetype, nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=2048), nullable=True),
        sa.Column("status", playliststatus, nullable=False),
        sa.Column(
            "target_completion_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
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
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "ix_playlists_user_id",
        "playlists",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_playlists_status",
        "playlists",
        ["status"],
        unique=False,
    )

    op.create_index(
        "ix_playlists_deleted_at",
        "playlists",
        ["deleted_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_playlists_deleted_at", table_name="playlists")
    op.drop_index("ix_playlists_status", table_name="playlists")
    op.drop_index("ix_playlists_user_id", table_name="playlists")

    op.drop_table("playlists")

    bind = op.get_bind()

    playliststatus = postgresql.ENUM(
        "ACTIVE",
        "COMPLETED",
        "ARCHIVED",
        "PAUSED",
        name="playliststatus",
        create_type=False,
    )

    sourcetype = postgresql.ENUM(
        "YOUTUBE",
        "PDF",
        "DOCUMENTATION",
        "BLOG",
        "OTHER",
        name="sourcetype",
        create_type=False,
    )

    playliststatus.drop(bind, checkfirst=True)
    sourcetype.drop(bind, checkfirst=True)