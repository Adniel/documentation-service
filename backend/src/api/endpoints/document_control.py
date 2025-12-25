"""Document control API endpoints.

Sprint 6: ISO 9001/13485 compliant document control features.

Compliance: ISO 9001 §7.5.2, ISO 13485 §4.2.4-5, ISO 15489
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.deps import get_current_user, get_db
from src.db.models.user import User
from src.db.models.page import Page, PageStatus
from src.db.models.space import Space
from src.db.models.workspace import Workspace
from src.db.models.document_lifecycle import DocumentStatus, DocumentType
from src.db.models.retention_policy import RetentionPolicy, DispositionMethod, ExpirationAction
from src.db.models.approval import ApprovalMatrix, ApprovalDecision
from src.db.models.change_request import ChangeRequest
from src.modules.document_control import (
    DocumentNumberingService,
    RevisionService,
    LifecycleService,
    RetentionService,
    ApprovalService,
    DocumentMetadataService,
)
from src.modules.audit import AuditService

router = APIRouter()


# ============================================================================
# Request/Response Schemas
# ============================================================================


class DocumentNumberRequest(BaseModel):
    """Request to generate a document number."""
    document_type: str = Field(..., description="Document type (sop, wi, form, etc.)")
    custom_prefix: Optional[str] = Field(None, description="Optional custom prefix")


class DocumentNumberResponse(BaseModel):
    """Response with generated document number."""
    document_number: str
    document_type: str
    prefix: str


class RevisionRequest(BaseModel):
    """Request to create a new revision."""
    is_major: bool = Field(False, description="Whether this is a major revision")
    change_reason: str = Field(..., min_length=10, description="Reason for the change")
    title: Optional[str] = Field(None, description="Optional title for the change request")


class StatusTransitionRequest(BaseModel):
    """Request to transition document status."""
    to_status: str = Field(..., description="Target status")
    effective_date: Optional[datetime] = Field(None, description="Effective date (for EFFECTIVE status)")
    superseded_by_id: Optional[str] = Field(None, description="ID of superseding document (for OBSOLETE)")
    reason: Optional[str] = Field(None, description="Reason for transition")


class MetadataUpdateRequest(BaseModel):
    """Request to update document metadata."""
    owner_id: Optional[str] = None
    custodian_id: Optional[str] = None
    review_cycle_months: Optional[int] = Field(None, ge=1, le=120)
    next_review_date: Optional[datetime] = None
    requires_training: Optional[bool] = None
    training_validity_months: Optional[int] = Field(None, ge=1, le=120)
    retention_policy_id: Optional[str] = None


class ReviewCompletionRequest(BaseModel):
    """Request to complete a periodic review."""
    next_review_months: Optional[int] = Field(None, ge=1, le=120, description="Override review cycle")


class RetentionPolicyCreate(BaseModel):
    """Request to create a retention policy."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    applicable_document_types: list[str] = Field(default_factory=list)
    retention_years: int = Field(..., ge=1, le=100)
    retention_from: str = Field("effective_date")
    disposition_method: str = Field(...)
    review_overdue_action: str = Field("notify_only")
    review_overdue_grace_days: int = Field(30, ge=0)
    retention_expiry_action: str = Field("notify_only")
    retention_expiry_grace_days: int = Field(90, ge=0)
    notify_owner: bool = True
    notify_custodian: bool = True
    notify_days_before: list[int] = Field(default_factory=lambda: [30, 7, 1])


class ApprovalMatrixCreate(BaseModel):
    """Request to create an approval matrix."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    applicable_document_types: list[str] = Field(default_factory=list)
    steps: list[dict] = Field(..., min_length=1)
    require_sequential: bool = True


class ApprovalDecisionRequest(BaseModel):
    """Request to record an approval decision."""
    decision: str = Field(..., description="approved, rejected, or skipped")
    comment: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================


async def get_page_with_org(
    db: AsyncSession,
    page_id: str,
) -> tuple[Page, str]:
    """Get a page and its organization ID."""
    result = await db.execute(
        select(Page)
        .where(Page.id == page_id)
        .options(
            joinedload(Page.space).joinedload(Space.workspace),
        )
    )
    page = result.unique().scalar_one_or_none()

    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    org_id = page.space.workspace.organization_id
    return page, org_id


# ============================================================================
# Document Number Endpoints
# ============================================================================


@router.post("/pages/{page_id}/number", response_model=DocumentNumberResponse)
async def generate_document_number(
    page_id: str,
    data: DocumentNumberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentNumberResponse:
    """Generate a unique document number for a page.

    This marks the document as controlled and assigns it a unique identifier.
    """
    page, org_id = await get_page_with_org(db, page_id)

    if page.document_number:
        raise HTTPException(
            status_code=400,
            detail="Document already has a number assigned",
        )

    # Generate number
    numbering_service = DocumentNumberingService(db)
    document_number = await numbering_service.generate_document_number(
        organization_id=org_id,
        document_type=data.document_type,
        custom_prefix=data.custom_prefix,
    )

    # Update page
    page.document_number = document_number
    page.document_type = data.document_type
    page.is_controlled = True

    # Get sequence for prefix info
    sequence = await numbering_service.get_sequence(org_id, data.document_type)

    # Log to audit trail
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="DOCUMENT_NUMBER_GENERATED",
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page",
        resource_id=page_id,
        resource_name=page.title,
        details={
            "document_number": document_number,
            "document_type": data.document_type,
        },
    )

    await db.commit()

    return DocumentNumberResponse(
        document_number=document_number,
        document_type=data.document_type,
        prefix=sequence.prefix if sequence else data.document_type.upper(),
    )


@router.get("/sequences")
async def list_number_sequences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List document number sequences for the organization."""
    # Get user's organization
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization")

    numbering_service = DocumentNumberingService(db)
    sequences = await numbering_service.list_sequences(current_user.organization_id)

    return {
        "sequences": [
            {
                "id": str(s.id),
                "document_type": s.document_type,
                "prefix": s.prefix,
                "current_number": s.current_number,
                "format_pattern": s.format_pattern,
                "next_preview": s.preview_next(),
            }
            for s in sequences
        ]
    }


