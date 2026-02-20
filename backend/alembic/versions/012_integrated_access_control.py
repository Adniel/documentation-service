"""Integrated Access Control for Published Sites.

Revision ID: 012_integrated_access_control
Revises: 011_mcp_integration
Create Date: 2025-01-05

Sprint D: Integrated Access Control
- Add workspace default_classification for inheritance chain
- Add page show_when_restricted for discovery behavior override
- Add published site discovery settings
- Add site visitors table for external users
- Add site visitor roles for per-site access grants
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = "012_integrated_access_control"
down_revision = "011_mcp_integration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === WORKSPACE: Add default_classification for inheritance ===
    op.add_column(
        "workspaces",
        sa.Column(
            "default_classification",
            sa.Integer(),
            nullable=True,  # None = inherit from org
        ),
    )

    # === PAGE: Add show_when_restricted for discovery override ===
    op.add_column(
        "pages",
        sa.Column(
            "show_when_restricted",
            sa.Boolean(),
            nullable=True,  # None = inherit from site setting
        ),
    )

    # === PUBLISHED SITES: Add discovery settings ===
    op.add_column(
        "published_sites",
        sa.Column(
            "show_restricted_as_placeholder",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "published_sites",
        sa.Column(
            "restricted_placeholder_message",
            sa.String(500),
            nullable=True,
        ),
    )

    # === SITE VISITORS: External users ===
    op.create_table(
        "site_visitors",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        # Email-based identity
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("email_verified", sa.Boolean(), default=False, nullable=False),
        # Authentication
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("magic_link_token", sa.String(255), nullable=True),
        sa.Column("magic_link_expires", sa.DateTime(timezone=True), nullable=True),
        # Profile
        sa.Column("display_name", sa.String(255), nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        # Link to internal user if applicable (for SSO)
        sa.Column(
            "internal_user_id",
            UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
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
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    # Index for magic link lookup
    op.create_index(
        "ix_site_visitors_magic_link",
        "site_visitors",
        ["magic_link_token"],
        unique=False,
    )

    # === SITE VISITOR ROLES: Per-site access grants ===
    op.create_table(
        "site_visitor_roles",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        # The visitor
        sa.Column(
            "visitor_id",
            UUID(as_uuid=False),
            sa.ForeignKey("site_visitors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # The site
        sa.Column(
            "site_id",
            UUID(as_uuid=False),
            sa.ForeignKey("published_sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Role and clearance
        sa.Column("role_name", sa.String(100), default="visitor", nullable=False),
        sa.Column("clearance_level", sa.Integer(), default=0, nullable=False),
        # Optional explicit page access (JSON array of page IDs)
        sa.Column("allowed_page_ids", JSONB, nullable=True),
        # Invitation tracking
        sa.Column(
            "invited_by_id",
            UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "invited_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # Expiration
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
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
        # Unique constraint: one role per visitor per site
        sa.UniqueConstraint("visitor_id", "site_id", name="uq_visitor_site_role"),
    )

    # Indexes for role lookup
    op.create_index(
        "ix_site_visitor_roles_visitor",
        "site_visitor_roles",
        ["visitor_id"],
    )
    op.create_index(
        "ix_site_visitor_roles_site",
        "site_visitor_roles",
        ["site_id"],
    )


def downgrade() -> None:
    # Drop site visitor roles
    op.drop_index("ix_site_visitor_roles_site")
    op.drop_index("ix_site_visitor_roles_visitor")
    op.drop_table("site_visitor_roles")

    # Drop site visitors
    op.drop_index("ix_site_visitors_magic_link")
    op.drop_table("site_visitors")

    # Remove published site columns
    op.drop_column("published_sites", "restricted_placeholder_message")
    op.drop_column("published_sites", "show_restricted_as_placeholder")

    # Remove page column
    op.drop_column("pages", "show_when_restricted")

    # Remove workspace column
    op.drop_column("workspaces", "default_classification")
