"""Document number sequence model.

Provides auto-incrementing document numbers per organization and document type.

Compliance: ISO 13485 §4.2.4 - Unique document identification
"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization


class DocumentNumberSequence(Base, UUIDMixin, TimestampMixin):
    """Auto-incrementing sequence for document numbers per org/type.

    Each organization has separate sequences per document type.
    The sequence is incremented atomically using SELECT FOR UPDATE
    to prevent race conditions.

    Example generated numbers:
    - SOP-001, SOP-002 (default format)
    - SOP-QMS-001 (custom prefix)
    - DOC-2025-0001 (custom format with year)
    """

    __tablename__ = "document_number_sequences"

    # Organization this sequence belongs to
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id"),
        nullable=False,
    )

    # Document type this sequence is for
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Prefix for generated numbers (e.g., "SOP", "SOP-QMS")
    prefix: Mapped[str] = mapped_column(String(50), nullable=False)

    # Current sequence number (last used)
    current_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Format pattern using Python str.format() syntax
    # Available tokens: {prefix}, {number}, {number:03d} (zero-padded)
    format_pattern: Mapped[str] = mapped_column(
        String(100),
        default="{prefix}-{number:03d}",
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")

    # Ensure unique sequence per org/type
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "document_type",
            name="uq_org_doctype_sequence",
        ),
    )

    def __repr__(self) -> str:
        return f"<DocumentNumberSequence {self.prefix} @ {self.current_number}>"

    def generate_next(self) -> str:
        """Generate the next document number.

        Note: This method increments current_number. The caller must
        use SELECT FOR UPDATE and commit the transaction to ensure
        atomicity.
        """
        self.current_number += 1
        return self.format_pattern.format(
            prefix=self.prefix,
            number=self.current_number,
        )

    def preview_next(self) -> str:
        """Preview what the next document number would be without incrementing."""
        return self.format_pattern.format(
            prefix=self.prefix,
            number=self.current_number + 1,
        )
