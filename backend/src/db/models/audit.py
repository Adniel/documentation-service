"""Audit event model for immutable audit trail."""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, UUIDMixin


class AuditEventType(str, Enum):
    """Types of auditable events."""

    # Content events
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"
    CONTENT_VIEWED = "content.viewed"

    # Workflow events
    WORKFLOW_SUBMITTED = "workflow.submitted"
    WORKFLOW_APPROVED = "workflow.approved"
    WORKFLOW_REJECTED = "workflow.rejected"
    WORKFLOW_PUBLISHED = "workflow.published"

    # Access events
    ACCESS_GRANTED = "access.granted"
    ACCESS_REVOKED = "access.revoked"
    ACCESS_DENIED = "access.denied"

    # Auth events
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    AUTH_PASSWORD_CHANGED = "auth.password_changed"

    # Signature events (21 CFR Part 11)
    SIGNATURE_INITIATED = "signature.initiated"
    SIGNATURE_CREATED = "signature.created"
    SIGNATURE_FAILED = "signature.failed"
    SIGNATURE_VERIFIED = "signature.verified"
    SIGNATURE_INVALIDATED = "signature.invalidated"


class AuditEvent(Base, UUIDMixin):
    """Immutable audit event record."""

    __tablename__ = "audit_events"

    # Event metadata
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Actor (who performed the action)
    actor_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )
    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actor_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 max length
    actor_user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Target resource
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    resource_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), nullable=True, index=True
    )
    resource_name: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Event details (using JSON for cross-database compatibility)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Cryptographic chain for tamper detection
    previous_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Composite index for efficient queries
    __table_args__ = (
        Index("ix_audit_events_resource", "resource_type", "resource_id"),
        Index("ix_audit_events_actor_time", "actor_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<AuditEvent {self.event_type} at {self.timestamp}>"