# ============================================================================
# Revision Endpoints
# ============================================================================


@router.post("/pages/{page_id}/revise")
async def create_revision(
    page_id: str,
    data: RevisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new revision of an effective document.

    Creates a change request with the pending revision metadata.
    """
    page, org_id = await get_page_with_org(db, page_id)

    if page.status != PageStatus.EFFECTIVE.value:
        raise HTTPException(
            status_code=400,
            detail="Can only create revisions of effective documents",
        )

    revision_service = RevisionService(db)
    change_request = await revision_service.create_revision(
        page=page,
        is_major=data.is_major,
        change_reason=data.change_reason,
        author_id=str(current_user.id),
        title=data.title,
    )

    # Log to audit trail
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="REVISION_CREATED",
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page",
        resource_id=page_id,
        resource_name=page.title,
        details={
            "change_request_id": str(change_request.id),
            "is_major": data.is_major,
            "pending_revision": change_request.pending_revision,
            "pending_version": change_request.pending_version,
            "reason": data.change_reason,
        },
    )

    await db.commit()

    return {
        "change_request_id": str(change_request.id),
        "number": change_request.number,
        "pending_revision": change_request.pending_revision,
        "pending_version": change_request.pending_version,
        "is_major": data.is_major,
    }


@router.get("/pages/{page_id}/revisions")
async def get_revision_history(
    page_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get complete revision history for a document."""
    page, org_id = await get_page_with_org(db, page_id)

    revision_service = RevisionService(db)
    history = await revision_service.get_revision_history(page_id)

    return {
        "page_id": page_id,
        "current_revision": page.revision,
        "current_version": f"{page.major_version}.{page.minor_version}",
        "revisions": history,
    }


# ============================================================================
# Status Transition Endpoints
# ============================================================================


@router.post("/pages/{page_id}/status")
async def transition_status(
    page_id: str,
    data: StatusTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Transition document to a new lifecycle status."""
    page, org_id = await get_page_with_org(db, page_id)

    # Parse target status
    try:
        to_status = DocumentStatus(data.to_status)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {data.to_status}",
        )

    from_status = DocumentStatus(page.status)

    # Check transition is allowed
    lifecycle_service = LifecycleService(db)
    if not lifecycle_service.is_transition_allowed(from_status, to_status):
        raise HTTPException(
            status_code=400,
            detail=f"Transition from {from_status.value} to {to_status.value} is not allowed",
        )

    # Validate metadata
    metadata_service = DocumentMetadataService(db)
    errors = metadata_service.validate_for_transition(page, from_status, to_status)
    if errors:
        raise HTTPException(
            status_code=422,
            detail={"validation_errors": errors},
        )

    # Handle specific transitions
    if to_status == DocumentStatus.EFFECTIVE:
        effective_date = data.effective_date or datetime.utcnow()
        await metadata_service.set_effective(page, effective_date, str(current_user.id))
    elif to_status == DocumentStatus.APPROVED:
        await metadata_service.set_approved(page, str(current_user.id))
    elif to_status == DocumentStatus.OBSOLETE:
        await metadata_service.mark_obsolete(
            page,
            data.superseded_by_id,
            data.reason or "Document obsoleted",
            str(current_user.id),
        )
    else:
        await lifecycle_service.transition(
            page, to_status, str(current_user.id), data.reason
        )

    # Log to audit trail
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="STATUS_CHANGED",
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page",
        resource_id=page_id,
        resource_name=page.title,
        details={
            "from_status": from_status.value,
            "to_status": to_status.value,
            "reason": data.reason,
        },
    )

    await db.commit()

    return {
        "page_id": page_id,
        "previous_status": from_status.value,
        "new_status": to_status.value,
    }


@router.get("/statuses")
async def list_statuses(
    current_user: User = Depends(get_current_user),
):
    """Get information about all document statuses."""
    lifecycle_service = LifecycleService(None)  # No DB needed for this
    return {"statuses": lifecycle_service.get_all_statuses()}


# ============================================================================
# Metadata Endpoints
# ============================================================================


@router.patch("/pages/{page_id}/metadata")
async def update_metadata(
    page_id: str,
    data: MetadataUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update document control metadata."""
    page, org_id = await get_page_with_org(db, page_id)

    metadata_service = DocumentMetadataService(db)

    # Apply updates
    if data.owner_id is not None or data.custodian_id is not None:
        await metadata_service.assign_owner(
            page,
            data.owner_id or page.owner_id,
            data.custodian_id,
        )

    if data.review_cycle_months is not None:
        await metadata_service.set_review_schedule(
            page,
            data.review_cycle_months,
            data.next_review_date,
        )

    if data.requires_training is not None:
        await metadata_service.set_training_requirement(
            page,
            data.requires_training,
            data.training_validity_months,
        )

    if data.retention_policy_id:
        result = await db.execute(
            select(RetentionPolicy).where(RetentionPolicy.id == data.retention_policy_id)
        )
        policy = result.scalar_one_or_none()
        if policy:
            retention_service = RetentionService(db)
            await retention_service.apply_retention_policy(page, policy)

    await db.commit()

    return {"page_id": page_id, "metadata": metadata_service.get_metadata_summary(page)}


@router.get("/pages/{page_id}/metadata")
async def get_metadata(
    page_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get document control metadata."""
    page, org_id = await get_page_with_org(db, page_id)

    metadata_service = DocumentMetadataService(db)
    return {"page_id": page_id, "metadata": metadata_service.get_metadata_summary(page)}


# ============================================================================
# Review Endpoints
# ============================================================================


@router.get("/review-due")
async def get_documents_due_for_review(
    days_ahead: int = Query(30, ge=1, le=365),
    include_overdue: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get documents due for periodic review."""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization")

    retention_service = RetentionService(db)
    documents = await retention_service.get_documents_due_for_review(
        organization_id=current_user.organization_id,
        include_overdue=include_overdue,
        days_ahead=days_ahead,
    )

    overdue_count = await retention_service.get_overdue_review_count(
        current_user.organization_id
    )

    return {
        "total": len(documents),
        "overdue_count": overdue_count,
        "documents": [
            {
                "id": str(doc.id),
                "title": doc.title,
                "document_number": doc.document_number,
                "next_review_date": doc.next_review_date.isoformat() if doc.next_review_date else None,
                "is_overdue": doc.is_review_overdue,
                "owner_id": str(doc.owner_id) if doc.owner_id else None,
            }
            for doc in documents
        ],
    }


@router.post("/pages/{page_id}/complete-review")
async def complete_review(
    page_id: str,
    data: ReviewCompletionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Complete a periodic review for a document."""
    page, org_id = await get_page_with_org(db, page_id)

    if page.status != PageStatus.EFFECTIVE.value:
        raise HTTPException(
            status_code=400,
            detail="Can only complete reviews for effective documents",
        )

    retention_service = RetentionService(db)
    await retention_service.complete_review(
        page,
        str(current_user.id),
        data.next_review_months,
    )

    # Log to audit trail
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="REVIEW_COMPLETED",
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="page",
        resource_id=page_id,
        resource_name=page.title,
        details={
            "next_review_date": page.next_review_date.isoformat() if page.next_review_date else None,
        },
    )

    await db.commit()

    return {
        "page_id": page_id,
        "reviewed_at": page.last_reviewed_date.isoformat(),
        "next_review_date": page.next_review_date.isoformat() if page.next_review_date else None,
    }


# ============================================================================
# Retention Endpoints
# ============================================================================


@router.get("/retention-due")
async def get_documents_due_for_disposition(
    days_ahead: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get documents approaching disposition date."""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization")

    retention_service = RetentionService(db)
    documents = await retention_service.get_documents_due_for_disposition(
        organization_id=current_user.organization_id,
        days_ahead=days_ahead,
    )

    return {
        "total": len(documents),
        "documents": [
            {
                "id": str(doc.id),
                "title": doc.title,
                "document_number": doc.document_number,
                "disposition_date": doc.disposition_date.isoformat() if doc.disposition_date else None,
                "retention_policy": doc.retention_policy.name if doc.retention_policy else None,
            }
            for doc in documents
        ],
    }


@router.get("/retention-policies")
async def list_retention_policies(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List retention policies for the organization."""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization")

    retention_service = RetentionService(db)
    policies = await retention_service.get_retention_policies(
        current_user.organization_id,
        active_only=active_only,
    )

    return {
        "policies": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "retention_years": p.retention_years,
                "disposition_method": p.disposition_method,
                "applicable_document_types": p.applicable_document_types,
                "is_active": p.is_active,
            }
            for p in policies
        ]
    }


@router.post("/retention-policies", status_code=status.HTTP_201_CREATED)
async def create_retention_policy(
    data: RetentionPolicyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new retention policy."""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization")

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    retention_service = RetentionService(db)
    policy = await retention_service.create_retention_policy(
        organization_id=current_user.organization_id,
        name=data.name,
        retention_years=data.retention_years,
        disposition_method=DispositionMethod(data.disposition_method),
        description=data.description,
        applicable_document_types=data.applicable_document_types,
        retention_from=data.retention_from,
        review_overdue_action=ExpirationAction(data.review_overdue_action),
        review_overdue_grace_days=data.review_overdue_grace_days,
        retention_expiry_action=ExpirationAction(data.retention_expiry_action),
        retention_expiry_grace_days=data.retention_expiry_grace_days,
        notify_owner=data.notify_owner,
        notify_custodian=data.notify_custodian,
        notify_days_before=data.notify_days_before,
    )

    await db.commit()

    return {"id": str(policy.id), "name": policy.name}


# ============================================================================
# Approval Workflow Endpoints
# ============================================================================


@router.get("/approval-matrices")
async def list_approval_matrices(
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List approval matrices for the organization."""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization")

    approval_service = ApprovalService(db)
    matrices = await approval_service.get_approval_matrices(
        current_user.organization_id,
        active_only=active_only,
    )

    return {
        "matrices": [
            {
                "id": str(m.id),
                "name": m.name,
                "description": m.description,
                "applicable_document_types": m.applicable_document_types,
                "steps": m.steps,
                "require_sequential": m.require_sequential,
                "is_active": m.is_active,
            }
            for m in matrices
        ]
    }


@router.post("/approval-matrices", status_code=status.HTTP_201_CREATED)
async def create_approval_matrix(
    data: ApprovalMatrixCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new approval matrix."""
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User has no organization")

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    approval_service = ApprovalService(db)
    matrix = await approval_service.create_approval_matrix(
        organization_id=current_user.organization_id,
        name=data.name,
        steps=data.steps,
        description=data.description,
        applicable_document_types=data.applicable_document_types,
        require_sequential=data.require_sequential,
    )

    await db.commit()

    return {"id": str(matrix.id), "name": matrix.name}


@router.post("/change-requests/{cr_id}/approve")
async def approve_change_request(
    cr_id: str,
    data: ApprovalDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record approval decision for a change request."""
    # Parse decision
    try:
        decision = ApprovalDecision(data.decision)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision: {data.decision}",
        )

    approval_service = ApprovalService(db)
    try:
        cr, is_complete = await approval_service.record_approval(
            change_request_id=cr_id,
            approver_id=str(current_user.id),
            decision=decision,
            comment=data.comment,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Log to audit trail
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="APPROVAL_RECORDED",
        actor_id=str(current_user.id),
        actor_email=current_user.email,
        resource_type="change_request",
        resource_id=cr_id,
        resource_name=cr.title,
        details={
            "decision": decision.value,
            "is_workflow_complete": is_complete,
            "current_step": cr.current_approval_step,
            "comment": data.comment,
        },
    )

    await db.commit()

    return {
        "change_request_id": cr_id,
        "approval_status": cr.approval_status,
        "is_workflow_complete": is_complete,
        "current_step": cr.current_approval_step,
    }


@router.get("/change-requests/{cr_id}/workflow-status")
async def get_workflow_status(
    cr_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed workflow status for a change request."""
    result = await db.execute(
        select(ChangeRequest)
        .where(ChangeRequest.id == cr_id)
        .options(joinedload(ChangeRequest.approval_matrix))
    )
    cr = result.unique().scalar_one_or_none()

    if not cr:
        raise HTTPException(status_code=404, detail="Change request not found")

    approval_service = ApprovalService(db)
    return await approval_service.get_workflow_status(cr)


@router.get("/pending-approvals")
async def get_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get change requests pending approval."""
    approval_service = ApprovalService(db)
    pending = await approval_service.get_pending_approvals(str(current_user.id))

    return {
        "total": len(pending),
        "change_requests": [
            {
                "id": str(cr.id),
                "number": cr.number,
                "title": cr.title,
                "page_title": cr.page.title if cr.page else None,
                "approval_status": cr.approval_status,
                "current_step": cr.current_approval_step,
                "submitted_at": cr.submitted_at.isoformat() if cr.submitted_at else None,
            }
            for cr in pending
        ],
    }
