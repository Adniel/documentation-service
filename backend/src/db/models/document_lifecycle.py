"""Document lifecycle status and transitions.

Provides configurable document lifecycle management for ISO 9001/13485 compliance.

Compliance: ISO 9001 §7.5.2, ISO 13485 §4.2.4
"""

from enum import IntEnum, Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization


class DocumentStatus(str, Enum):
    """Document lifecycle status.

    Default 5-state lifecycle model:
    DRAFT -> IN_REVIEW -> APPROVED -> EFFECTIVE -> OBSOLETE
    """

    DRAFT = "draft"              # Work in progress, editable
    IN_REVIEW = "in_review"      # Submitted for approval, not editable
    APPROVED = "approved"        # Approved, awaiting effective date
    EFFECTIVE = "effective"      # Current active version
    OBSOLETE = "obsolete"        # Superseded or retired


class DocumentType(str, Enum):
    """Standard document types for regulated environments."""

    SOP = "sop"                    # Standard Operating Procedure
    WI = "wi"                      # Work Instruction
    FORM = "form"                  # Form/Template
    POLICY = "policy"              # Policy Document
    RECORD = "record"              # Record (filled form)
    SPECIFICATION = "specification"  # Technical Specification
    MANUAL = "manual"              # Manual/Handbook
    GUIDELINE = "guideline"        # Guideline
    PROTOCOL = "protocol"          # Protocol (e.g., test protocol)


# Default prefixes for document numbering
DEFAULT_DOCUMENT_PREFIXES: dict[DocumentType, str] = {
    DocumentType.SOP: "SOP",
    DocumentType.WI: "WI",
    DocumentType.FORM: "FRM",
    DocumentType.POLICY: "POL",
    DocumentType.RECORD: "REC",
    DocumentType.SPECIFICATION: "SPEC",
    DocumentType.MANUAL: "MAN",
    DocumentType.GUIDELINE: "GL",
    DocumentType.PROTOCOL: "PROT",
}


# Default allowed transitions
DEFAULT_TRANSITIONS: dict[DocumentStatus, list[DocumentStatus]] = {
    DocumentStatus.DRAFT: [DocumentStatus.IN_REVIEW],
    DocumentStatus.IN_REVIEW: [DocumentStatus.DRAFT, DocumentStatus.APPROVED],
    DocumentStatus.APPROVED: [DocumentStatus.EFFECTIVE, DocumentStatus.DRAFT],
    DocumentStatus.EFFECTIVE: [DocumentStatus.OBSOLETE],
    DocumentStatus.OBSOLETE: [],  # Terminal state
}


# Minimum role required for each transition
from src.db.models.permission import Role

TRANSITION_PERMISSIONS: dict[tuple[DocumentStatus, DocumentStatus], Role] = {
    (DocumentStatus.DRAFT, DocumentStatus.IN_REVIEW): Role.EDITOR,       # Author submits
    (DocumentStatus.IN_REVIEW, DocumentStatus.DRAFT): Role.REVIEWER,     # Reviewer rejects
    (DocumentStatus.IN_REVIEW, DocumentStatus.APPROVED): Role.REVIEWER,  # Reviewer approves
    (DocumentStatus.APPROVED, DocumentStatus.EFFECTIVE): Role.ADMIN,     # Admin activates
    (DocumentStatus.APPROVED, DocumentStatus.DRAFT): Role.ADMIN,         # Admin reverts
    (DocumentStatus.EFFECTIVE, DocumentStatus.OBSOLETE): Role.ADMIN,     # Admin obsoletes
}


class LifecycleConfig(Base, UUIDMixin, TimestampMixin):
    """Organization-specific document lifecycle configuration.

    Allows organizations to customize document lifecycle states and transitions.
    If use_defaults is True, the DEFAULT_TRANSITIONS are used.
    """

    __tablename__ = "lifecycle_configs"

    # Organization this config belongs to
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id"),
        nullable=False,
        unique=True,
    )

    # Custom states (JSON array)
    # Example: [{"name": "draft", "label": "Draft", "editable": true, "visible": false}]
    custom_states: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

    # Custom transitions (JSON array)
    # Example: [{"from": "draft", "to": "in_review", "required_role": "editor"}]
    custom_transitions: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

    # Use default states/transitions if custom not defined
    use_defaults: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")

    def __repr__(self) -> str:
        return f"<LifecycleConfig org={self.organization_id}>"

    def get_allowed_transitions(self, from_status: DocumentStatus) -> list[DocumentStatus]:
        """Get allowed transitions from a status."""
        if self.use_defaults or not self.custom_transitions:
            return DEFAULT_TRANSITIONS.get(from_status, [])

        return [
            DocumentStatus(t["to"])
            for t in self.custom_transitions
            if t["from"] == from_status.value
        ]

    def get_transition_role(
        self, from_status: DocumentStatus, to_status: DocumentStatus
    ) -> Role | None:
        """Get required role for a transition."""
        if self.use_defaults or not self.custom_transitions:
            return TRANSITION_PERMISSIONS.get((from_status, to_status))

        for t in self.custom_transitions:
            if t["from"] == from_status.value and t["to"] == to_status.value:
                return Role[t.get("required_role", "admin").upper()]

        return None
