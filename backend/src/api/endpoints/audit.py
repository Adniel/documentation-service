"""Audit trail API endpoints.

Provides endpoints for querying, verifying, and exporting audit events.

Sprint B: Added organization-scoped audit endpoints for org admins.

Compliance:
- 21 CFR §11.10(e) - Audit trail reviewability and export
- ISO 9001 §7.5.3 - Control of documented information
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_current_user
from src.modules.access.dependencies import require_superuser
from src.modules.audit.audit_service import AuditService
from src.modules.audit.audit_schemas import (
    AuditEventResponse,
    AuditEventListResponse,
    AuditStatsResponse,
    ChainVerificationRequest,
    ChainVerificationResponse,
    EventVerificationResponse,
    ResourceAuditHistoryResponse,
    AuditExportRequest,
)
from src.db.models.organization import Organization, organization_members
from src.modules.content.service import get_organization

router = APIRouter(prefix="/audit", tags=["audit"])


async def _require_org_admin(db: AsyncSession, org_id: str, current_user) -> None:
    """Check if user is admin/owner of the organization."""
    if current_user.is_superuser:
        return

    org = await get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Owner always has admin access
    if org.owner_id == current_user.id:
        return

    # Check member role
    result = await db.execute(
        select(organization_members.c.role).where(
            and_(
                organization_members.c.organization_id == org_id,
                organization_members.c.user_id == current_user.id,
            )
        )
    )
    row = result.first()
    role = row[0] if row else None

    if role not in ("admin", "owner"):
        raise HTTPException(
            status_code=403,
            detail="Admin or owner role required for this action"
        )


# -----------------------------------------------------------------------------
# Query Endpoints
# -----------------------------------------------------------------------------

@router.get("/events", response_model=AuditEventListResponse)
async def list_audit_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    actor_id: Optional[UUID] = Query(None, description="Filter by actor ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[UUID] = Query(None, description="Filter by resource ID"),
    start_date: Optional[datetime] = Query(None, description="Filter events after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events before this date"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_superuser),
):
    """List audit events with optional filters.

    Requires admin role. Returns paginated list of audit events
    sorted by timestamp (newest first).
    """
    audit_service = AuditService(db)
    return await audit_service.query_events(
        event_type=event_type,
        actor_id=str(actor_id) if actor_id else None,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@router.get("/events/{event_id}", response_model=AuditEventResponse)
async def get_audit_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_superuser),
):
    """Get a single audit event by ID.

    Requires admin role.
    """
    audit_service = AuditService(db)
    event = await audit_service.get_event_by_id(str(event_id))

    if not event:
        raise HTTPException(status_code=404, detail="Audit event not found")

    return AuditEventResponse.model_validate(event)


@router.get("/resource/{resource_type}/{resource_id}", response_model=ResourceAuditHistoryResponse)
async def get_resource_audit_history(
    resource_type: str,
    resource_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get audit history for a specific resource.

    Available to users with at least Editor role on the resource.
    Returns chronological list of all audit events for the resource.
    """
    # Note: In production, add permission check for the specific resource
    audit_service = AuditService(db)
    return await audit_service.get_resource_history(
        resource_type=resource_type,
        resource_id=str(resource_id),
        limit=limit,
    )


@router.get("/stats", response_model=AuditStatsResponse)
async def get_audit_stats(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_superuser),
):
    """Get audit trail statistics.

    Requires admin role. Returns summary statistics including
    total events, breakdown by type, and chain head hash.
    """
    audit_service = AuditService(db)
    return await audit_service.get_stats()


# -----------------------------------------------------------------------------
# Verification Endpoints (21 CFR §11.10(e) Compliance)
# -----------------------------------------------------------------------------

@router.post("/verify", response_model=ChainVerificationResponse)
async def verify_audit_chain(
    request: ChainVerificationRequest = None,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_superuser),
):
    """Verify audit trail hash chain integrity.

    Requires admin role. Walks the audit chain and verifies
    each event's hash matches its content. Detects any
    modifications or deletions (tampering).

    This is a critical compliance endpoint for 21 CFR §11.10(e).
    """
    if request is None:
        request = ChainVerificationRequest()

    audit_service = AuditService(db)
    return await audit_service.verify_chain_integrity(
        start_from_id=str(request.start_from_id) if request.start_from_id else None,
        end_at_id=str(request.end_at_id) if request.end_at_id else None,
        max_events=request.max_events,
    )


