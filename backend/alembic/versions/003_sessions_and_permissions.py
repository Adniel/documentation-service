"""Add sessions and permissions tables for Sprint 5 Access Control.

Revision ID: 003_sessions_permissions
Revises: 002_change_requests
Create Date: 2025-12-21

Compliance: 21 CFR §11.10(d) - Limiting system access to authorized individuals
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003_sessions_permissions"
down_revision = "002_change_requests"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sessions table
    op.create_table(
        "sessions",
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("token_jti", sa.String(255), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("last_activity", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_reason", sa.String(255), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # Create indexes for sessions
    op.create_index("ix_sessions_token_jti", "sessions", ["token_jti"], unique=True)
    op.create_index("ix_session_user_active", "sessions", ["user_id", "is_active"])
    op.create_index("ix_session_expires", "sessions", ["expires_at"])

    # Create permissions table
    op.create_table(
        "permissions",
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("principal_type", sa.String(20), nullable=False),
        sa.Column("principal_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("granted_by_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["granted_by_id"], ["users.id"], ondelete="SET NULL"),
    )

    # Create indexes for permissions
    op.create_index("ix_permissions_resource", "permissions", ["resource_type", "resource_id"])
    op.create_index("ix_permissions_principal", "permissions", ["principal_type", "principal_id"])
    op.create_index(
        "ix_permissions_unique",
        "permissions",
        ["resource_type", "resource_id", "principal_type", "principal_id", "role"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("permissions")
    op.drop_table("sessions")
