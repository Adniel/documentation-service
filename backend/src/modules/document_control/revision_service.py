"""Revision service for document version management.

Manages major and minor revisions for controlled documents.

Compliance: ISO 13485 §4.2.5 - Changes must be identified and controlled
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.page import Page, PageStatus
from src.db.models.change_request import ChangeRequest, ChangeRequestStatus


class RevisionService:
    """Service for managing document revisions.

    Revision scheme:
    - Revision letter (A, B, C...) - Major changes requiring re-approval
    - Version numbers (1.0, 1.1...) - Minor changes within a revision

    Major revision: A v1.0 → B v1.0 (increments letter, resets version)
    Minor revision: A v1.0 → A v1.1 (increments minor version only)
    """

    # Letters used for revision tracking
    REVISION_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, db: AsyncSession):
        self.db = db

    def _next_revision_letter(self, current: str) -> str:
        """Get the next revision letter.

        A → B → ... → Z → AA → AB → ...

        Args:
            current: Current revision letter

        Returns:
            Next revision letter
        """
        if not current:
            return "A"

        # Single letter
        if len(current) == 1 and current in self.REVISION_LETTERS:
            idx = self.REVISION_LETTERS.index(current)
            if idx < len(self.REVISION_LETTERS) - 1:
                return self.REVISION_LETTERS[idx + 1]
            return "AA"  # After Z comes AA

        # Multi-letter (AA, AB, etc.)
        if len(current) == 2:
            first, second = current[0], current[1]
            if second in self.REVISION_LETTERS:
                idx = self.REVISION_LETTERS.index(second)
                if idx < len(self.REVISION_LETTERS) - 1:
                    return first + self.REVISION_LETTERS[idx + 1]
                # Roll over: AZ → BA
                first_idx = self.REVISION_LETTERS.index(first)
                if first_idx < len(self.REVISION_LETTERS) - 1:
                    return self.REVISION_LETTERS[first_idx + 1] + "A"
                return "AAA"  # After ZZ

        # For longer strings, just append A
        return current + "A"

    def calculate_next_revision(
        self,
        page: Page,
        is_major: bool,
    ) -> tuple[str, int, int]:
        """Calculate the next revision/version numbers.

        Args:
            page: Page to calculate revision for
            is_major: Whether this is a major revision

        Returns:
            Tuple of (revision_letter, major_version, minor_version)
        """
        if is_major:
            # Major: increment revision letter, reset version to 1.0
            new_revision = self._next_revision_letter(page.revision)
            return (new_revision, 1, 0)
        else:
            # Minor: keep revision, increment minor version
            return (page.revision, page.major_version, page.minor_version + 1)

    async def create_revision(
        self,
        page: Page,
        is_major: bool,
        change_reason: str,
        author_id: str,
        title: str | None = None,
    ) -> ChangeRequest:
        """Create a new revision of an effective document.

        For controlled documents, this creates a new ChangeRequest
        with the pending revision metadata.

        Args:
            page: Page to create revision for
            is_major: Whether this is a major revision
            change_reason: Reason for the change (required for major)
            author_id: User creating the revision
            title: Optional title for the change request

        Returns:
            Created ChangeRequest

        Raises:
            ValueError: If page is not effective or change_reason missing for major
        """
        if page.status != PageStatus.EFFECTIVE.value:
            raise ValueError("Can only create revisions of effective documents")

        if is_major and not change_reason:
            raise ValueError("Change reason is required for major revisions")

        # Calculate new revision numbers
        new_revision, new_major, new_minor = self.calculate_next_revision(page, is_major)

        # Generate title if not provided
        if not title:
            title = f"Revision {new_revision} v{new_major}.{new_minor}"

        # Get next CR number for this page
        result = await self.db.execute(
            select(ChangeRequest)
            .where(ChangeRequest.page_id == page.id)
            .order_by(ChangeRequest.number.desc())
            .limit(1)
        )
        last_cr = result.scalar_one_or_none()
        next_number = (last_cr.number + 1) if last_cr else 1

        # Create change request
        change_request = ChangeRequest(
            page_id=page.id,
            title=title,
            description=change_reason,
            number=next_number,
            author_id=author_id,
            branch_name=f"draft/CR-{next_number}-{page.slug[:50]}",
            base_commit_sha=page.git_commit_sha or "HEAD",
            status=ChangeRequestStatus.DRAFT.value,
            is_major_revision=is_major,
            change_reason=change_reason,
            revision_metadata={
                "pending_revision": new_revision,
                "pending_major_version": new_major,
                "pending_minor_version": new_minor,
            },
        )
        self.db.add(change_request)

        await self.db.flush()
        return change_request

    async def apply_revision(
        self,
        change_request: ChangeRequest,
    ) -> Page:
        """Apply revision metadata to page when publishing.

        Called by the publish workflow after approval.

        Args:
            change_request: Approved change request with revision metadata

        Returns:
            Updated page
        """
        page = change_request.page
        revision_metadata = change_request.revision_metadata or {}

        if "pending_revision" in revision_metadata:
            # Update revision info
            page.revision = revision_metadata["pending_revision"]
            page.major_version = revision_metadata.get("pending_major_version", 1)
            page.minor_version = revision_metadata.get("pending_minor_version", 0)

            # Update legacy version field
            page.version = f"{page.major_version}.{page.minor_version}"

            # Update change control fields
            page.change_summary = change_request.title
            page.change_reason = change_request.change_reason

        await self.db.flush()
        return page

    async def get_revision_history(
        self,
        page_id: str,
    ) -> list[dict]:
        """Get complete revision history for a document.

        Returns all published change requests with revision information.

        Args:
            page_id: Page UUID

        Returns:
            List of revision history entries
        """
        result = await self.db.execute(
            select(ChangeRequest)
            .where(
                ChangeRequest.page_id == page_id,
                ChangeRequest.status == ChangeRequestStatus.PUBLISHED.value,
            )
            .order_by(ChangeRequest.published_at.desc())
        )

        history = []
        for cr in result.scalars():
            revision_metadata = cr.revision_metadata or {}
            history.append({
                "change_request_id": str(cr.id),
                "number": cr.number,
                "revision": revision_metadata.get("pending_revision"),
                "version": f"{revision_metadata.get('pending_major_version', 1)}.{revision_metadata.get('pending_minor_version', 0)}",
                "title": cr.title,
                "description": cr.description,
                "change_reason": cr.change_reason,
                "is_major": cr.is_major_revision,
                "author_id": str(cr.author_id),
                "published_at": cr.published_at.isoformat() if cr.published_at else None,
                "published_by_id": str(cr.published_by_id) if cr.published_by_id else None,
            })

        return history

    async def get_current_version_info(
        self,
        page: Page,
    ) -> dict:
        """Get current version information for a page.

        Args:
            page: Page to get version info for

        Returns:
            Dictionary with version details
        """
        return {
            "revision": page.revision,
            "major_version": page.major_version,
            "minor_version": page.minor_version,
            "full_version": page.full_version,
            "version": page.version,
            "change_summary": page.change_summary,
            "change_reason": page.change_reason,
        }
