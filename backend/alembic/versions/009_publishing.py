"""Add publishing tables for Sprint A.

Revision ID: 009_publishing
Revises: 008_git_remote_support
Create Date: 2025-12-29

Sprint A: Publishing
Features: Published sites, themes, site configuration
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "009_publishing"
down_revision = "008_git_remote_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # CREATE ENUM TYPES
    # ==========================================================================
    sidebar_position_enum = postgresql.ENUM(
        "left", "right", "hidden",
        name="sidebar_position_enum",
        create_type=False,
    )
    sidebar_position_enum.create(op.get_bind(), checkfirst=True)

    content_width_enum = postgresql.ENUM(
        "prose", "wide", "full",
        name="content_width_enum",
        create_type=False,
    )
    content_width_enum.create(op.get_bind(), checkfirst=True)

    site_status_enum = postgresql.ENUM(
        "draft", "published", "maintenance", "archived",
        name="site_status_enum",
        create_type=False,
    )
    site_status_enum.create(op.get_bind(), checkfirst=True)

    site_visibility_enum = postgresql.ENUM(
        "public", "authenticated", "restricted",
        name="site_visibility_enum",
        create_type=False,
    )
    site_visibility_enum.create(op.get_bind(), checkfirst=True)

    # ==========================================================================
    # THEMES TABLE
    # ==========================================================================
    op.create_table(
        "themes",
        # Primary key and timestamps
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Organization (nullable for system themes)
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=True),

        # Basic info
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),

        # Colors
        sa.Column("primary_color", sa.String(20), nullable=False, server_default="#2563eb"),
        sa.Column("secondary_color", sa.String(20), nullable=False, server_default="#64748b"),
        sa.Column("accent_color", sa.String(20), nullable=False, server_default="#0ea5e9"),
        sa.Column("background_color", sa.String(20), nullable=False, server_default="#ffffff"),
        sa.Column("surface_color", sa.String(20), nullable=False, server_default="#f8fafc"),
        sa.Column("text_color", sa.String(20), nullable=False, server_default="#1f2937"),
        sa.Column("text_muted_color", sa.String(20), nullable=False, server_default="#6b7280"),

        # Typography
        sa.Column("heading_font", sa.String(100), nullable=False, server_default="Inter"),
        sa.Column("body_font", sa.String(100), nullable=False, server_default="Inter"),
        sa.Column("code_font", sa.String(100), nullable=False, server_default="JetBrains Mono"),
        sa.Column("base_font_size", sa.String(20), nullable=False, server_default="16px"),

        # Layout
        sa.Column("sidebar_position", sa.String(20), nullable=False, server_default="left"),
        sa.Column("content_width", sa.String(20), nullable=False, server_default="prose"),
        sa.Column("toc_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("header_height", sa.String(20), nullable=False, server_default="64px"),

        # Branding
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("favicon_url", sa.Text(), nullable=True),

        # Custom CSS/HTML
        sa.Column("custom_css", sa.Text(), nullable=True),
        sa.Column("custom_head_html", sa.Text(), nullable=True),

        # Created by
        sa.Column("created_by_id", postgresql.UUID(as_uuid=False), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_index("ix_themes_organization_id", "themes", ["organization_id"])
    op.create_index("ix_themes_is_default", "themes", ["is_default"])

    # ==========================================================================
    # PUBLISHED SITES TABLE
    # ==========================================================================
    op.create_table(
        "published_sites",
        # Primary key and timestamps
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Content source (one site per space)
        sa.Column("space_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),

        # Site identity
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("custom_domain", sa.String(255), nullable=True),
        sa.Column("custom_domain_verified", sa.Boolean(), nullable=False, server_default="false"),

        # Site metadata (SEO)
        sa.Column("site_title", sa.String(255), nullable=False),
        sa.Column("site_description", sa.Text(), nullable=True),
        sa.Column("og_image_url", sa.Text(), nullable=True),
        sa.Column("favicon_url", sa.Text(), nullable=True),

        # Theme
        sa.Column("theme_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("custom_css", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.Text(), nullable=True),

        # Visibility and access
        sa.Column("visibility", sa.String(20), nullable=False, server_default="authenticated"),
        sa.Column("allowed_email_domains", sa.JSON(), nullable=True),  # JSON list of domain strings

        # Publishing state
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("last_published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_by_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("published_commit_sha", sa.String(40), nullable=True),

        # Feature flags
        sa.Column("search_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("toc_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("version_selector_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("feedback_enabled", sa.Boolean(), nullable=False, server_default="false"),

        # Analytics
        sa.Column("analytics_id", sa.String(50), nullable=True),

        # Navigation customization
        sa.Column("navigation_config", sa.Text(), nullable=True),
        sa.Column("footer_config", sa.Text(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["space_id"], ["spaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["theme_id"], ["themes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["published_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("space_id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("custom_domain"),
    )

    op.create_index("ix_published_sites_slug", "published_sites", ["slug"])
    op.create_index("ix_published_sites_organization_id", "published_sites", ["organization_id"])
    op.create_index("ix_published_sites_status", "published_sites", ["status"])
    op.create_index("ix_published_sites_custom_domain", "published_sites", ["custom_domain"])

    # ==========================================================================
    # INSERT DEFAULT SYSTEM THEMES
    # ==========================================================================
    op.execute("""
        INSERT INTO themes (id, name, description, is_default, primary_color, secondary_color,
                           accent_color, background_color, surface_color, text_color, text_muted_color)
        VALUES
            (gen_random_uuid(), 'Default Light', 'Clean and modern light theme', true,
             '#2563eb', '#64748b', '#0ea5e9', '#ffffff', '#f8fafc', '#1f2937', '#6b7280'),
            (gen_random_uuid(), 'Default Dark', 'Modern dark theme for low-light environments', false,
             '#3b82f6', '#94a3b8', '#22d3ee', '#0f172a', '#1e293b', '#f1f5f9', '#94a3b8'),
            (gen_random_uuid(), 'Ocean', 'Calm blue-green theme', false,
             '#0891b2', '#64748b', '#06b6d4', '#ffffff', '#f0fdfa', '#134e4a', '#5eead4'),
            (gen_random_uuid(), 'Forest', 'Nature-inspired green theme', false,
             '#16a34a', '#71717a', '#22c55e', '#ffffff', '#f0fdf4', '#14532d', '#86efac')
    """)


def downgrade() -> None:
    # Drop published_sites
    op.drop_index("ix_published_sites_custom_domain")
    op.drop_index("ix_published_sites_status")
    op.drop_index("ix_published_sites_organization_id")
    op.drop_index("ix_published_sites_slug")
    op.drop_table("published_sites")

    # Drop themes
    op.drop_index("ix_themes_is_default")
    op.drop_index("ix_themes_organization_id")
    op.drop_table("themes")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS site_visibility_enum")
    op.execute("DROP TYPE IF EXISTS site_status_enum")
    op.execute("DROP TYPE IF EXISTS content_width_enum")
    op.execute("DROP TYPE IF EXISTS sidebar_position_enum")
