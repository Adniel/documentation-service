"""Audit schemas for query and export operations.

Provides Pydantic models for audit trail queries, verification,
and compliance export functionality.

Compliance:
- 21 CFR §11.10(e) - Audit trail reviewability and export
"""

from datetime import datetime
from typing import Any, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Query Schemas
# -----------------------------------------------------------------------------

class AuditEventResponse(BaseModel):
    """Response schema for a single audit event."""

    id: UUID
    event_type: str
    timestamp: datetime
    actor_id: Optional[UUID] = None
    actor_email: Optional[str] = None
    actor_ip: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    resource_name: Optional[str] = None
    details: Optional[dict] = None
    event_hash: str
    previous_hash: Optional[str] = None

    class Config:
        from_attributes = True


class AuditEventListResponse(BaseModel):
    """Paginated list of audit events."""

    events: List[AuditEventResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class AuditStatsResponse(BaseModel):
    """Statistics summary of audit events."""

    total_events: int
    events_by_type: dict[str, int]
    events_today: int
    events_this_week: int
    unique_actors: int
    chain_head_hash: Optional[str] = None
    oldest_event: Optional[datetime] = None
    newest_event: Optional[datetime] = None


# -----------------------------------------------------------------------------
# Verification Schemas
# -----------------------------------------------------------------------------

class ChainVerificationRequest(BaseModel):
    """Request to verify hash chain integrity."""

    start_from_id: Optional[UUID] = Field(
        None,
        description="Start verification from this event ID (default: beginning)"
    )
    end_at_id: Optional[UUID] = Field(
        None,
        description="End verification at this event ID (default: chain head)"
    )
    max_events: int = Field(
        10000,
        ge=1,
        le=100000,
        description="Maximum events to verify in one request"
    )


class ChainVerificationResponse(BaseModel):
    """Result of hash chain verification."""

    is_valid: bool
    total_events: int
    verified_events: int
    first_invalid_event_id: Optional[UUID] = None
    first_invalid_reason: Optional[str] = None
    verification_timestamp: datetime
    chain_head_hash: Optional[str] = None
    verification_duration_ms: float


class EventVerificationResponse(BaseModel):
    """Result of single event verification."""

    event_id: UUID
    is_valid: bool
    stored_hash: str
    computed_hash: str
    previous_hash_valid: bool
    issues: List[str]


# -----------------------------------------------------------------------------
# Export Schemas
# -----------------------------------------------------------------------------

class AuditExportRequest(BaseModel):
    """Request to export audit trail."""

    format: Literal["csv", "json", "pdf"] = Field(
        ...,
        description="Export format"
    )
    start_date: datetime = Field(
        ...,
        description="Start of export period"
    )
    end_date: datetime = Field(
        ...,
        description="End of export period"
    )
    event_types: Optional[List[str]] = Field(
        None,
        description="Filter by specific event types"
    )
    actor_id: Optional[UUID] = Field(
        None,
        description="Filter by specific actor"
    )
    resource_type: Optional[str] = Field(
        None,
        description="Filter by resource type"
    )
    resource_id: Optional[UUID] = Field(
        None,
        description="Filter by specific resource"
    )
    include_details: bool = Field(
        True,
        description="Include event details in export"
    )
    include_verification: bool = Field(
        True,
        description="Include hash chain verification in PDF reports"
    )


class AuditExportResponse(BaseModel):
    """Response for audit export request."""

    filename: str
    content_type: str
    size_bytes: int
    event_count: int
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    report_hash: str  # SHA-256 of the report for integrity


# -----------------------------------------------------------------------------
# Reason Capture Schemas
# -----------------------------------------------------------------------------

class ChangeReason(BaseModel):
    """Schema for capturing change reason (21 CFR §11.10(e) compliance)."""

    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Reason for the change (required for compliance)"
    )


class ContentUpdateWithReason(BaseModel):
    """Content update request with mandatory reason."""

    title: Optional[str] = None
    content: Optional[dict] = None
    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Reason for the change"
    )


class ContentDeleteWithReason(BaseModel):
    """Content deletion request with mandatory reason."""

    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Reason for deletion"
    )


# -----------------------------------------------------------------------------
# Resource Audit History
# -----------------------------------------------------------------------------

class ResourceAuditHistoryResponse(BaseModel):
    """Audit history for a specific resource."""

    resource_type: str
    resource_id: UUID
    resource_name: Optional[str] = None
    events: List[AuditEventResponse]
    total_events: int
    first_event: Optional[datetime] = None
    last_event: Optional[datetime] = None
