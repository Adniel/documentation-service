"""Add electronic signatures tables for Sprint 7.

Revision ID: 005_electronic_signatures
Revises: 004_document_control
Create Date: 2025-12-22

Compliance: FDA 21 CFR Part 11 §11.50, §11.70, §11.100, §11.200
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "005_electronic_signatures"
down_revision = "004_document_control"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create electronic_signatures table
    op.create_table(
        "electronic_signatures",
        # Primary key
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # What was signed (one of these should be set)
        sa.Column("page_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("change_request_id", postgresql.UUID(as_uuid=False), nullable=True),

        # Who signed - FROZEN at signature time (§11.50)
        sa.Column("signer_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("signer_name", sa.String(255), nullable=False),
        sa.Column("signer_email", sa.String(255), nullable=False),
        sa.Column("signer_title", sa.String(255), nullable=True),

        # Signature meaning (§11.50)
        sa.Column("meaning", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),

        # Content integrity (§11.70)
        sa.Column("content_hash", sa.String(64), nullable=False),  # SHA-256 hex
        sa.Column("git_commit_sha", sa.String(40), nullable=True),

        # Trusted timestamp (§11.50)
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ntp_server", sa.String(255), nullable=False),

        # Re-authentication evidence (§11.200)
        sa.Column("auth_method", sa.String(50), nullable=False),
        sa.Column("auth_session_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=False),  # IPv6 max
        sa.Column("user_agent", sa.String(512), nullable=True),

        # Signature chain for multi-sig workflows
        sa.Column("previous_signature_id", postgresql.UUID(as_uuid=False), nullable=True),

        # Validity tracking
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidation_reason", sa.Text(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["page_id"], ["pages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["change_request_id"], ["change_requests.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["signer_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["auth_session_id"], ["sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["previous_signature_id"], ["electronic_signatures.id"], ondelete="SET NULL"),
    )

    # Create indexes for electronic_signatures
    op.create_index("ix_esig_page_id", "electronic_signatures", ["page_id"])
    op.create_index("ix_esig_cr_id", "electronic_signatures", ["change_request_id"])
    op.create_index("ix_esig_signer_id", "electronic_signatures", ["signer_id"])
    op.create_index("ix_esig_meaning", "electronic_signatures", ["meaning"])
    op.create_index("ix_esig_page_valid", "electronic_signatures", ["page_id", "is_valid"])
    op.create_index("ix_esig_cr_valid", "electronic_signatures", ["change_request_id", "is_valid"])
    op.create_index("ix_esig_signer_time", "electronic_signatures", ["signer_id", "signed_at"])

    # Create signature_challenges table
    op.create_table(
        "signature_challenges",
        # Primary key
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Who is signing
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),

        # What will be signed
        sa.Column("page_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("change_request_id", postgresql.UUID(as_uuid=False), nullable=True),

        # Signature intent
        sa.Column("meaning", sa.String(50), nullable=False),
        sa.Column("reason", sa.String(1000), nullable=True),

        # Content hash at challenge time
        sa.Column("content_hash", sa.String(64), nullable=False),

        # Challenge token
        sa.Column("challenge_token", sa.String(64), nullable=False, unique=True),

        # Expiration
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),

        # Usage tracking
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["page_id"], ["pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["change_request_id"], ["change_requests.id"], ondelete="CASCADE"),
    )

    # Create indexes for signature_challenges
    op.create_index("ix_sigchallenge_token", "signature_challenges", ["challenge_token"])
    op.create_index("ix_sigchallenge_user_id", "signature_challenges", ["user_id"])
    op.create_index("ix_sigchallenge_expires", "signature_challenges", ["expires_at"])
    op.create_index("ix_sigchallenge_user_active", "signature_challenges", ["user_id", "is_used", "expires_at"])


def downgrade() -> None:
    # Drop signature_challenges indexes and table
    op.drop_index("ix_sigchallenge_user_active")
    op.drop_index("ix_sigchallenge_expires")
    op.drop_index("ix_sigchallenge_user_id")
    op.drop_index("ix_sigchallenge_token")
    op.drop_table("signature_challenges")

    # Drop electronic_signatures indexes and table
    op.drop_index("ix_esig_signer_time")
    op.drop_index("ix_esig_cr_valid")
    op.drop_index("ix_esig_page_valid")
    op.drop_index("ix_esig_meaning")
    op.drop_index("ix_esig_signer_id")
    op.drop_index("ix_esig_cr_id")
    op.drop_index("ix_esig_page_id")
    op.drop_table("electronic_signatures")
