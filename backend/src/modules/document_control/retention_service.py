"""Retention service for document retention and review management.

Tracks periodic reviews and retention policies for documents.

Compliance: ISO 15489 - Records management
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.models.page import Page, PageStatus
from src.db.models.retention_policy import RetentionPolicy, DispositionMethod, ExpirationAction
from src.db.models.space import Space
from src.db.models.workspace import Workspace


class RetentionService:
    """Service for managing document retention and disposition.

    Provides:
    - Periodic review tracking
    - Retention policy enforcement
    - Disposition scheduling
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply_retention_policy(
        self,
        page: Page,
        policy: RetentionPolicy,
    ) -> Page:
        """Apply a retention policy to a document.

        Calculates and sets the disposition date based on the policy.

        Args:
            page: Page to apply policy to
            policy: Retention policy to apply

        Returns:
            Updated page
        """
        page.retention_policy_id = policy.id

        # Determine base date for retention calculation
        if policy.retention_from == "effective_date" and page.effective_date:
            base_date = page.effective_date
        elif policy.retention_from == "obsolete_date" and page.status == PageStatus.OBSOLETE.value:
            base_date = page.updated_at
        else:
            base_date = page.created_at

        # Calculate disposition date
        page.disposition_date = base_date + timedelta(days=policy.retention_years * 365)

        await self.db.flush()
        return page

    async def get_documents_due_for_review(
        self,
        organization_id: str,
        include_overdue: bool = True,
        days_ahead: int = 30,
    ) -> list[Page]:
        """Get documents due for periodic review.

        Args:
            organization_id: Organization UUID
            include_overdue: Whether to include overdue reviews
            days_ahead: How many days ahead to look

        Returns:
            List of pages due for review
        """
        now = datetime.now(timezone.utc)
        future_date = now + timedelta(days=days_ahead)

        # Build conditions
        base_conditions = [
            Page.is_controlled == True,
            Page.status == PageStatus.EFFECTIVE.value,
            Page.next_review_date.isnot(None),
        ]

        if include_overdue:
            date_condition = Page.next_review_date <= future_date
        else:
            date_condition = and_(
                Page.next_review_date > now,
                Page.next_review_date <= future_date,
            )

        # Query through hierarchy to filter by org
        result = await self.db.execute(
            select(Page)
            .join(Space, Page.space_id == Space.id)
            .join(Workspace, Space.workspace_id == Workspace.id)
            .where(
                Workspace.organization_id == organization_id,
                and_(*base_conditions),
                date_condition,
            )
            .options(
                joinedload(Page.owner),
                joinedload(Page.custodian),
            )
            .order_by(Page.next_review_date)
        )
        return list(result.unique().scalars().all())

    async def get_documents_due_for_disposition(
        self,
        organization_id: str,
        days_ahead: int = 90,
    ) -> list[Page]:
        """Get documents approaching disposition date.

        Args:
            organization_id: Organization UUID
            days_ahead: How many days ahead to look

        Returns:
            List of pages due for disposition
        """
        future_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)

        result = await self.db.execute(
            select(Page)
            .join(Space, Page.space_id == Space.id)
            .join(Workspace, Space.workspace_id == Workspace.id)
            .where(
                Workspace.organization_id == organization_id,
                Page.disposition_date.isnot(None),
                Page.disposition_date <= future_date,
                Page.status != PageStatus.OBSOLETE.value,
            )
            .options(
                joinedload(Page.owner),
                joinedload(Page.custodian),
                joinedload(Page.retention_policy),
            )
            .order_by(Page.disposition_date)
        )
        return list(result.unique().scalars().all())

    async def complete_review(
        self,
        page: Page,
        reviewed_by_id: str,
        next_review_months: int | None = None,
    ) -> Page:
        """Record completion of a periodic review.

        Args:
            page: Page that was reviewed
            reviewed_by_id: User who performed the review
            next_review_months: Optional override for next review cycle

        Returns:
            Updated page
        """
        now = datetime.now(timezone.utc)

        page.last_reviewed_date = now
        page.last_reviewed_by_id = reviewed_by_id

        # Calculate next review date
        review_cycle = next_review_months or page.review_cycle_months
        if review_cycle:
            page.next_review_date = now + timedelta(days=review_cycle * 30)

        await self.db.flush()
        return page

    async def execute_disposition(
        self,
        page: Page,
        executed_by_id: str,
        reason: str,
    ) -> Page:
        """Execute disposition action on a document.

        Args:
            page: Page to dispose
            executed_by_id: User executing disposition
            reason: Reason for disposition

        Returns:
            Updated page
        """
        policy = page.retention_policy
        if not policy:
            raise ValueError("Page has no retention policy")

        disposition_method = DispositionMethod(policy.disposition_method)

        if disposition_method == DispositionMethod.ARCHIVE:
            # Mark as archived (keep but restrict access)
            page.status = PageStatus.OBSOLETE.value
            page.change_reason = f"Archived per retention policy: {reason}"

        elif disposition_method == DispositionMethod.DESTROY:
            # Soft delete
            page.is_active = False
            page.status = PageStatus.ARCHIVED.value
            page.change_reason = f"Destroyed per retention policy: {reason}"

        elif disposition_method == DispositionMethod.TRANSFER:
            # Mark for transfer
            page.status = PageStatus.OBSOLETE.value
            page.change_reason = f"Transferred per retention policy: {reason}"

        elif disposition_method == DispositionMethod.REVIEW:
            # Just mark as reviewed, no status change
            page.change_reason = f"Disposition reviewed: {reason}"

        await self.db.flush()
        return page

    async def get_retention_policies(
        self,
        organization_id: str,
        active_only: bool = True,
    ) -> list[RetentionPolicy]:
        """Get retention policies for an organization.

        Args:
            organization_id: Organization UUID
            active_only: Whether to include only active policies

        Returns:
            List of retention policies
        """
        query = select(RetentionPolicy).where(
            RetentionPolicy.organization_id == organization_id
        )

        if active_only:
            query = query.where(RetentionPolicy.is_active == True)

        result = await self.db.execute(query.order_by(RetentionPolicy.name))
        return list(result.scalars().all())

    async def create_retention_policy(
        self,
        organization_id: str,
        name: str,
        retention_years: int,
        disposition_method: DispositionMethod,
        description: str | None = None,
        applicable_document_types: list[str] | None = None,
        retention_from: str = "effective_date",
        review_overdue_action: ExpirationAction = ExpirationAction.NOTIFY_ONLY,
        review_overdue_grace_days: int = 30,
        retention_expiry_action: ExpirationAction = ExpirationAction.NOTIFY_ONLY,
        retention_expiry_grace_days: int = 90,
        notify_owner: bool = True,
        notify_custodian: bool = True,
        notify_days_before: list[int] | None = None,
    ) -> RetentionPolicy:
        """Create a new retention policy.

        Args:
            organization_id: Organization UUID
            name: Policy name
            retention_years: How long to keep documents
            disposition_method: How to dispose documents
            description: Optional description
            applicable_document_types: Document types this applies to
            retention_from: When to start counting retention
            review_overdue_action: Action when review is overdue
            review_overdue_grace_days: Grace period for overdue reviews
            retention_expiry_action: Action when retention expires
            retention_expiry_grace_days: Grace period for retention expiry
            notify_owner: Whether to notify owner
            notify_custodian: Whether to notify custodian
            notify_days_before: Days before deadline to notify

        Returns:
            Created policy
        """
        policy = RetentionPolicy(
            organization_id=organization_id,
            name=name,
            description=description,
            applicable_document_types=applicable_document_types or [],
            retention_years=retention_years,
            retention_from=retention_from,
            disposition_method=disposition_method.value,
            review_overdue_action=review_overdue_action.value,
            review_overdue_grace_days=review_overdue_grace_days,
            retention_expiry_action=retention_expiry_action.value,
            retention_expiry_grace_days=retention_expiry_grace_days,
            notify_owner=notify_owner,
            notify_custodian=notify_custodian,
            notify_days_before=notify_days_before or [30, 7, 1],
        )
        self.db.add(policy)
        await self.db.flush()
        return policy

    async def get_applicable_policy(
        self,
        organization_id: str,
        document_type: str | None,
    ) -> RetentionPolicy | None:
        """Get the applicable retention policy for a document type.

        Args:
            organization_id: Organization UUID
            document_type: Document type

        Returns:
            Applicable policy, or None if no matching policy
        """
        policies = await self.get_retention_policies(organization_id)

        # First try to find a policy specific to this document type
        for policy in policies:
            if policy.applicable_document_types and document_type in policy.applicable_document_types:
                return policy

        # Then try to find a catch-all policy (empty applicable_document_types)
        for policy in policies:
            if not policy.applicable_document_types:
                return policy

        return None

    async def get_overdue_review_count(
        self,
        organization_id: str,
    ) -> int:
        """Get count of documents with overdue reviews.

        Args:
            organization_id: Organization UUID

        Returns:
            Count of documents with overdue reviews
        """
        now = datetime.now(timezone.utc)

        result = await self.db.execute(
            select(Page)
            .join(Space, Page.space_id == Space.id)
            .join(Workspace, Space.workspace_id == Workspace.id)
            .where(
                Workspace.organization_id == organization_id,
                Page.is_controlled == True,
                Page.status == PageStatus.EFFECTIVE.value,
                Page.next_review_date.isnot(None),
                Page.next_review_date < now,
            )
        )
        return len(list(result.scalars().all()))
