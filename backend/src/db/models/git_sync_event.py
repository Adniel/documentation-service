"""GitSyncEvent model - Track Git sync operations for audit trail.

Sprint 13: Git Remote Support
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization
    from src.db.models.user import User


class SyncEventType(str, Enum):
    """Types of Git sync events."""

    PUSH = "push"
    PULL = "pull"
    FETCH = "fetch"
    CLONE = "clone"
    CONFLICT = "conflict"
    ERROR = "error"


class SyncDirection(str, Enum):
    """Direction of sync operation."""

    OUTBOUND = "outbound"  # Local -> Remote
    INBOUND = "inbound"  # Remote -> Local


class SyncStatus(str, Enum):
    """Status of sync operation."""

    SUCCESS = "success"
    FAILED = "failed"
    CONFLICT = "conflict"
    IN_PROGRESS = "in_progress"


class GitSyncEvent(Base, UUIDMixin):
    """Record of a Git sync operation.

    Provides audit trail for all sync operations between local and remote repos.
    """

    __tablename__ = "git_sync_events"

    # Organization this event belongs to
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Event details
    event_type: Mapped[SyncEventType] = mapped_column(
        SqlEnum(SyncEventType, name="sync_event_type_enum"),
        nullable=False,
    )

    direction: Mapped[SyncDirection] = mapped_column(
        SqlEnum(SyncDirection, name="sync_direction_enum"),
        nullable=False,
    )

    status: Mapped[SyncStatus] = mapped_column(
        SqlEnum(SyncStatus, name="sync_status_enum"),
        nullable=False,
    )

    # Branch involved
    branch_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Commit SHAs
    commit_sha_before: Mapped[str | None] = mapped_column(String(40), nullable=True)
    commit_sha_after: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Error details if failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Files affected (JSON array of paths)
    files_changed: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Who triggered this sync (null for webhook/automated)
    triggered_by_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True
    )

    # Trigger source
    trigger_source: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # manual, webhook, scheduled, page_save

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    triggered_by: Mapped["User | None"] = relationship("User")

    def __repr__(self) -> str:
        return f"<GitSyncEvent {self.event_type.value} {self.status.value} org={self.organization_id}>"

    @property
    def duration_seconds(self) -> float | None:
        """Calculate duration of sync operation."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
