"""Document metadata service.

Validates and manages document metadata for controlled documents.

Compliance: ISO 13485 §4.2.4 - Document control requirements
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.page import Page, PageStatus
from src.db.models.document_lifecycle import DocumentStatus


class DocumentMetadataService:
    """Service for validating and managing document metadata.

    Ensures controlled documents have required metadata
    at each lifecycle stage.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    def validate_for_transition(
        self,
        page: Page,
        from_status: DocumentStatus,
        to_status: DocumentStatus,
    ) -> list[str]:
        """Validate document has required metadata for a status transition.

        Args:
            page: Page to validate
            from_status: Current status
            to_status: Target status

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Non-controlled documents skip validation
        if not page.is_controlled:
            return errors

        # === DRAFT → IN_REVIEW ===
        if to_status == DocumentStatus.IN_REVIEW:
            if not page.document_number:
                errors.append("Document number is required before review")
            if not page.owner_id:
                errors.append("Document owner must be assigned")

        # === IN_REVIEW → APPROVED ===
        if to_status == DocumentStatus.APPROVED:
            if not page.document_type:
                errors.append("Document type must be specified")

        # === APPROVED → EFFECTIVE ===
        if to_status == DocumentStatus.EFFECTIVE:
            # effective_date is set by the endpoint during transition, so we don't validate it here
            # Only check that if both dates exist, effective isn't before approved
            if page.effective_date and page.approved_date:
                if page.effective_date < page.approved_date:
                    errors.append("Effective date cannot be before approved date")
            # next_review_date is calculated during transition if review_cycle_months is set

            # Required retention policy for certain document types
            if page.document_type in ("record", "form") and not page.retention_policy_id:
                errors.append(f"Retention policy required for {page.document_type} documents")

        return errors

    def validate_major_revision(
        self,
        page: Page,
        change_reason: str | None,
    ) -> list[str]:
        """Validate requirements for a major revision.

        Args:
            page: Page being revised
            change_reason: Reason for the change

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not change_reason:
            errors.append("Change reason is required for major revisions")

        if len(change_reason or "") < 10:
            errors.append("Change reason must be at least 10 characters")

        return errors

    async def set_effective(
        self,
        page: Page,
        effective_date: datetime,
        set_by_id: str,
    ) -> Page:
        """Make a document effective and calculate next review date.

        Args:
            page: Page to make effective
            effective_date: When document becomes effective
            set_by_id: User setting effective status

        Returns:
            Updated page
        """
        page.effective_date = effective_date
        page.status = PageStatus.EFFECTIVE.value

        # Calculate next review date if review cycle is set
        if page.review_cycle_months:
            page.next_review_date = effective_date + timedelta(
                days=page.review_cycle_months * 30
            )

        await self.db.flush()
        return page

    async def set_approved(
        self,
        page: Page,
        approved_by_id: str,
        approved_date: datetime | None = None,
    ) -> Page:
        """Mark a document as approved.

        Args:
            page: Page to approve
            approved_by_id: User approving the document
            approved_date: Optional approval date (defaults to now)

        Returns:
            Updated page
        """
        page.approved_date = approved_date or datetime.now(timezone.utc)
        page.approved_by_id = approved_by_id
        page.status = PageStatus.APPROVED.value

        await self.db.flush()
        return page

    async def mark_obsolete(
        self,
        page: Page,
        superseded_by_id: str | None,
        reason: str,
        marked_by_id: str,
    ) -> Page:
        """Mark a document as obsolete.

        Args:
            page: Page to mark obsolete
            superseded_by_id: ID of document that supersedes this one
            reason: Reason for obsolescence
            marked_by_id: User marking the document obsolete

        Returns:
            Updated page
        """
        page.status = PageStatus.OBSOLETE.value
        page.change_reason = reason

        if superseded_by_id:
            page.superseded_by_id = superseded_by_id
            # Also update the new document to reference what it supersedes
            from sqlalchemy import select
            result = await self.db.execute(
                select(Page).where(Page.id == superseded_by_id)
            )
            new_doc = result.scalar_one_or_none()
            if new_doc:
                new_doc.supersedes_id = page.id

        await self.db.flush()
        return page

    async def assign_owner(
        self,
        page: Page,
        owner_id: str,
        custodian_id: str | None = None,
    ) -> Page:
        """Assign owner and optional custodian to a document.

        Args:
            page: Page to update
            owner_id: New owner user ID
            custodian_id: Optional custodian user ID

        Returns:
            Updated page
        """
        page.owner_id = owner_id
        if custodian_id is not None:
            page.custodian_id = custodian_id

        await self.db.flush()
        return page

    async def set_review_schedule(
        self,
        page: Page,
        review_cycle_months: int,
        next_review_date: datetime | None = None,
    ) -> Page:
        """Set periodic review schedule for a document.

        Args:
            page: Page to update
            review_cycle_months: Review cycle in months
            next_review_date: Optional specific next review date

        Returns:
            Updated page
        """
        page.review_cycle_months = review_cycle_months

        if next_review_date:
            page.next_review_date = next_review_date
        elif page.effective_date:
            page.next_review_date = page.effective_date + timedelta(
                days=review_cycle_months * 30
            )
        else:
            page.next_review_date = datetime.now(timezone.utc) + timedelta(
                days=review_cycle_months * 30
            )

        await self.db.flush()
        return page

    async def set_training_requirement(
        self,
        page: Page,
        requires_training: bool,
        validity_months: int | None = None,
    ) -> Page:
        """Set training requirement for a document.

        Args:
            page: Page to update
            requires_training: Whether training is required
            validity_months: How long training is valid

        Returns:
            Updated page
        """
        page.requires_training = requires_training
        page.training_validity_months = validity_months if requires_training else None

        await self.db.flush()
        return page

    def get_metadata_summary(self, page: Page) -> dict:
        """Get a summary of document metadata.

        Args:
            page: Page to summarize

        Returns:
            Dictionary of metadata
        """
        return {
            "document_number": page.document_number,
            "document_type": page.document_type,
            "is_controlled": page.is_controlled,
            "revision": page.revision,
            "version": f"{page.major_version}.{page.minor_version}",
            "full_version": page.full_version,
            "status": page.status,
            "classification": page.classification,
            "owner_id": str(page.owner_id) if page.owner_id else None,
            "custodian_id": str(page.custodian_id) if page.custodian_id else None,
            "approved_date": page.approved_date.isoformat() if page.approved_date else None,
            "effective_date": page.effective_date.isoformat() if page.effective_date else None,
            "next_review_date": page.next_review_date.isoformat() if page.next_review_date else None,
            "last_reviewed_date": page.last_reviewed_date.isoformat() if page.last_reviewed_date else None,
            "review_cycle_months": page.review_cycle_months,
            "disposition_date": page.disposition_date.isoformat() if page.disposition_date else None,
            "requires_training": page.requires_training,
            "training_validity_months": page.training_validity_months,
            "change_summary": page.change_summary,
            "change_reason": page.change_reason,
            "supersedes_id": str(page.supersedes_id) if page.supersedes_id else None,
            "superseded_by_id": str(page.superseded_by_id) if page.superseded_by_id else None,
        }

    def get_missing_required_fields(
        self,
        page: Page,
        target_status: DocumentStatus | None = None,
    ) -> list[str]:
        """Get list of missing required fields.

        Args:
            page: Page to check
            target_status: Optional target status to check against

        Returns:
            List of missing field names
        """
        missing = []

        if not page.is_controlled:
            return missing

        # Always required for controlled documents
        if not page.document_number:
            missing.append("document_number")
        if not page.document_type:
            missing.append("document_type")
        if not page.owner_id:
            missing.append("owner_id")

        # Required for specific statuses
        if target_status == DocumentStatus.EFFECTIVE or page.status == PageStatus.EFFECTIVE.value:
            if not page.effective_date:
                missing.append("effective_date")
            if page.review_cycle_months and not page.next_review_date:
                missing.append("next_review_date")

        return missing