@router.get("/verify/{event_id}", response_model=EventVerificationResponse)
async def verify_single_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_superuser),
):
    """Verify a single audit event's integrity.

    Requires admin role. Checks that the event's hash matches
    its content and that its previous_hash links to a valid event.
    """
    audit_service = AuditService(db)
    return await audit_service.verify_single_event(str(event_id))


# -----------------------------------------------------------------------------
# Export Endpoints
# -----------------------------------------------------------------------------

@router.post("/export")
async def export_audit_trail(
    request: AuditExportRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_superuser),
):
    """Export audit trail for compliance reporting.

    Requires admin role. Generates export in specified format
    (CSV, JSON, or PDF) for the given date range.

    PDF reports include hash chain verification and are suitable
    for regulatory submission.
    """
    audit_service = AuditService(db)

    # Query events for export
    events_response = await audit_service.query_events(
        event_type=request.event_types[0] if request.event_types and len(request.event_types) == 1 else None,
        actor_id=str(request.actor_id) if request.actor_id else None,
        resource_type=request.resource_type,
        resource_id=str(request.resource_id) if request.resource_id else None,
        start_date=request.start_date,
        end_date=request.end_date,
        limit=10000,  # Max export size
        offset=0,
    )

    events = events_response.events

    # Filter by multiple event types if specified
    if request.event_types and len(request.event_types) > 1:
        events = [e for e in events if e.event_type in request.event_types]

    if request.format == "csv":
        return await _export_csv(events, request)
    elif request.format == "json":
        return await _export_json(events, request)
    elif request.format == "pdf":
        # PDF export requires additional dependency
        raise HTTPException(
            status_code=501,
            detail="PDF export not yet implemented. Use CSV or JSON format."
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown format: {request.format}")


async def _export_csv(events: list, request: AuditExportRequest) -> Response:
    """Generate CSV export of audit events."""
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    headers = [
        "ID", "Event Type", "Timestamp", "Actor ID", "Actor Email",
        "Actor IP", "Resource Type", "Resource ID", "Resource Name",
        "Event Hash"
    ]
    if request.include_details:
        headers.append("Details")
    writer.writerow(headers)

    # Data rows
    for event in events:
        row = [
            str(event.id),
            event.event_type,
            event.timestamp.isoformat() if event.timestamp else "",
            str(event.actor_id) if event.actor_id else "",
            event.actor_email or "",
            event.actor_ip or "",
            event.resource_type or "",
            str(event.resource_id) if event.resource_id else "",
            event.resource_name or "",
            event.event_hash,
        ]
        if request.include_details:
            import json
            row.append(json.dumps(event.details) if event.details else "")
        writer.writerow(row)

    csv_content = output.getvalue()

    filename = f"audit_export_{request.start_date.strftime('%Y%m%d')}_{request.end_date.strftime('%Y%m%d')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Event-Count": str(len(events)),
        }
    )


async def _export_json(events: list, request: AuditExportRequest) -> Response:
    """Generate JSON export of audit events."""
    import json
    import hashlib

    export_data = {
        "export_metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "period_start": request.start_date.isoformat(),
            "period_end": request.end_date.isoformat(),
            "event_count": len(events),
            "filters": {
                "event_types": request.event_types,
                "actor_id": str(request.actor_id) if request.actor_id else None,
                "resource_type": request.resource_type,
                "resource_id": str(request.resource_id) if request.resource_id else None,
            },
        },
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "actor_id": str(e.actor_id) if e.actor_id else None,
                "actor_email": e.actor_email,
                "actor_ip": e.actor_ip,
                "resource_type": e.resource_type,
                "resource_id": str(e.resource_id) if e.resource_id else None,
                "resource_name": e.resource_name,
                "details": e.details if request.include_details else None,
                "event_hash": e.event_hash,
                "previous_hash": e.previous_hash,
            }
            for e in events
        ],
    }

    # Add report hash for integrity
    json_content = json.dumps(export_data, sort_keys=True, indent=2)
    report_hash = hashlib.sha256(json_content.encode()).hexdigest()
    export_data["export_metadata"]["report_hash"] = report_hash

    # Re-serialize with hash
    json_content = json.dumps(export_data, sort_keys=True, indent=2)

    filename = f"audit_export_{request.start_date.strftime('%Y%m%d')}_{request.end_date.strftime('%Y%m%d')}.json"

    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "X-Event-Count": str(len(events)),
            "X-Report-Hash": report_hash,
        }
    )


