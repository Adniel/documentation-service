"""Document numbering service.

Generates unique document numbers per organization and document type.

Compliance: ISO 13485 §4.2.4 - Unique document identification
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.document_lifecycle import DocumentType, DEFAULT_DOCUMENT_PREFIXES
from src.db.models.document_number import DocumentNumberSequence
from src.db.models.page import Page


class DocumentNumberingService:
    """Service for generating unique document numbers.

    Uses database-level locking (SELECT FOR UPDATE) to prevent
    race conditions when multiple users request numbers simultaneously.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_document_number(
        self,
        organization_id: str,
        document_type: DocumentType | str,
        custom_prefix: str | None = None,
    ) -> str:
        """Generate the next document number for an organization/type.

        Uses SELECT FOR UPDATE to ensure atomicity and prevent duplicate numbers.

        Args:
            organization_id: Organization UUID
            document_type: Type of document (SOP, WI, etc.)
            custom_prefix: Optional custom prefix (overrides default)

        Returns:
            Generated document number (e.g., "SOP-001")
        """
        # Normalize document type to string
        doc_type_str = (
            document_type.value
            if isinstance(document_type, DocumentType)
            else document_type
        )

        # Get or create sequence with row lock
        result = await self.db.execute(
            select(DocumentNumberSequence)
            .where(
                DocumentNumberSequence.organization_id == organization_id,
                DocumentNumberSequence.document_type == doc_type_str,
            )
            .with_for_update()
        )
        sequence = result.scalar_one_or_none()

        if not sequence:
            # Create new sequence
            prefix = custom_prefix
            if not prefix:
                try:
                    dt = DocumentType(doc_type_str)
                    prefix = DEFAULT_DOCUMENT_PREFIXES.get(dt, doc_type_str.upper())
                except ValueError:
                    prefix = doc_type_str.upper()

            sequence = DocumentNumberSequence(
                organization_id=organization_id,
                document_type=doc_type_str,
                prefix=prefix,
                format_pattern="{prefix}-{number:03d}",
                current_number=0,
            )
            self.db.add(sequence)

        # Generate next number
        document_number = sequence.generate_next()

        await self.db.flush()
        return document_number

    async def validate_document_number(
        self,
        document_number: str,
        exclude_page_id: str | None = None,
    ) -> bool:
        """Check if a document number is unique.

        Args:
            document_number: Number to validate
            exclude_page_id: Optional page ID to exclude (for updates)

        Returns:
            True if number is unique, False if already exists
        """
        query = select(Page).where(Page.document_number == document_number)
        if exclude_page_id:
            query = query.where(Page.id != exclude_page_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none() is None

    async def configure_sequence(
        self,
        organization_id: str,
        document_type: DocumentType | str,
        prefix: str,
        format_pattern: str = "{prefix}-{number:03d}",
    ) -> DocumentNumberSequence:
        """Configure numbering for a document type.

        Args:
            organization_id: Organization UUID
            document_type: Type of document
            prefix: Prefix for generated numbers
            format_pattern: Python str.format() pattern

        Returns:
            Created or updated sequence
        """
        doc_type_str = (
            document_type.value
            if isinstance(document_type, DocumentType)
            else document_type
        )

        result = await self.db.execute(
            select(DocumentNumberSequence).where(
                DocumentNumberSequence.organization_id == organization_id,
                DocumentNumberSequence.document_type == doc_type_str,
            )
        )
        sequence = result.scalar_one_or_none()

        if sequence:
            sequence.prefix = prefix
            sequence.format_pattern = format_pattern
        else:
            sequence = DocumentNumberSequence(
                organization_id=organization_id,
                document_type=doc_type_str,
                prefix=prefix,
                format_pattern=format_pattern,
                current_number=0,
            )
            self.db.add(sequence)

        await self.db.flush()
        return sequence

    async def get_sequence(
        self,
        organization_id: str,
        document_type: DocumentType | str,
    ) -> DocumentNumberSequence | None:
        """Get sequence for an organization/type.

        Args:
            organization_id: Organization UUID
            document_type: Type of document

        Returns:
            Sequence if exists, None otherwise
        """
        doc_type_str = (
            document_type.value
            if isinstance(document_type, DocumentType)
            else document_type
        )

        result = await self.db.execute(
            select(DocumentNumberSequence).where(
                DocumentNumberSequence.organization_id == organization_id,
                DocumentNumberSequence.document_type == doc_type_str,
            )
        )
        return result.scalar_one_or_none()

    async def preview_next_number(
        self,
        organization_id: str,
        document_type: DocumentType | str,
    ) -> str | None:
        """Preview what the next document number would be.

        Does not increment the sequence.

        Args:
            organization_id: Organization UUID
            document_type: Type of document

        Returns:
            Preview of next number, or None if no sequence exists
        """
        sequence = await self.get_sequence(organization_id, document_type)
        if sequence:
            return sequence.preview_next()
        return None

    async def list_sequences(
        self,
        organization_id: str,
    ) -> list[DocumentNumberSequence]:
        """List all numbering sequences for an organization.

        Args:
            organization_id: Organization UUID

        Returns:
            List of sequences
        """
        result = await self.db.execute(
            select(DocumentNumberSequence)
            .where(DocumentNumberSequence.organization_id == organization_id)
            .order_by(DocumentNumberSequence.document_type)
        )
        return list(result.scalars().all())
