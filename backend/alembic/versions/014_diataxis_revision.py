"""Diataxis Revision - Per-Page Content Types.

Revision ID: 014_diataxis_revision
Revises: 013_attachments
Create Date: 2026-02-20

Sprint E: Diataxis Revision
- Add diataxis_types JSONB array to pages table
- Enables per-page multi-type categorization (replaces space-only typing)
- Data migration: populate page types from parent space's diataxis_type
- Rename space.diataxis_type to default_diataxis_type semantically (keep column name)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = "014_diataxis_revision"
down_revision = "013_attachments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add diataxis_types JSONB array column to pages
    op.add_column(
        "pages",
        sa.Column(
            "diataxis_types",
            JSONB,
            server_default="[]",
            nullable=False,
        ),
    )

    # GIN index for efficient array containment queries (@> operator)
    op.create_index(
        "ix_pages_diataxis_types",
        "pages",
        ["diataxis_types"],
        postgresql_using="gin",
    )

    # Data migration: populate page diataxis_types from parent space
    # Pages in a space with a specific type get that type in their array
    # Pages in "mixed" spaces get an empty array (no specific type)
    op.execute("""
        UPDATE pages
        SET diataxis_types = CASE
            WHEN spaces.diataxis_type = 'mixed' THEN '[]'::jsonb
            ELSE jsonb_build_array(spaces.diataxis_type)
        END
        FROM spaces
        WHERE pages.space_id = spaces.id
    """)


def downgrade() -> None:
    op.drop_index("ix_pages_diataxis_types", table_name="pages")
    op.drop_column("pages", "diataxis_types")
