"""Retention policy model.

Provides configurable document retention and disposition management.

Compliance: ISO 15489 - Records management
"""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization


class DispositionMethod(str, Enum):
    """How to handle documents when retention period expires."""

    ARCHIVE = "archive"       # Move to archive storage (restricted access)
    DESTROY = "destroy"       # Permanently delete
    TRANSFER = "transfer"     # Transfer to external system
    REVIEW = "review"         # Requires manual review before disposition


class ExpirationAction(str, Enum):
    """What action to take when a deadline is reached."""

    NOTIFY_ONLY = "notify_only"             # Send notification, no state change
    AUTO_STATE_CHANGE = "auto_state_change"  # Automatically change document state
    BLOCK_ACCESS = "block_access"            # Block access until reviewed


class RetentionPolicy(Base, UUIDMixin, TimestampMixin):
    """Configurable retention policy for documents.

    Defines how long documents should be kept and what happens
    when various deadlines are reached (review due, retention expiry).

    Organizations can have multiple retention policies for different
    document types or compliance requirements.
    """

    __tablename__ = "retention_policies"

    # Organization this policy belongs to
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    # Policy identification
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Document types this policy applies to (empty = all types)
    applicable_document_types: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Retention period
    retention_years: Mapped[int] = mapped_column(Integer, nullable=False)

    # When to start counting retention period
    # Options: "effective_date", "obsolete_date", "created_date"
    retention_from: Mapped[str] = mapped_column(
        String(50),
        default="effective_date",
        nullable=False,
    )

    # How to dispose of the document
    disposition_method: Mapped[str] = mapped_column(String(50), nullable=False)

    # === Review Overdue Behavior ===

    # What to do when periodic review is overdue
    review_overdue_action: Mapped[str] = mapped_column(
        String(50),
        default=ExpirationAction.NOTIFY_ONLY.value,
        nullable=False,
    )

    # Grace period before taking action (days)
    review_overdue_grace_days: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
    )

    # === Retention Expiry Behavior ===

    # What to do when retention period expires
    retention_expiry_action: Mapped[str] = mapped_column(
        String(50),
        default=ExpirationAction.NOTIFY_ONLY.value,
        nullable=False,
    )

    # Grace period before taking action (days)
    retention_expiry_grace_days: Mapped[int] = mapped_column(
        Integer,
        default=90,
        nullable=False,
    )

    # === Notification Settings ===

    # Who to notify
    notify_owner: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_custodian: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Days before deadline to send notifications
    # Example: [30, 7, 1] = 30 days, 7 days, and 1 day before
    notify_days_before: Mapped[list[int]] = mapped_column(
        JSON,
        default=lambda: [30, 7, 1],
        nullable=False,
    )

    # Whether this policy is active
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")

    def __repr__(self) -> str:
        return f"<RetentionPolicy {self.name}>"

    def applies_to_type(self, document_type: str | None) -> bool:
        """Check if this policy applies to a document type."""
        if not self.applicable_document_types:
            return True  # Empty list = applies to all
        return document_type in self.applicable_document_types

    @property
    def disposition_method_enum(self) -> DispositionMethod:
        """Get disposition method as enum."""
        return DispositionMethod(self.disposition_method)

    @property
    def review_overdue_action_enum(self) -> ExpirationAction:
        """Get review overdue action as enum."""
        return ExpirationAction(self.review_overdue_action)

    @property
    def retention_expiry_action_enum(self) -> ExpirationAction:
        """Get retention expiry action as enum."""
        return ExpirationAction(self.retention_expiry_action)
