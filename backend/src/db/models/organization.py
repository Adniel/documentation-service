"""Organization model - top level of content hierarchy."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.user import User
    from src.db.models.workspace import Workspace


# Association table for organization members
organization_members = Table(
    "organization_members",
    Base.metadata,
    Column("organization_id", UUID(as_uuid=False), ForeignKey("organizations.id"), primary_key=True),
    Column("user_id", UUID(as_uuid=False), ForeignKey("users.id"), primary_key=True),
    Column("role", String(50), nullable=False, default="viewer"),
)


class Organization(Base, UUIDMixin, TimestampMixin):
    """Organization - top level container for workspaces."""

    __tablename__ = "organizations"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Owner
    owner_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False
    )

    # Git repository path for this organization (local)
    git_repo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Git Remote Configuration (Sprint 13)
    git_remote_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    git_remote_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # github, gitlab, gitea, custom
    git_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    git_sync_strategy: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # push_only, pull_only, bidirectional
    git_default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    git_last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    git_sync_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # synced, pending, error, conflict
    git_webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id])
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary=organization_members,
        back_populates="organizations",
    )
    workspaces: Mapped[list["Workspace"]] = relationship(
        "Workspace", back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"
