"""Add document control columns and tables for Sprint 6.

Revision ID: 004_document_control
Revises: 003_sessions_permissions
Create Date: 2025-12-21

Compliance: ISO 9001 §7.5.2, ISO 13485 §4.2.4-5, ISO 15489
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "004_document_control"
down_revision = "003_sessions_permissions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing document control columns to pages table
    # (document_number, version, status, classification already exist)
    op.add_column("pages", sa.Column("document_type", sa.String(50), nullable=True))
    op.add_column("pages", sa.Column("is_controlled", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("pages", sa.Column("revision", sa.String(10), nullable=False, server_default="A"))
    op.add_column("pages", sa.Column("major_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("pages", sa.Column("minor_version", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("pages", sa.Column("approved_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("pages", sa.Column("approved_by_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("pages", sa.Column("effective_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("pages", sa.Column("review_cycle_months", sa.Integer(), nullable=True))
    op.add_column("pages", sa.Column("next_review_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("pages", sa.Column("last_reviewed_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("pages", sa.Column("last_reviewed_by_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("pages", sa.Column("owner_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("pages", sa.Column("custodian_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("pages", sa.Column("retention_policy_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("pages", sa.Column("disposition_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("pages", sa.Column("supersedes_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("pages", sa.Column("superseded_by_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("pages", sa.Column("change_summary", sa.Text(), nullable=True))
    op.add_column("pages", sa.Column("change_reason", sa.Text(), nullable=True))
    op.add_column("pages", sa.Column("requires_training", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("pages", sa.Column("training_validity_months", sa.Integer(), nullable=True))

    # Update classification column from integer to varchar
    op.alter_column("pages", "classification", type_=sa.String(50), postgresql_using="CASE WHEN classification = 0 THEN 'public' WHEN classification = 1 THEN 'internal' WHEN classification = 2 THEN 'confidential' WHEN classification = 3 THEN 'restricted' ELSE 'internal' END")

    # Create indexes for document control
    op.create_index("ix_pages_document_type", "pages", ["document_type"])
    op.create_index("ix_pages_status", "pages", ["status"])
    op.create_index("ix_pages_next_review_date", "pages", ["next_review_date"])
    op.create_index("ix_pages_owner_id", "pages", ["owner_id"])

    # Create foreign keys
    op.create_foreign_key("fk_pages_approved_by", "pages", "users", ["approved_by_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_pages_last_reviewed_by", "pages", "users", ["last_reviewed_by_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_pages_owner", "pages", "users", ["owner_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_pages_custodian", "pages", "users", ["custodian_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_pages_supersedes", "pages", "pages", ["supersedes_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_pages_superseded_by", "pages", "pages", ["superseded_by_id"], ["id"], ondelete="SET NULL")

    # Create document_number_sequences table
    op.create_table(
        "document_number_sequences",
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("prefix", sa.String(20), nullable=False),
        sa.Column("format_pattern", sa.String(100), nullable=False, server_default="{prefix}-{number:03d}"),
        sa.Column("current_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("organization_id", "document_type", name="uq_doc_number_seq_org_type"),
    )

    # Create retention_policies table
    op.create_table(
        "retention_policies",
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("retention_years", sa.Integer(), nullable=False),
        sa.Column("disposition_method", sa.String(50), nullable=False, server_default="archive"),
        sa.Column("applicable_document_types", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notify_days_before", postgresql.JSON(), nullable=False, server_default="[30, 7, 1]"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )

    # Create approval_matrices table
    op.create_table(
        "approval_matrices",
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("applicable_document_types", postgresql.JSON(), nullable=False, server_default="[]"),
        sa.Column("steps", postgresql.JSON(), nullable=False),
        sa.Column("require_sequential", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
    )

    # Create approval_records table
    op.create_table(
        "approval_records",
        sa.Column("change_request_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("step_name", sa.String(100), nullable=False),
        sa.Column("approver_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("decision", sa.String(50), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["change_request_id"], ["change_requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approver_id"], ["users.id"]),
    )
    op.create_index("ix_approval_records_change_request", "approval_records", ["change_request_id"])

    # Add approval workflow columns to change_requests
    op.add_column("change_requests", sa.Column("approval_matrix_id", postgresql.UUID(as_uuid=False), nullable=True))
    op.add_column("change_requests", sa.Column("current_approval_step", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("change_requests", sa.Column("approval_status", sa.String(50), nullable=False, server_default="pending"))
    op.add_column("change_requests", sa.Column("is_major_revision", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("change_requests", sa.Column("change_reason", sa.Text(), nullable=True))
    op.add_column("change_requests", sa.Column("revision_metadata", postgresql.JSON(), nullable=True))

    op.create_foreign_key("fk_change_requests_approval_matrix", "change_requests", "approval_matrices", ["approval_matrix_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_pages_retention_policy", "pages", "retention_policies", ["retention_policy_id"], ["id"], ondelete="SET NULL")

    # Create document_lifecycle_configs table
    op.create_table(
        "document_lifecycle_configs",
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=True),
        sa.Column("allowed_transitions", postgresql.JSON(), nullable=False),
        sa.Column("custom_states", postgresql.JSON(), nullable=True),
        sa.Column("custom_transitions", postgresql.JSON(), nullable=True),
        sa.Column("requires_approval_for_effective", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("auto_obsolete_on_supersede", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("organization_id", "document_type", name="uq_lifecycle_config_org_type"),
    )


def downgrade() -> None:
    op.drop_table("document_lifecycle_configs")
    op.drop_constraint("fk_pages_retention_policy", "pages", type_="foreignkey")
    op.drop_constraint("fk_change_requests_approval_matrix", "change_requests", type_="foreignkey")

    op.drop_column("change_requests", "revision_metadata")
    op.drop_column("change_requests", "change_reason")
    op.drop_column("change_requests", "is_major_revision")
    op.drop_column("change_requests", "approval_status")
    op.drop_column("change_requests", "current_approval_step")
    op.drop_column("change_requests", "approval_matrix_id")

    op.drop_table("approval_records")
    op.drop_table("approval_matrices")
    op.drop_table("retention_policies")
    op.drop_table("document_number_sequences")

    op.drop_constraint("fk_pages_superseded_by", "pages", type_="foreignkey")
    op.drop_constraint("fk_pages_supersedes", "pages", type_="foreignkey")
    op.drop_constraint("fk_pages_custodian", "pages", type_="foreignkey")
    op.drop_constraint("fk_pages_owner", "pages", type_="foreignkey")
    op.drop_constraint("fk_pages_last_reviewed_by", "pages", type_="foreignkey")
    op.drop_constraint("fk_pages_approved_by", "pages", type_="foreignkey")

    op.drop_index("ix_pages_owner_id")
    op.drop_index("ix_pages_next_review_date")
    op.drop_index("ix_pages_status")
    op.drop_index("ix_pages_document_type")

    op.drop_column("pages", "training_validity_months")
    op.drop_column("pages", "requires_training")
    op.drop_column("pages", "change_reason")
    op.drop_column("pages", "change_summary")
    op.drop_column("pages", "superseded_by_id")
    op.drop_column("pages", "supersedes_id")
    op.drop_column("pages", "disposition_date")
    op.drop_column("pages", "retention_policy_id")
    op.drop_column("pages", "custodian_id")
    op.drop_column("pages", "owner_id")
    op.drop_column("pages", "last_reviewed_by_id")
    op.drop_column("pages", "last_reviewed_date")
    op.drop_column("pages", "next_review_date")
    op.drop_column("pages", "review_cycle_months")
    op.drop_column("pages", "effective_date")
    op.drop_column("pages", "approved_by_id")
    op.drop_column("pages", "approved_date")
    op.drop_column("pages", "minor_version")
    op.drop_column("pages", "major_version")
    op.drop_column("pages", "revision")
    op.drop_column("pages", "is_controlled")
    op.drop_column("pages", "document_type")