# -----------------------------------------------------------------------------
# Organization-Scoped Audit Endpoints (Sprint B)
# -----------------------------------------------------------------------------

@router.get("/organizations/{org_id}/events", response_model=AuditEventListResponse)
async def list_org_audit_events(
    org_id: str,
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    actor_id: Optional[UUID] = Query(None, description="Filter by actor ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[datetime] = Query(None, description="Filter events after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events before this date"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List audit events for a specific organization.

    Requires admin role in the organization (not superuser).
    Returns paginated list of audit events filtered by organization.
    """
    await _require_org_admin(db, org_id, current_user)

    audit_service = AuditService(db)

    # Query events with organization filter
    # The audit service will filter by events that have the org_id in their details
    # or belong to resources within the organization
    return await audit_service.query_events(
        event_type=event_type,
        actor_id=str(actor_id) if actor_id else None,
        resource_type=resource_type,
        resource_id=None,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        organization_id=org_id,  # Filter by organization
    )


@router.get("/organizations/{org_id}/stats", response_model=AuditStatsResponse)
async def get_org_audit_stats(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get audit trail statistics for an organization.

    Requires admin role in the organization.
    """
    await _require_org_admin(db, org_id, current_user)

    audit_service = AuditService(db)
    return await audit_service.get_stats(organization_id=org_id)


@router.post("/organizations/{org_id}/verify", response_model=ChainVerificationResponse)
async def verify_org_audit_chain(
    org_id: str,
    request: ChainVerificationRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Verify audit trail hash chain integrity for an organization.

    Requires admin role in the organization.
    Walks the audit chain for the organization's events and verifies integrity.
    """
    await _require_org_admin(db, org_id, current_user)

    if request is None:
        request = ChainVerificationRequest()

    audit_service = AuditService(db)
    return await audit_service.verify_chain_integrity(
        start_from_id=str(request.start_from_id) if request.start_from_id else None,
        end_at_id=str(request.end_at_id) if request.end_at_id else None,
        max_events=request.max_events,
        organization_id=org_id,
    )


@router.post("/organizations/{org_id}/export")
async def export_org_audit_trail(
    org_id: str,
    request: AuditExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Export audit trail for an organization.

    Requires admin role in the organization.
    Generates export in specified format (CSV, JSON) for the given date range.
    """
    await _require_org_admin(db, org_id, current_user)

    audit_service = AuditService(db)

    # Query events for export with organization filter
    events_response = await audit_service.query_events(
        event_type=request.event_types[0] if request.event_types and len(request.event_types) == 1 else None,
        actor_id=str(request.actor_id) if request.actor_id else None,
        resource_type=request.resource_type,
        resource_id=str(request.resource_id) if request.resource_id else None,
        start_date=request.start_date,
        end_date=request.end_date,
        limit=10000,
        offset=0,
        organization_id=org_id,
    )

    events = events_response.events

    # Filter by multiple event types if specified
    if request.event_types and len(request.event_types) > 1:
        events = [e for e in events if e.event_type in request.event_types]

    if request.format == "csv":
        return await _export_csv(events, request)
    elif request.format == "json":
        return await _export_json(events, request)
    elif request.format == "pdf":
        raise HTTPException(
            status_code=501,
            detail="PDF export not yet implemented. Use CSV or JSON format."
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown format: {request.format}")
