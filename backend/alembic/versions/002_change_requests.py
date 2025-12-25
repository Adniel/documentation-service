"""Add change_requests tables for Sprint 4 Version Control UI

Revision ID: 002_change_requests
Revises: 001_initial
Create Date: 2025-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_change_requests"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change requests table - tracks drafts/branches at application level
    op.create_table(
        "change_requests",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        # Document being edited
        sa.Column(
            "page_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("pages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Metadata
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("number", sa.Integer(), nullable=False),
        # Author
        sa.Column(
            "author_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        # Git tracking (hidden from user)
        sa.Column("branch_name", sa.String(200), nullable=False, unique=True),
        sa.Column("base_commit_sha", sa.String(40), nullable=False),
        sa.Column("head_commit_sha", sa.String(40), nullable=True),
        # Status
        sa.Column("status", sa.String(50), nullable=False, default="draft", index=True),
        # Review tracking
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "reviewer_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_comment", sa.Text(), nullable=True),
        # Publication
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "published_by_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("merge_commit_sha", sa.String(40), nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Create index for finding change requests by page and status
    op.create_index(
        "ix_change_requests_page_status",
        "change_requests",
        ["page_id", "status"],
    )

    # Change request comments table
    op.create_table(
        "change_request_comments",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        # Parent change request
        sa.Column(
            "change_request_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("change_requests.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # Author
        sa.Column(
            "author_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        # Content
        sa.Column("content", sa.Text(), nullable=False),
        # Optional line-level comment
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=True),
        # Thread support
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("change_request_comments.id", ondelete="CASCADE"),
            nullable=True,
        ),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("change_request_comments")
    op.drop_index("ix_change_requests_page_status", table_name="change_requests")
    op.drop_table("change_requests")
