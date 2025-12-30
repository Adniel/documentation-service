"""Add Git remote support tables for Sprint 13.

Revision ID: 008_git_remote_support
Revises: 007_learning_module
Create Date: 2025-12-29

Sprint 13: Git Remote Support
Features: Remote configuration, credential storage, sync events
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "008_git_remote_support"
down_revision = "007_learning_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # ADD GIT REMOTE FIELDS TO ORGANIZATIONS
    # ==========================================================================
    op.add_column(
        "organizations",
        sa.Column("git_remote_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("git_remote_provider", sa.String(50), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("git_sync_enabled", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "organizations",
        sa.Column("git_sync_strategy", sa.String(50), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("git_default_branch", sa.String(100), nullable=False, server_default="main"),
    )
    op.add_column(
        "organizations",
        sa.Column("git_last_sync_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("git_sync_status", sa.String(50), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("git_webhook_secret", sa.String(255), nullable=True),
    )

    # ==========================================================================
    # CREATE ENUM TYPES
    # ==========================================================================
    credential_type_enum = postgresql.ENUM(
        "ssh_key", "https_token", "deploy_key",
        name="credential_type_enum",
        create_type=False,
    )
    credential_type_enum.create(op.get_bind(), checkfirst=True)

    sync_event_type_enum = postgresql.ENUM(
        "push", "pull", "fetch", "clone", "conflict", "error",
        name="sync_event_type_enum",
        create_type=False,
    )
    sync_event_type_enum.create(op.get_bind(), checkfirst=True)

    sync_direction_enum = postgresql.ENUM(
        "outbound", "inbound",
        name="sync_direction_enum",
        create_type=False,
    )
    sync_direction_enum.create(op.get_bind(), checkfirst=True)

    sync_status_enum = postgresql.ENUM(
        "success", "failed", "conflict", "in_progress",
        name="sync_status_enum",
        create_type=False,
    )
    sync_status_enum.create(op.get_bind(), checkfirst=True)

    # ==========================================================================
    # GIT CREDENTIALS TABLE
    # ==========================================================================
    op.create_table(
        "git_credentials",
        # Primary key and timestamps
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Organization (one-to-one)
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),

        # Credential type and value
        sa.Column(
            "credential_type",
            postgresql.ENUM("ssh_key", "https_token", "deploy_key", name="credential_type_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("encrypted_value", sa.Text(), nullable=False),
        sa.Column("encryption_iv", sa.String(32), nullable=False),

        # Optional metadata
        sa.Column("key_fingerprint", sa.String(100), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("label", sa.String(100), nullable=True),

        # Audit
        sa.Column("created_by_id", postgresql.UUID(as_uuid=False), nullable=False),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("organization_id"),
    )

    op.create_index("ix_git_credentials_org_id", "git_credentials", ["organization_id"])

    # ==========================================================================
    # GIT SYNC EVENTS TABLE
    # ==========================================================================
    op.create_table(
        "git_sync_events",
        # Primary key
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),

        # Organization
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),

        # Event details
        sa.Column(
            "event_type",
            postgresql.ENUM("push", "pull", "fetch", "clone", "conflict", "error", name="sync_event_type_enum", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "direction",
            postgresql.ENUM("outbound", "inbound", name="sync_direction_enum", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM("success", "failed", "conflict", "in_progress", name="sync_status_enum", create_type=False),
            nullable=False,
        ),

        # Branch and commits
        sa.Column("branch_name", sa.String(255), nullable=False),
        sa.Column("commit_sha_before", sa.String(40), nullable=True),
        sa.Column("commit_sha_after", sa.String(40), nullable=True),

        # Error details
        sa.Column("error_message", sa.Text(), nullable=True),

        # Files changed (JSON array)
        sa.Column("files_changed", sa.Text(), nullable=True),

        # Who triggered
        sa.Column("triggered_by_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("trigger_source", sa.String(50), nullable=True),

        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["triggered_by_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_index("ix_git_sync_events_org_id", "git_sync_events", ["organization_id"])
    op.create_index("ix_git_sync_events_status", "git_sync_events", ["status"])
    op.create_index("ix_git_sync_events_created_at", "git_sync_events", ["created_at"])
    op.create_index("ix_git_sync_events_org_status", "git_sync_events", ["organization_id", "status"])


def downgrade() -> None:
    # Drop git_sync_events
    op.drop_index("ix_git_sync_events_org_status")
    op.drop_index("ix_git_sync_events_created_at")
    op.drop_index("ix_git_sync_events_status")
    op.drop_index("ix_git_sync_events_org_id")
    op.drop_table("git_sync_events")

    # Drop git_credentials
    op.drop_index("ix_git_credentials_org_id")
    op.drop_table("git_credentials")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS sync_status_enum")
    op.execute("DROP TYPE IF EXISTS sync_direction_enum")
    op.execute("DROP TYPE IF EXISTS sync_event_type_enum")
    op.execute("DROP TYPE IF EXISTS credential_type_enum")

    # Remove organization columns
    op.drop_column("organizations", "git_webhook_secret")
    op.drop_column("organizations", "git_sync_status")
    op.drop_column("organizations", "git_last_sync_at")
    op.drop_column("organizations", "git_default_branch")
    op.drop_column("organizations", "git_sync_strategy")
    op.drop_column("organizations", "git_sync_enabled")
    op.drop_column("organizations", "git_remote_provider")
    op.drop_column("organizations", "git_remote_url")
