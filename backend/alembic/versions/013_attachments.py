"""Attachments & Media Support.

Revision ID: 013_attachments
Revises: 012_integrated_access_control
Create Date: 2026-02-20

Sprint F: Attachments & Media Support
- Create attachments table for binary file metadata
- Supports images, PDFs, documents, audio, video
- Content hash for 21 CFR Part 11 signature integrity
- Version tracking with replacement chain
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "013_attachments"
down_revision = "012_integrated_access_control"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "attachments",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        # Parent page
        sa.Column(
            "page_id",
            UUID(as_uuid=False),
            sa.ForeignKey("pages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        # File identity
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        # Storage
        sa.Column("storage_key", sa.String(1000), nullable=False, unique=True),
        sa.Column(
            "storage_backend",
            sa.String(50),
            nullable=False,
            server_default="local",
        ),
        # Integrity
        sa.Column("content_hash", sa.String(64), nullable=False),  # SHA-256
        # Versioning
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "replaces_id",
            UUID(as_uuid=False),
            sa.ForeignKey("attachments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Status
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="active",
            index=True,
        ),
        # Uploader
        sa.Column(
            "uploaded_by_id",
            UUID(as_uuid=False),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        # Metadata
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("alt_text", sa.String(500), nullable=True),
        # Image dimensions
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        # Audio/video duration
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        # Deletion tracking
        sa.Column("deletion_reason", sa.Text(), nullable=True),
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
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Index for listing attachments by page and status
    op.create_index(
        "ix_attachments_page_status",
        "attachments",
        ["page_id", "status"],
    )

    # Index for content hash lookups (deduplication)
    op.create_index(
        "ix_attachments_content_hash",
        "attachments",
        ["content_hash"],
    )


def downgrade() -> None:
    op.drop_index("ix_attachments_content_hash")
    op.drop_index("ix_attachments_page_status")
    op.drop_table("attachments")
