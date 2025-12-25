"""Permission model for Sprint 5 Access Control.

Implements dual-dimension access control:
1. Role-based (hierarchical): Owner > Admin > Editor > Reviewer > Viewer
2. Classification-based (clearance): Public < Internal < Confidential < Restricted

Both dimensions must grant access for content to be visible.

Compliance: ISO 9001 §7.5.3, ISO 13485 §4.2.4, 21 CFR §11.10(d)
"""

from datetime import datetime
from enum import IntEnum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.user import User


class Role(IntEnum):
    """Permission roles with numeric values for hierarchy comparison.

    Higher values = more permissions.
    """
    VIEWER = 1
    REVIEWER = 2
    EDITOR = 3
    ADMIN = 4
    OWNER = 5

    @classmethod
    def from_string(cls, value: str) -> "Role":
        """Convert string to Role enum."""
        return cls[value.upper()]

    def __str__(self) -> str:
        return self.name.lower()

    def can_perform(self, required_role: "Role") -> bool:
        """Check if this role meets or exceeds the required role."""
        return self.value >= required_role.value


class ResourceType(str):
    """Resource types for permission scoping."""
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    SPACE = "space"
    PAGE = "page"


class ClassificationLevel(IntEnum):
    """Classification levels for content.

    Higher values = more restricted.
    User clearance must be >= content classification for access.
    """
    PUBLIC = 0       # Anyone can access
    INTERNAL = 1     # Authenticated users
    CONFIDENTIAL = 2 # Clearance level 2+
    RESTRICTED = 3   # Clearance level 3 (highest)

    @classmethod
    def from_string(cls, value: str) -> "ClassificationLevel":
        """Convert string to ClassificationLevel enum."""
        return cls[value.upper()]

    def __str__(self) -> str:
        return self.name.lower()


# Role capabilities mapping
ROLE_CAPABILITIES = {
    Role.VIEWER: {
        "can_read": True,
        "can_comment": False,
        "can_edit": False,
        "can_delete_own": False,
        "can_delete_any": False,
        "can_approve": False,
        "can_manage_members": False,
        "can_manage_settings": False,
        "can_delete_resource": False,
    },
    Role.REVIEWER: {
        "can_read": True,
        "can_comment": True,
        "can_edit": False,
        "can_delete_own": False,
        "can_delete_any": False,
        "can_approve": True,
        "can_manage_members": False,
        "can_manage_settings": False,
        "can_delete_resource": False,
    },
    Role.EDITOR: {
        "can_read": True,
        "can_comment": True,
        "can_edit": True,
        "can_delete_own": True,
        "can_delete_any": False,
        "can_approve": False,
        "can_manage_members": False,
        "can_manage_settings": False,
        "can_delete_resource": False,
    },
    Role.ADMIN: {
        "can_read": True,
        "can_comment": True,
        "can_edit": True,
        "can_delete_own": True,
        "can_delete_any": True,
        "can_approve": True,
        "can_manage_members": True,
        "can_manage_settings": True,
        "can_delete_resource": False,
    },
    Role.OWNER: {
        "can_read": True,
        "can_comment": True,
        "can_edit": True,
        "can_delete_own": True,
        "can_delete_any": True,
        "can_approve": True,
        "can_manage_members": True,
        "can_manage_settings": True,
        "can_delete_resource": True,
    },
}


class Permission(Base, UUIDMixin, TimestampMixin):
    """Permission grant for a user at a specific resource level.

    Permissions are granted at org/workspace/space/page level and
    inherit downward through the content hierarchy.

    Attributes:
        user_id: User who has the permission
        resource_type: Type of resource (organization, workspace, space, page)
        resource_id: UUID of the resource
        role: Role granted (viewer, reviewer, editor, admin, owner)
        granted_by_id: User who granted this permission
        granted_at: When the permission was granted
        reason: Optional reason for the permission grant
        is_active: Whether the permission is active (soft delete)
        expires_at: Optional expiration time for temporary permissions
    """

    __tablename__ = "permissions"

    # User receiving permission
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Resource identification
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    resource_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
    )

    # Role granted
    role: Mapped[int] = mapped_column(
        nullable=False,
    )

    # Audit fields
    granted_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
    )

    granted_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Permission status
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined",
    )

    granted_by: Mapped["User"] = relationship(
        "User",
        foreign_keys=[granted_by_id],
        lazy="joined",
    )

    __table_args__ = (
        # Unique constraint: one permission per user per resource
        UniqueConstraint(
            "user_id",
            "resource_type",
            "resource_id",
            name="uq_permission_user_resource",
        ),
        # Index for fast user permission lookup
        Index("ix_permission_user", "user_id"),
        # Index for fast resource permission lookup
        Index("ix_permission_resource", "resource_type", "resource_id"),
        # Index for filtering active permissions
        Index("ix_permission_active", "is_active"),
    )

    @property
    def role_enum(self) -> Role:
        """Get role as enum."""
        return Role(self.role)

    @role_enum.setter
    def role_enum(self, value: Role) -> None:
        """Set role from enum."""
        self.role = value.value

    def is_valid(self) -> bool:
        """Check if permission is currently valid (active and not expired)."""
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def can_perform(self, required_role: Role) -> bool:
        """Check if this permission grants the required role level."""
        if not self.is_valid():
            return False
        return self.role_enum.can_perform(required_role)

    def __repr__(self) -> str:
        return (
            f"Permission(user_id={self.user_id}, "
            f"resource={self.resource_type}:{self.resource_id}, "
            f"role={self.role_enum})"
        )
