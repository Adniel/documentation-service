"""Space model - container for pages, organized by Diátaxis type."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.workspace import Workspace
    from src.db.models.page import Page


class DiataxisType(str, Enum):
    """Diátaxis documentation types."""

    TUTORIAL = "tutorial"
    HOW_TO = "how_to"
    REFERENCE = "reference"
    EXPLANATION = "explanation"
    MIXED = "mixed"


class Space(Base, UUIDMixin, TimestampMixin):
    """Space - container for pages, can be typed by Diátaxis category."""

    __tablename__ = "spaces"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Diátaxis type
    diataxis_type: Mapped[str] = mapped_column(
        String(50), default=DiataxisType.MIXED.value, nullable=False
    )

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Classification (0-3: Public, Internal, Confidential, Restricted)
    classification: Mapped[int] = mapped_column(default=0, nullable=False)

    # Ordering
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Parent workspace
    workspace_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("workspaces.id"), nullable=False
    )

    # Optional parent space (for nested spaces)
    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("spaces.id"), nullable=True
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="spaces")
    parent: Mapped["Space | None"] = relationship(
        "Space", remote_side="Space.id", back_populates="children"
    )
    children: Mapped[list["Space"]] = relationship("Space", back_populates="parent")
    pages: Mapped[list["Page"]] = relationship(
        "Page", back_populates="space", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Space {self.name}>"
