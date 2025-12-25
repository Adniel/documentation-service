"""Approval workflow models.

Provides multi-step approval workflows integrated with Change Requests.

Compliance: ISO 9001 §7.5.2 - Documents must be approved before release
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.change_request import ChangeRequest
    from src.db.models.organization import Organization
    from src.db.models.user import User


class ApprovalDecision(str, Enum):
    """Possible decisions for an approval step."""

    APPROVED = "approved"      # Step approved
    REJECTED = "rejected"      # Step rejected, returns to draft
    SKIPPED = "skipped"        # Optional step skipped


class ApprovalMatrix(Base, UUIDMixin, TimestampMixin):
    """Defines approval workflow steps for document types.

    An approval matrix specifies what approval steps are required
    for documents of certain types. Steps can be sequential or parallel,
    required or optional.

    Example steps configuration:
    [
        {"order": 1, "name": "Technical Review", "role": "reviewer", "required": true},
        {"order": 2, "name": "QA Approval", "role": "qa_approver", "required": true},
        {"order": 3, "name": "Management Sign-off", "role": "admin", "required": false}
    ]
    """

    __tablename__ = "approval_matrices"

    # Organization this matrix belongs to
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    # Matrix identification
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Document types this matrix applies to (empty = all types)
    applicable_document_types: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Approval steps (ordered list)
    # Each step: {"order": int, "name": str, "role": str, "required": bool}
    steps: Mapped[list[dict]] = mapped_column(JSON, nullable=False)

    # Whether steps must be completed in order
    require_sequential: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Whether this matrix is active
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")

    def __repr__(self) -> str:
        return f"<ApprovalMatrix {self.name}>"

    def get_step(self, order: int) -> dict | None:
        """Get a specific step by order number."""
        for step in self.steps:
            if step.get("order") == order:
                return step
        return None

    def get_required_steps(self) -> list[dict]:
        """Get all required steps."""
        return [s for s in self.steps if s.get("required", True)]

    def get_total_steps(self) -> int:
        """Get total number of steps."""
        return len(self.steps)

    def applies_to_type(self, document_type: str | None) -> bool:
        """Check if this matrix applies to a document type."""
        if not self.applicable_document_types:
            return True  # Empty list = applies to all
        return document_type in self.applicable_document_types


class ApprovalRecord(Base, UUIDMixin, TimestampMixin):
    """Individual approval decision within a change request workflow.

    Each time an approver makes a decision (approve, reject, skip),
    a record is created. This provides a complete audit trail of
    the approval process.
    """

    __tablename__ = "approval_records"

    # Change request being approved
    change_request_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("change_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Which step this approval is for
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Who made the decision
    approver_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
    )

    # The decision
    decision: Mapped[str] = mapped_column(String(50), nullable=False)

    # Optional comment explaining the decision
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # When the decision was made
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    change_request: Mapped["ChangeRequest"] = relationship(
        "ChangeRequest",
        back_populates="approval_records",
    )
    approver: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ApprovalRecord step={self.step_order} decision={self.decision}>"

    @property
    def decision_enum(self) -> ApprovalDecision:
        """Get decision as enum."""
        return ApprovalDecision(self.decision)
