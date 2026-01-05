"""Pydantic schemas for MCP integration.

Sprint C: MCP Integration
"""

from datetime import datetime
from typing import Any
import ipaddress

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Service Account Schemas
# =============================================================================


class ServiceAccountCreate(BaseModel):
    """Create a new service account."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    role: str = Field(default="viewer", pattern="^(viewer|editor|admin)$")
    allowed_spaces: list[str] | None = None
    allowed_operations: list[str] | None = None
    ip_allowlist: list[str] | None = None
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000)
    expires_at: datetime | None = None

    @field_validator("ip_allowlist")
    @classmethod
    def validate_ip_allowlist(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        for cidr in v:
            try:
                ipaddress.ip_network(cidr, strict=False)
            except ValueError:
                raise ValueError(f"Invalid CIDR notation: {cidr}")
        return v


class ServiceAccountUpdate(BaseModel):
    """Update a service account."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    role: str | None = Field(None, pattern="^(viewer|editor|admin)$")
    allowed_spaces: list[str] | None = None
    allowed_operations: list[str] | None = None
    ip_allowlist: list[str] | None = None
    rate_limit_per_minute: int | None = Field(None, ge=1, le=1000)
    is_active: bool | None = None
    expires_at: datetime | None = None

    @field_validator("ip_allowlist")
    @classmethod
    def validate_ip_allowlist(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        for cidr in v:
            try:
                ipaddress.ip_network(cidr, strict=False)
            except ValueError:
                raise ValueError(f"Invalid CIDR notation: {cidr}")
        return v


class ServiceAccountResponse(BaseModel):
    """Service account response (without sensitive data)."""

    id: str
    organization_id: str
    name: str
    description: str | None
    api_key_prefix: str
    role: str
    allowed_spaces: list[str] | None
    allowed_operations: list[str] | None
    ip_allowlist: list[str] | None
    rate_limit_per_minute: int
    is_active: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    created_by_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceAccountCreateResponse(ServiceAccountResponse):
    """Response when creating a service account (includes API key once)."""

    api_key: str  # Only returned once at creation


class ServiceAccountListResponse(BaseModel):
    """List of service accounts."""

    accounts: list[ServiceAccountResponse]
    total: int


class ApiKeyRotateResponse(BaseModel):
    """Response when rotating API key."""

    api_key: str
    api_key_prefix: str


# =============================================================================
# Usage Statistics Schemas
# =============================================================================


class UsageStatsResponse(BaseModel):
    """Usage statistics for a service account."""

    service_account_id: str
    period_start: datetime
    period_end: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float | None
    requests_by_operation: dict[str, int]
    requests_by_day: list[dict[str, Any]]


class UsageRecordResponse(BaseModel):
    """Single usage record."""

    id: str
    timestamp: datetime
    operation: str
    resource_type: str | None
    resource_id: str | None
    ip_address: str | None
    response_code: int
    response_time_ms: int | None
    error_message: str | None

    model_config = {"from_attributes": True}


# =============================================================================
# MCP Protocol Schemas
# =============================================================================


class McpRequest(BaseModel):
    """MCP JSON-RPC request."""

    jsonrpc: str = "2.0"
    id: str | int
    method: str
    params: dict[str, Any] | None = None


class McpResponse(BaseModel):
    """MCP JSON-RPC response."""

    jsonrpc: str = "2.0"
    id: str | int
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None


class McpError(BaseModel):
    """MCP error object."""

    code: int
    message: str
    data: dict[str, Any] | None = None


# =============================================================================
# MCP Tool Schemas
# =============================================================================


class SearchDocumentsParams(BaseModel):
    """Parameters for search_documents tool."""

    query: str = Field(..., min_length=1)
    space_id: str | None = None
    limit: int = Field(default=10, ge=1, le=100)


class GetDocumentParams(BaseModel):
    """Parameters for get_document tool."""

    document_id: str


class ListSpacesParams(BaseModel):
    """Parameters for list_spaces tool."""

    workspace_id: str | None = None


class DocumentResult(BaseModel):
    """Document search result."""

    id: str
    title: str
    space_id: str
    space_name: str
    excerpt: str | None
    score: float | None
    status: str
    updated_at: datetime


class DocumentContent(BaseModel):
    """Full document content."""

    id: str
    title: str
    content_markdown: str
    content_html: str | None = None
    metadata: dict[str, Any]
    version: str
    status: str
    updated_at: datetime


class SpaceInfo(BaseModel):
    """Space information."""

    id: str
    name: str
    description: str | None
    workspace_id: str
    workspace_name: str
    page_count: int
