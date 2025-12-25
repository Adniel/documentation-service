"""Approval service for document approval workflows.

Manages multi-step approval workflows integrated with Change Requests.

Compliance: ISO 9001 §7.5.2 - Documents must be approved before release
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.models.approval import ApprovalMatrix, ApprovalRecord, ApprovalDecision
from src.db.models.change_request import ChangeRequest, ChangeRequestStatus
from src.db.models.page import Page
from src.db.models.space import Space
from src.db.models.workspace import Workspace


class ApprovalService:
    """Service for managing document approval workflows.

    Provides:
    - Approval matrix management
    - Workflow initiation and progression
    - Approval/rejection recording
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_applicable_matrix(
        self,
        organization_id: str,
        document_type: str | None,
    ) -> ApprovalMatrix | None:
        """Find the approval matrix applicable to a document type.

        Args:
            organization_id: Organization UUID
            document_type: Document type

        Returns:
            Applicable matrix, or None
        """
        result = await self.db.execute(
            select(ApprovalMatrix).where(
                ApprovalMatrix.organization_id == organization_id,
                ApprovalMatrix.is_active == True,
            )
        )
        matrices = result.scalars().all()

        # First try type-specific matrix
        for matrix in matrices:
            if matrix.applicable_document_types and document_type in matrix.applicable_document_types:
                return matrix

        # Then try catch-all matrix
        for matrix in matrices:
            if not matrix.applicable_document_types:
                return matrix

        return None

    async def initiate_approval(
        self,
        change_request: ChangeRequest,
        initiated_by_id: str,
    ) -> ChangeRequest:
        """Start approval workflow for a change request.

        Args:
            change_request: Change request to start approval for
            initiated_by_id: User initiating approval

        Returns:
            Updated change request
        """
        page = change_request.page

        # Get organization ID through hierarchy
        org_id = None
        if page.space and page.space.workspace:
            org_id = page.space.workspace.organization_id

        # Find applicable matrix
        matrix = None
        if org_id:
            matrix = await self.get_applicable_matrix(
                organization_id=org_id,
                document_type=page.document_type,
            )

        if matrix:
            change_request.approval_matrix_id = matrix.id
            change_request.current_approval_step = 1
            change_request.approval_status = "in_progress"
        else:
            # No matrix = single-step approval (reviewer approves)
            change_request.approval_status = "pending"

        change_request.status = ChangeRequestStatus.IN_REVIEW.value
        change_request.submitted_at = datetime.now(timezone.utc)

        await self.db.flush()
        return change_request

    async def record_approval(
        self,
        change_request_id: str,
        approver_id: str,
        decision: ApprovalDecision,
        comment: str | None = None,
    ) -> tuple[ChangeRequest, bool]:
        """Record an approval decision.

        Args:
            change_request_id: Change request UUID
            approver_id: User making decision
            decision: Approval decision
            comment: Optional comment

        Returns:
            Tuple of (change_request, is_workflow_complete)
        """
        result = await self.db.execute(
            select(ChangeRequest)
            .where(ChangeRequest.id == change_request_id)
            .options(joinedload(ChangeRequest.approval_matrix))
        )
        cr = result.scalar_one_or_none()
        if not cr:
            raise ValueError(f"Change request not found: {change_request_id}")

        now = datetime.now(timezone.utc)

        # Handle simple approval (no matrix)
        if not cr.approval_matrix:
            cr.approval_status = decision.value
            cr.status = (
                ChangeRequestStatus.APPROVED.value
                if decision == ApprovalDecision.APPROVED
                else ChangeRequestStatus.CHANGES_REQUESTED.value
            )
            cr.reviewed_at = now
            cr.reviewer_id = approver_id
            cr.review_comment = comment

            await self.db.flush()
            return cr, True

        # Get current step from matrix
        matrix = cr.approval_matrix
        current_step = matrix.get_step(cr.current_approval_step)
        if not current_step:
            raise ValueError(f"Invalid approval step: {cr.current_approval_step}")

        # Record this approval
        record = ApprovalRecord(
            change_request_id=cr.id,
            step_order=cr.current_approval_step,
            step_name=current_step["name"],
            approver_id=approver_id,
            decision=decision.value,
            comment=comment,
            decided_at=now,
        )
        self.db.add(record)

        # Handle rejection
        if decision == ApprovalDecision.REJECTED:
            cr.approval_status = "rejected"
            cr.status = ChangeRequestStatus.CHANGES_REQUESTED.value
            cr.reviewed_at = now
            cr.review_comment = comment

            await self.db.flush()
            return cr, True

        # Move to next step
        if cr.current_approval_step < matrix.get_total_steps():
            next_step = matrix.get_step(cr.current_approval_step + 1)
            if next_step:
                if next_step.get("required", True):
                    cr.current_approval_step += 1
                    await self.db.flush()
                    return cr, False
                else:
                    # Skip optional steps
                    cr.current_approval_step += 1
                    # Recursively check next step
                    return await self._advance_to_required_step(cr)

        # All steps complete
        cr.approval_status = "approved"
        cr.status = ChangeRequestStatus.APPROVED.value
        cr.reviewed_at = now

        await self.db.flush()
        return cr, True

    async def _advance_to_required_step(
        self,
        cr: ChangeRequest,
    ) -> tuple[ChangeRequest, bool]:
        """Advance to the next required step, skipping optional ones.

        Args:
            cr: Change request

        Returns:
            Tuple of (change_request, is_workflow_complete)
        """
        matrix = cr.approval_matrix
        if not matrix:
            return cr, True

        while cr.current_approval_step <= matrix.get_total_steps():
            step = matrix.get_step(cr.current_approval_step)
            if not step:
                break

            if step.get("required", True):
                # Found required step, stop here
                await self.db.flush()
                return cr, False

            # Skip optional step
            cr.current_approval_step += 1

        # All steps complete
        cr.approval_status = "approved"
        cr.status = ChangeRequestStatus.APPROVED.value
        cr.reviewed_at = datetime.now(timezone.utc)

        await self.db.flush()
        return cr, True

    async def skip_optional_step(
        self,
        change_request_id: str,
        skipped_by_id: str,
        reason: str | None = None,
    ) -> tuple[ChangeRequest, bool]:
        """Skip an optional approval step.

        Args:
            change_request_id: Change request UUID
            skipped_by_id: User skipping the step
            reason: Optional reason for skipping

        Returns:
            Tuple of (change_request, is_workflow_complete)
        """
        return await self.record_approval(
            change_request_id=change_request_id,
            approver_id=skipped_by_id,
            decision=ApprovalDecision.SKIPPED,
            comment=reason,
        )

    async def get_pending_approvals(
        self,
        approver_id: str,
    ) -> list[ChangeRequest]:
        """Get change requests pending approval by a user.

        Args:
            approver_id: User UUID

        Returns:
            List of change requests awaiting approval
        """
        # Get CRs in review status where user is reviewer
        # or where user matches current step requirements
        result = await self.db.execute(
            select(ChangeRequest)
            .where(
                ChangeRequest.status == ChangeRequestStatus.IN_REVIEW.value,
                ChangeRequest.approval_status.in_(["pending", "in_progress"]),
            )
            .options(
                joinedload(ChangeRequest.page),
                joinedload(ChangeRequest.approval_matrix),
            )
        )
        return list(result.unique().scalars().all())

    async def get_approval_history(
        self,
        change_request_id: str,
    ) -> list[ApprovalRecord]:
        """Get approval history for a change request.

        Args:
            change_request_id: Change request UUID

        Returns:
            List of approval records
        """
        result = await self.db.execute(
            select(ApprovalRecord)
            .where(ApprovalRecord.change_request_id == change_request_id)
            .options(joinedload(ApprovalRecord.approver))
            .order_by(ApprovalRecord.step_order, ApprovalRecord.decided_at)
        )
        return list(result.unique().scalars().all())

    async def create_approval_matrix(
        self,
        organization_id: str,
        name: str,
        steps: list[dict],
        description: str | None = None,
        applicable_document_types: list[str] | None = None,
        require_sequential: bool = True,
    ) -> ApprovalMatrix:
        """Create a new approval matrix.

        Args:
            organization_id: Organization UUID
            name: Matrix name
            steps: List of approval steps
            description: Optional description
            applicable_document_types: Document types this applies to
            require_sequential: Whether steps must be sequential

        Returns:
            Created matrix
        """
        matrix = ApprovalMatrix(
            organization_id=organization_id,
            name=name,
            description=description,
            applicable_document_types=applicable_document_types or [],
            steps=steps,
            require_sequential=require_sequential,
        )
        self.db.add(matrix)
        await self.db.flush()
        return matrix

    async def get_approval_matrices(
        self,
        organization_id: str,
        active_only: bool = True,
    ) -> list[ApprovalMatrix]:
        """Get approval matrices for an organization.

        Args:
            organization_id: Organization UUID
            active_only: Whether to include only active matrices

        Returns:
            List of approval matrices
        """
        query = select(ApprovalMatrix).where(
            ApprovalMatrix.organization_id == organization_id
        )

        if active_only:
            query = query.where(ApprovalMatrix.is_active == True)

        result = await self.db.execute(query.order_by(ApprovalMatrix.name))
        return list(result.scalars().all())

    async def get_workflow_status(
        self,
        change_request: ChangeRequest,
    ) -> dict:
        """Get detailed workflow status for a change request.

        Args:
            change_request: Change request

        Returns:
            Workflow status dictionary
        """
        history = await self.get_approval_history(str(change_request.id))

        status = {
            "change_request_id": str(change_request.id),
            "approval_status": change_request.approval_status,
            "current_step": change_request.current_approval_step,
            "total_steps": 0,
            "steps": [],
        }

        matrix = change_request.approval_matrix
        if matrix:
            status["total_steps"] = matrix.get_total_steps()
            status["matrix_name"] = matrix.name

            for step in matrix.steps:
                step_info = {
                    "order": step["order"],
                    "name": step["name"],
                    "role": step.get("role"),
                    "required": step.get("required", True),
                    "status": "pending",
                    "approver": None,
                    "decided_at": None,
                    "comment": None,
                }

                # Find approval record for this step
                for record in history:
                    if record.step_order == step["order"]:
                        step_info["status"] = record.decision
                        step_info["approver"] = record.approver.full_name if record.approver else None
                        step_info["decided_at"] = record.decided_at.isoformat()
                        step_info["comment"] = record.comment

                # Mark current step
                if step["order"] == change_request.current_approval_step:
                    if step_info["status"] == "pending":
                        step_info["status"] = "awaiting"

                status["steps"].append(step_info)
        else:
            # Simple approval
            status["total_steps"] = 1
            status["steps"] = [{
                "order": 1,
                "name": "Review",
                "required": True,
                "status": change_request.approval_status,
                "approver": None,
                "decided_at": change_request.reviewed_at.isoformat() if change_request.reviewed_at else None,
                "comment": change_request.review_comment,
            }]

        return status
