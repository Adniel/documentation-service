"""MCP Integration - Service Accounts.

Revision ID: 011_mcp_integration
Revises: 010_admin_ui_completion
Create Date: 2025-01-05

Sprint C: MCP Integration
- Service accounts for API access
- Usage tracking for service accounts
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = "011_mcp_integration"
down_revision = "010_admin_ui_completion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Service accounts table
    op.create_table(
        "service_accounts",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "organization_id",
            UUID(as_uuid=False),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Authentication
        sa.Column("api_key_hash", sa.String(64), nullable=False),  # SHA-256 hash
        sa.Column("api_key_prefix", sa.String(12), nullable=False),  # dsk_ + 8 chars
        # Permissions
        sa.Column("role", sa.String(50), nullable=False, server_default="viewer"),
        sa.Column("allowed_spaces", JSONB, nullable=True),  # List of space UUIDs
        sa.Column("allowed_operations", JSONB, nullable=True),  # List of operation names
        # Security
        sa.Column("ip_allowlist", JSONB, nullable=True),  # List of CIDR ranges
        sa.Column("rate_limit_per_minute", sa.Integer, nullable=False, server_default="60"),
        # Status
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column(
            "created_by_id",
            UUID(as_uuid=False),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
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

    # Indexes for service_accounts
    op.create_index(
        "ix_service_accounts_organization_id",
        "service_accounts",
        ["organization_id"],
    )
    op.create_index(
        "ix_service_accounts_api_key_prefix",
        "service_accounts",
        ["api_key_prefix"],
    )
    op.create_index(
        "ix_service_accounts_is_active",
        "service_accounts",
        ["is_active"],
    )
    op.create_unique_constraint(
        "uq_service_accounts_org_name",
        "service_accounts",
        ["organization_id", "name"],
    )

    # Service account usage tracking
    op.create_table(
        "service_account_usage",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "service_account_id",
            UUID(as_uuid=False),
            sa.ForeignKey("service_accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("operation", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", UUID(as_uuid=False), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),  # IPv6 max length
        sa.Column("response_code", sa.Integer, nullable=False),
        sa.Column("response_time_ms", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
    )

    # Indexes for usage tracking (optimized for time-series queries)
    op.create_index(
        "ix_service_account_usage_account_timestamp",
        "service_account_usage",
        ["service_account_id", "timestamp"],
    )
    op.create_index(
        "ix_service_account_usage_timestamp",
        "service_account_usage",
        ["timestamp"],
    )


def downgrade() -> None:
    op.drop_table("service_account_usage")
    op.drop_table("service_accounts")
