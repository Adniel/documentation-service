"""Admin UI completion - organization settings fields.

Revision ID: 010
Revises: 009
Create Date: 2025-12-30

Sprint B: Admin UI Completion
- Add doc_numbering_enabled to organizations
- Add default_classification to organizations
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add organization settings fields
    op.add_column(
        "organizations",
        sa.Column("doc_numbering_enabled", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "organizations",
        sa.Column("default_classification", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("organizations", "default_classification")
    op.drop_column("organizations", "doc_numbering_enabled")
