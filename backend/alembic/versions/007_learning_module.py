"""Add learning module tables for Sprint 9.

Revision ID: 007_learning_module
Revises: 006_audit_immutability
Create Date: 2025-12-22

Sprint 9: Learning Module Basics
Compliance: ISO 9001 training records, ISO 13485 competency verification
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "007_learning_module"
down_revision = "006_audit_immutability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # ASSESSMENTS TABLE
    # ==========================================================================
    op.create_table(
        "assessments",
        # Primary key and timestamps
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Link to document
        sa.Column("page_id", postgresql.UUID(as_uuid=False), nullable=False),

        # Assessment metadata
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),

        # Scoring settings
        sa.Column("passing_score", sa.Integer(), nullable=False, server_default="80"),

        # Attempt limits
        sa.Column("max_attempts", sa.Integer(), nullable=True),
        sa.Column("time_limit_minutes", sa.Integer(), nullable=True),

        # Status
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),

        # Authorship
        sa.Column("created_by_id", postgresql.UUID(as_uuid=False), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["page_id"], ["pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_index("ix_assessments_page_id", "assessments", ["page_id"])
    op.create_index("ix_assessments_active", "assessments", ["is_active"])

    # ==========================================================================
    # ASSESSMENT QUESTIONS TABLE
    # ==========================================================================
    op.create_table(
        "assessment_questions",
        # Primary key and timestamps
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Parent assessment
        sa.Column("assessment_id", postgresql.UUID(as_uuid=False), nullable=False),

        # Question content
        sa.Column("question_type", sa.String(50), nullable=False, server_default="multiple_choice"),
        sa.Column("question_text", sa.Text(), nullable=False),

        # Answer options (for multiple choice)
        sa.Column("options", postgresql.JSON(), nullable=True),

        # Correct answer (for true_false and fill_blank)
        sa.Column("correct_answer", sa.String(500), nullable=True),

        # Scoring
        sa.Column("points", sa.Integer(), nullable=False, server_default="1"),

        # Feedback
        sa.Column("explanation", sa.Text(), nullable=True),

        # Ordering
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_assessment_questions_assessment_id", "assessment_questions", ["assessment_id"])
    op.create_index("ix_assessment_questions_order", "assessment_questions", ["assessment_id", "sort_order"])

    # ==========================================================================
    # LEARNING ASSIGNMENTS TABLE
    # ==========================================================================
    op.create_table(
        "learning_assignments",
        # Primary key and timestamps
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Core assignment info
        sa.Column("page_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("assigned_by_id", postgresql.UUID(as_uuid=False), nullable=True),

        # Status tracking
        sa.Column("status", sa.String(50), nullable=False, server_default="assigned"),

        # Dates
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reminder_sent_at", sa.DateTime(timezone=True), nullable=True),

        # Optional notes
        sa.Column("notes", sa.Text(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["page_id"], ["pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assigned_by_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_index("ix_learning_assignments_page_id", "learning_assignments", ["page_id"])
    op.create_index("ix_learning_assignments_user_id", "learning_assignments", ["user_id"])
    op.create_index("ix_learning_assignments_status", "learning_assignments", ["status"])
    op.create_index("ix_learning_assignments_due_date", "learning_assignments", ["due_date"])
    op.create_index("ix_learning_assignments_user_status", "learning_assignments", ["user_id", "status"])
    op.create_index("ix_learning_assignments_page_status", "learning_assignments", ["page_id", "status"])

    # ==========================================================================
    # QUIZ ATTEMPTS TABLE
    # ==========================================================================
    op.create_table(
        "quiz_attempts",
        # Primary key and timestamps
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Core references
        sa.Column("assessment_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=False), nullable=True),

        # Status and scoring
        sa.Column("status", sa.String(50), nullable=False, server_default="in_progress"),
        sa.Column("score", sa.Float(), nullable=True),

        # Answers stored as JSON
        sa.Column("answers", postgresql.JSON(), nullable=False, server_default="{}"),

        # Timing
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=True),

        # Attempt tracking
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),

        # Grading details
        sa.Column("earned_points", sa.Integer(), nullable=True),
        sa.Column("total_points", sa.Integer(), nullable=True),
        sa.Column("passing_score", sa.Integer(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assignment_id"], ["learning_assignments.id"], ondelete="SET NULL"),
    )

    op.create_index("ix_quiz_attempts_assessment_id", "quiz_attempts", ["assessment_id"])
    op.create_index("ix_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    op.create_index("ix_quiz_attempts_assignment_id", "quiz_attempts", ["assignment_id"])
    op.create_index("ix_quiz_attempts_status", "quiz_attempts", ["status"])
    op.create_index("ix_quiz_attempts_user_assessment", "quiz_attempts", ["user_id", "assessment_id"])

    # ==========================================================================
    # TRAINING ACKNOWLEDGMENTS TABLE
    # ==========================================================================
    op.create_table(
        "training_acknowledgments",
        # Primary key and timestamps
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),

        # Core references
        sa.Column("page_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("quiz_attempt_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("signature_id", postgresql.UUID(as_uuid=False), nullable=False),

        # Timing
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),

        # Validity tracking
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidation_reason", sa.Text(), nullable=True),

        # Document version at acknowledgment time
        sa.Column("page_version", sa.String(50), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["page_id"], ["pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assignment_id"], ["learning_assignments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["quiz_attempt_id"], ["quiz_attempts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["signature_id"], ["electronic_signatures.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("signature_id"),
    )

    op.create_index("ix_training_ack_page_id", "training_acknowledgments", ["page_id"])
    op.create_index("ix_training_ack_user_id", "training_acknowledgments", ["user_id"])
    op.create_index("ix_training_ack_assignment_id", "training_acknowledgments", ["assignment_id"])
    op.create_index("ix_training_ack_valid_until", "training_acknowledgments", ["valid_until"])
    op.create_index("ix_training_ack_user_page", "training_acknowledgments", ["user_id", "page_id"])
    op.create_index("ix_training_ack_valid_user", "training_acknowledgments", ["is_valid", "user_id"])


def downgrade() -> None:
    # Drop training_acknowledgments
    op.drop_index("ix_training_ack_valid_user")
    op.drop_index("ix_training_ack_user_page")
    op.drop_index("ix_training_ack_valid_until")
    op.drop_index("ix_training_ack_assignment_id")
    op.drop_index("ix_training_ack_user_id")
    op.drop_index("ix_training_ack_page_id")
    op.drop_table("training_acknowledgments")

    # Drop quiz_attempts
    op.drop_index("ix_quiz_attempts_user_assessment")
    op.drop_index("ix_quiz_attempts_status")
    op.drop_index("ix_quiz_attempts_assignment_id")
    op.drop_index("ix_quiz_attempts_user_id")
    op.drop_index("ix_quiz_attempts_assessment_id")
    op.drop_table("quiz_attempts")

    # Drop learning_assignments
    op.drop_index("ix_learning_assignments_page_status")
    op.drop_index("ix_learning_assignments_user_status")
    op.drop_index("ix_learning_assignments_due_date")
    op.drop_index("ix_learning_assignments_status")
    op.drop_index("ix_learning_assignments_user_id")
    op.drop_index("ix_learning_assignments_page_id")
    op.drop_table("learning_assignments")

    # Drop assessment_questions
    op.drop_index("ix_assessment_questions_order")
    op.drop_index("ix_assessment_questions_assessment_id")
    op.drop_table("assessment_questions")

    # Drop assessments
    op.drop_index("ix_assessments_active")
    op.drop_index("ix_assessments_page_id")
    op.drop_table("assessments")
