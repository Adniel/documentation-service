# Sprint C: MCP Integration - Detailed Implementation Plan

## Overview

**Goal:** Enable the platform as an MCP (Model Context Protocol) server for AI agent consumption, with secure service account management.

**Priority:** P1 - Enables AI integration use cases

**Estimated Effort:** 2 weeks

**Dependencies:**
- Authentication system (completed)
- Audit trail (completed)
- Content management (completed)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     External AI Agents                          │
│         (Claude, ChatGPT, Custom Agents, IDE Extensions)        │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                          API Key Auth
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Rate Limiter │  │ IP Allowlist │  │ Permission Checker   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    MCP Tools                              │   │
│  │  • search_documents    • get_document_content            │   │
│  │  • get_document        • get_document_metadata           │   │
│  │  • list_spaces         • get_document_history            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    MCP Resources                          │   │
│  │  • doc://{org}/{workspace}/{space}/{page}                │   │
│  │  • space://{org}/{workspace}/{space}                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                          Audit Logging
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Existing Platform Services                    │
│         Content Service │ Search Service │ Git Service          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Database & Models (Days 1-2)

### 1.1 Database Migration

**File:** `backend/alembic/versions/011_mcp_integration.py`

```python
"""MCP Integration - Service Accounts

Revision ID: 011_mcp_integration
Revises: 010_admin_ui_completion
Create Date: 2025-01-XX
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "011_mcp_integration"
down_revision = "010_admin_ui_completion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Service accounts table
    op.create_table(
        "service_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),

        # Authentication
        sa.Column("api_key_hash", sa.String(64), nullable=False),  # SHA-256 hash
        sa.Column("api_key_prefix", sa.String(8), nullable=False),  # First 8 chars for identification

        # Permissions
        sa.Column("role", sa.String(50), nullable=False, default="viewer"),
        sa.Column("allowed_spaces", JSONB, nullable=True),  # List of space UUIDs, null = all
        sa.Column("allowed_operations", JSONB, nullable=True),  # List of operation names, null = all

        # Security
        sa.Column("ip_allowlist", JSONB, nullable=True),  # List of CIDR ranges
        sa.Column("rate_limit_per_minute", sa.Integer, nullable=False, default=60),

        # Status
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),

        # Audit
        sa.Column("created_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Indexes for service_accounts
    op.create_index("ix_service_accounts_organization_id", "service_accounts", ["organization_id"])
    op.create_index("ix_service_accounts_api_key_prefix", "service_accounts", ["api_key_prefix"])
    op.create_index("ix_service_accounts_is_active", "service_accounts", ["is_active"])
    op.create_unique_constraint("uq_service_accounts_org_name", "service_accounts", ["organization_id", "name"])

    # Service account usage tracking
    op.create_table(
        "service_account_usage",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("service_account_id", UUID(as_uuid=True), sa.ForeignKey("service_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("operation", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", UUID(as_uuid=True), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),  # IPv6 max length
        sa.Column("response_code", sa.Integer, nullable=False),
        sa.Column("response_time_ms", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
    )

    # Indexes for usage tracking (optimized for time-series queries)
    op.create_index("ix_service_account_usage_account_timestamp", "service_account_usage", ["service_account_id", "timestamp"])
    op.create_index("ix_service_account_usage_timestamp", "service_account_usage", ["timestamp"])


def downgrade() -> None:
    op.drop_table("service_account_usage")
    op.drop_table("service_accounts")
```

### 1.2 SQLAlchemy Models

**File:** `backend/src/db/models/service_account.py`

```python
"""Service Account models for MCP integration."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base
from src.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.db.models.organization import Organization
    from src.db.models.user import User


class ServiceAccount(Base, UUIDMixin, TimestampMixin):
    """Service account for API access."""

    __tablename__ = "service_accounts"

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Authentication
    api_key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    api_key_prefix: Mapped[str] = mapped_column(String(8), nullable=False, index=True)

    # Permissions
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")
    allowed_spaces: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    allowed_operations: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    # Security
    ip_allowlist: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=60)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="service_accounts")
    created_by: Mapped["User"] = relationship()
    usage_records: Mapped[list["ServiceAccountUsage"]] = relationship(
        back_populates="service_account", cascade="all, delete-orphan"
    )


class ServiceAccountUsage(Base, UUIDMixin):
    """Usage tracking for service accounts."""

    __tablename__ = "service_account_usage"

    service_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("service_accounts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    operation: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    response_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    service_account: Mapped["ServiceAccount"] = relationship(back_populates="usage_records")
```

**Update:** `backend/src/db/models/__init__.py`

```python
# Add to existing imports
from src.db.models.service_account import ServiceAccount, ServiceAccountUsage
```

**Update:** `backend/src/db/models/organization.py`

```python
# Add relationship
service_accounts: Mapped[list["ServiceAccount"]] = relationship(
    back_populates="organization", cascade="all, delete-orphan"
)
```

---

## Phase 2: Service Account Backend (Days 3-4)

### 2.1 Schemas

**File:** `backend/src/modules/mcp/schemas.py`

```python
"""Pydantic schemas for MCP integration."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
import ipaddress


# =============================================================================
# Service Account Schemas
# =============================================================================

class ServiceAccountCreate(BaseModel):
    """Create a new service account."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    role: str = Field(default="viewer", pattern="^(viewer|editor|admin)$")
    allowed_spaces: list[UUID] | None = None
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
    allowed_spaces: list[UUID] | None = None
    allowed_operations: list[str] | None = None
    ip_allowlist: list[str] | None = None
    rate_limit_per_minute: int | None = Field(None, ge=1, le=1000)
    is_active: bool | None = None
    expires_at: datetime | None = None


class ServiceAccountResponse(BaseModel):
    """Service account response (without sensitive data)."""

    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    api_key_prefix: str
    role: str
    allowed_spaces: list[UUID] | None
    allowed_operations: list[str] | None
    ip_allowlist: list[str] | None
    rate_limit_per_minute: int
    is_active: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    created_by_id: UUID
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

    service_account_id: UUID
    period_start: datetime
    period_end: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float | None
    requests_by_operation: dict[str, int]
    requests_by_day: list[dict]


class UsageRecordResponse(BaseModel):
    """Single usage record."""

    id: UUID
    timestamp: datetime
    operation: str
    resource_type: str | None
    resource_id: UUID | None
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
    params: dict | None = None


class McpResponse(BaseModel):
    """MCP JSON-RPC response."""

    jsonrpc: str = "2.0"
    id: str | int
    result: dict | None = None
    error: dict | None = None


class McpError(BaseModel):
    """MCP error object."""

    code: int
    message: str
    data: dict | None = None


# =============================================================================
# MCP Tool Schemas
# =============================================================================

class SearchDocumentsParams(BaseModel):
    """Parameters for search_documents tool."""

    query: str = Field(..., min_length=1)
    space_id: UUID | None = None
    limit: int = Field(default=10, ge=1, le=100)


class GetDocumentParams(BaseModel):
    """Parameters for get_document tool."""

    document_id: UUID


class ListSpacesParams(BaseModel):
    """Parameters for list_spaces tool."""

    workspace_id: UUID | None = None


class DocumentResult(BaseModel):
    """Document search result."""

    id: UUID
    title: str
    space_id: UUID
    space_name: str
    excerpt: str | None
    score: float | None
    status: str
    updated_at: datetime


class DocumentContent(BaseModel):
    """Full document content."""

    id: UUID
    title: str
    content_markdown: str
    content_html: str | None
    metadata: dict
    version: str
    status: str
    updated_at: datetime


class SpaceInfo(BaseModel):
    """Space information."""

    id: UUID
    name: str
    description: str | None
    workspace_id: UUID
    workspace_name: str
    page_count: int
```

### 2.2 Service Account Service

**File:** `backend/src/modules/mcp/service.py`

```python
"""Service account management service."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.service_account import ServiceAccount, ServiceAccountUsage
from src.modules.mcp.schemas import (
    ServiceAccountCreate,
    ServiceAccountUpdate,
    UsageStatsResponse,
)


class ServiceAccountService:
    """Service for managing service accounts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def generate_api_key() -> tuple[str, str, str]:
        """Generate a new API key.

        Returns:
            Tuple of (full_key, key_hash, key_prefix)
        """
        # Generate 32-byte random key, encode as hex (64 chars)
        key_bytes = secrets.token_bytes(32)
        full_key = f"dsk_{key_bytes.hex()}"  # dsk = doc service key
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        key_prefix = full_key[:12]  # "dsk_" + first 8 hex chars
        return full_key, key_hash, key_prefix

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for comparison."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    async def create(
        self,
        organization_id: UUID,
        created_by_id: UUID,
        data: ServiceAccountCreate,
    ) -> tuple[ServiceAccount, str]:
        """Create a new service account.

        Returns:
            Tuple of (service_account, api_key)
        """
        full_key, key_hash, key_prefix = self.generate_api_key()

        account = ServiceAccount(
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            api_key_hash=key_hash,
            api_key_prefix=key_prefix,
            role=data.role,
            allowed_spaces=[str(s) for s in data.allowed_spaces] if data.allowed_spaces else None,
            allowed_operations=data.allowed_operations,
            ip_allowlist=data.ip_allowlist,
            rate_limit_per_minute=data.rate_limit_per_minute,
            expires_at=data.expires_at,
            created_by_id=created_by_id,
        )

        self.db.add(account)
        await self.db.flush()
        await self.db.refresh(account)

        return account, full_key

    async def get_by_id(self, account_id: UUID) -> ServiceAccount | None:
        """Get service account by ID."""
        result = await self.db.execute(
            select(ServiceAccount)
            .where(ServiceAccount.id == account_id)
            .options(selectinload(ServiceAccount.created_by))
        )
        return result.scalar_one_or_none()

    async def get_by_api_key(self, api_key: str) -> ServiceAccount | None:
        """Get service account by API key."""
        key_hash = self.hash_api_key(api_key)
        key_prefix = api_key[:12]

        result = await self.db.execute(
            select(ServiceAccount)
            .where(
                ServiceAccount.api_key_prefix == key_prefix,
                ServiceAccount.api_key_hash == key_hash,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: UUID,
        include_inactive: bool = False,
    ) -> list[ServiceAccount]:
        """List service accounts for an organization."""
        query = select(ServiceAccount).where(
            ServiceAccount.organization_id == organization_id
        )

        if not include_inactive:
            query = query.where(ServiceAccount.is_active == True)

        query = query.order_by(ServiceAccount.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        account: ServiceAccount,
        data: ServiceAccountUpdate,
    ) -> ServiceAccount:
        """Update a service account."""
        update_data = data.model_dump(exclude_unset=True)

        # Handle allowed_spaces conversion
        if "allowed_spaces" in update_data and update_data["allowed_spaces"]:
            update_data["allowed_spaces"] = [str(s) for s in update_data["allowed_spaces"]]

        for field, value in update_data.items():
            setattr(account, field, value)

        await self.db.flush()
        await self.db.refresh(account)
        return account

    async def rotate_api_key(self, account: ServiceAccount) -> tuple[ServiceAccount, str]:
        """Rotate the API key for a service account."""
        full_key, key_hash, key_prefix = self.generate_api_key()

        account.api_key_hash = key_hash
        account.api_key_prefix = key_prefix

        await self.db.flush()
        await self.db.refresh(account)

        return account, full_key

    async def delete(self, account: ServiceAccount) -> None:
        """Delete a service account."""
        await self.db.delete(account)
        await self.db.flush()

    async def update_last_used(self, account: ServiceAccount) -> None:
        """Update the last_used_at timestamp."""
        account.last_used_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def record_usage(
        self,
        account_id: UUID,
        operation: str,
        response_code: int,
        ip_address: str | None = None,
        resource_type: str | None = None,
        resource_id: UUID | None = None,
        response_time_ms: int | None = None,
        error_message: str | None = None,
    ) -> None:
        """Record a usage event."""
        usage = ServiceAccountUsage(
            service_account_id=account_id,
            operation=operation,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            response_code=response_code,
            response_time_ms=response_time_ms,
            error_message=error_message,
        )
        self.db.add(usage)
        await self.db.flush()

    async def get_usage_stats(
        self,
        account_id: UUID,
        days: int = 30,
    ) -> UsageStatsResponse:
        """Get usage statistics for a service account."""
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(days=days)

        # Total counts
        total_result = await self.db.execute(
            select(
                func.count(ServiceAccountUsage.id).label("total"),
                func.count(ServiceAccountUsage.id).filter(
                    ServiceAccountUsage.response_code < 400
                ).label("successful"),
                func.avg(ServiceAccountUsage.response_time_ms).label("avg_time"),
            )
            .where(
                ServiceAccountUsage.service_account_id == account_id,
                ServiceAccountUsage.timestamp >= period_start,
            )
        )
        totals = total_result.one()

        # By operation
        op_result = await self.db.execute(
            select(
                ServiceAccountUsage.operation,
                func.count(ServiceAccountUsage.id).label("count"),
            )
            .where(
                ServiceAccountUsage.service_account_id == account_id,
                ServiceAccountUsage.timestamp >= period_start,
            )
            .group_by(ServiceAccountUsage.operation)
        )
        by_operation = {row.operation: row.count for row in op_result}

        # By day
        day_result = await self.db.execute(
            select(
                func.date_trunc("day", ServiceAccountUsage.timestamp).label("day"),
                func.count(ServiceAccountUsage.id).label("count"),
            )
            .where(
                ServiceAccountUsage.service_account_id == account_id,
                ServiceAccountUsage.timestamp >= period_start,
            )
            .group_by(func.date_trunc("day", ServiceAccountUsage.timestamp))
            .order_by(func.date_trunc("day", ServiceAccountUsage.timestamp))
        )
        by_day = [{"date": row.day.isoformat(), "count": row.count} for row in day_result]

        return UsageStatsResponse(
            service_account_id=account_id,
            period_start=period_start,
            period_end=period_end,
            total_requests=totals.total or 0,
            successful_requests=totals.successful or 0,
            failed_requests=(totals.total or 0) - (totals.successful or 0),
            avg_response_time_ms=float(totals.avg_time) if totals.avg_time else None,
            requests_by_operation=by_operation,
            requests_by_day=by_day,
        )

    def is_expired(self, account: ServiceAccount) -> bool:
        """Check if a service account has expired."""
        if account.expires_at is None:
            return False
        return datetime.now(timezone.utc) > account.expires_at

    def check_ip_allowed(self, account: ServiceAccount, ip_address: str) -> bool:
        """Check if an IP address is allowed."""
        import ipaddress

        if account.ip_allowlist is None:
            return True

        try:
            client_ip = ipaddress.ip_address(ip_address)
            for cidr in account.ip_allowlist:
                network = ipaddress.ip_network(cidr, strict=False)
                if client_ip in network:
                    return True
            return False
        except ValueError:
            return False
```

### 2.3 Rate Limiter

**File:** `backend/src/modules/mcp/rate_limiter.py`

```python
"""Rate limiting for MCP service accounts."""

import time
from collections import defaultdict
from dataclasses import dataclass
from threading import Lock
from uuid import UUID


@dataclass
class RateLimitState:
    """State for a single rate limit window."""

    tokens: float
    last_update: float


class RateLimiter:
    """Token bucket rate limiter for service accounts.

    Uses a simple in-memory implementation. For production with multiple
    workers, replace with Redis-based implementation.
    """

    def __init__(self):
        self._states: dict[UUID, RateLimitState] = defaultdict(
            lambda: RateLimitState(tokens=0, last_update=time.time())
        )
        self._lock = Lock()

    def check_rate_limit(
        self,
        account_id: UUID,
        rate_limit_per_minute: int,
    ) -> tuple[bool, int]:
        """Check if request is allowed under rate limit.

        Args:
            account_id: Service account ID
            rate_limit_per_minute: Maximum requests per minute

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        with self._lock:
            now = time.time()
            state = self._states[account_id]

            # Calculate tokens to add based on time elapsed
            elapsed = now - state.last_update
            tokens_to_add = elapsed * (rate_limit_per_minute / 60.0)

            # Update state
            state.tokens = min(rate_limit_per_minute, state.tokens + tokens_to_add)
            state.last_update = now

            if state.tokens >= 1:
                state.tokens -= 1
                return True, 0
            else:
                # Calculate retry after
                tokens_needed = 1 - state.tokens
                retry_after = int(tokens_needed * (60.0 / rate_limit_per_minute)) + 1
                return False, retry_after

    def reset(self, account_id: UUID) -> None:
        """Reset rate limit state for an account."""
        with self._lock:
            if account_id in self._states:
                del self._states[account_id]


# Global rate limiter instance
rate_limiter = RateLimiter()
```

### 2.4 API Key Authentication

**File:** `backend/src/modules/mcp/auth.py`

```python
"""API key authentication for MCP."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.db.models.service_account import ServiceAccount
from src.modules.mcp.rate_limiter import rate_limiter
from src.modules.mcp.service import ServiceAccountService


async def get_service_account(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> ServiceAccount:
    """Authenticate request using API key.

    Expected header format: Authorization: Bearer dsk_...
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = parts[1]
    if not api_key.startswith("dsk_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    service = ServiceAccountService(db)
    account = await service.get_by_api_key(api_key)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service account is deactivated",
        )

    if service.is_expired(account):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service account has expired",
        )

    # Check IP allowlist
    client_ip = request.client.host if request.client else None
    if client_ip and not service.check_ip_allowed(account, client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IP address not allowed",
        )

    # Check rate limit
    allowed, retry_after = rate_limiter.check_rate_limit(
        account.id, account.rate_limit_per_minute
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )

    # Update last used
    account.last_used_at = datetime.now(timezone.utc)
    await db.flush()

    return account


# Type alias for dependency injection
McpServiceAccount = Annotated[ServiceAccount, Depends(get_service_account)]
```

---

## Phase 3: Service Account API Endpoints (Day 5)

### 3.1 Service Account Endpoints

**File:** `backend/src/api/endpoints/service_accounts.py`

```python
"""Service account management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import CurrentUser, DbSession
from src.modules.audit.audit_service import AuditService
from src.modules.mcp.schemas import (
    ApiKeyRotateResponse,
    ServiceAccountCreate,
    ServiceAccountCreateResponse,
    ServiceAccountListResponse,
    ServiceAccountResponse,
    ServiceAccountUpdate,
    UsageStatsResponse,
)
from src.modules.mcp.service import ServiceAccountService

router = APIRouter()


@router.post(
    "",
    response_model=ServiceAccountCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service_account(
    data: ServiceAccountCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> ServiceAccountCreateResponse:
    """Create a new service account.

    The API key is only returned once in this response. Store it securely.
    """
    # TODO: Check user has admin role in organization
    organization_id = current_user.organization_id  # Assume user has org context

    service = ServiceAccountService(db)
    account, api_key = await service.create(
        organization_id=organization_id,
        created_by_id=current_user.id,
        data=data,
    )

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="mcp.service_account_created",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="service_account",
        resource_id=account.id,
        resource_name=account.name,
        details={
            "role": account.role,
            "rate_limit": account.rate_limit_per_minute,
        },
    )

    await db.commit()

    return ServiceAccountCreateResponse(
        **ServiceAccountResponse.model_validate(account).model_dump(),
        api_key=api_key,
    )


@router.get("", response_model=ServiceAccountListResponse)
async def list_service_accounts(
    db: DbSession,
    current_user: CurrentUser,
    include_inactive: bool = Query(False),
) -> ServiceAccountListResponse:
    """List service accounts for the organization."""
    organization_id = current_user.organization_id

    service = ServiceAccountService(db)
    accounts = await service.list_by_organization(
        organization_id, include_inactive=include_inactive
    )

    return ServiceAccountListResponse(
        accounts=[ServiceAccountResponse.model_validate(a) for a in accounts],
        total=len(accounts),
    )


@router.get("/{account_id}", response_model=ServiceAccountResponse)
async def get_service_account(
    account_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ServiceAccountResponse:
    """Get a service account by ID."""
    service = ServiceAccountService(db)
    account = await service.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service account not found",
        )

    # Check organization access
    if account.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return ServiceAccountResponse.model_validate(account)


@router.patch("/{account_id}", response_model=ServiceAccountResponse)
async def update_service_account(
    account_id: UUID,
    data: ServiceAccountUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> ServiceAccountResponse:
    """Update a service account."""
    service = ServiceAccountService(db)
    account = await service.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service account not found",
        )

    if account.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    account = await service.update(account, data)

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="mcp.service_account_updated",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="service_account",
        resource_id=account.id,
        resource_name=account.name,
        details=data.model_dump(exclude_unset=True),
    )

    await db.commit()

    return ServiceAccountResponse.model_validate(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_account(
    account_id: UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a service account."""
    service = ServiceAccountService(db)
    account = await service.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service account not found",
        )

    if account.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    account_name = account.name

    await service.delete(account)

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="mcp.service_account_deleted",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="service_account",
        resource_id=account_id,
        resource_name=account_name,
    )

    await db.commit()


@router.post("/{account_id}/rotate-key", response_model=ApiKeyRotateResponse)
async def rotate_api_key(
    account_id: UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiKeyRotateResponse:
    """Rotate the API key for a service account.

    The new API key is only returned once. Store it securely.
    """
    service = ServiceAccountService(db)
    account = await service.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service account not found",
        )

    if account.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    account, new_key = await service.rotate_api_key(account)

    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="mcp.api_key_rotated",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="service_account",
        resource_id=account.id,
        resource_name=account.name,
    )

    await db.commit()

    return ApiKeyRotateResponse(
        api_key=new_key,
        api_key_prefix=account.api_key_prefix,
    )


@router.get("/{account_id}/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    account_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    days: int = Query(30, ge=1, le=365),
) -> UsageStatsResponse:
    """Get usage statistics for a service account."""
    service = ServiceAccountService(db)
    account = await service.get_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service account not found",
        )

    if account.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return await service.get_usage_stats(account_id, days=days)
```

---

## Phase 4: MCP Server Implementation (Days 6-8)

### 4.1 MCP Tools Implementation

**File:** `backend/src/modules/mcp/tools.py`

```python
"""MCP tool implementations."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.service_account import ServiceAccount
from src.modules.content.content_service import ContentService
from src.modules.content.git_service import GitService
from src.modules.mcp.schemas import (
    DocumentContent,
    DocumentResult,
    GetDocumentParams,
    ListSpacesParams,
    SearchDocumentsParams,
    SpaceInfo,
)
from src.modules.search.search_service import SearchService


class McpTools:
    """MCP tool implementations."""

    def __init__(
        self,
        db: AsyncSession,
        service_account: ServiceAccount,
    ):
        self.db = db
        self.service_account = service_account
        self.content_service = ContentService(db)
        self.git_service = GitService(db)
        self.search_service = SearchService(db)

    def _check_space_access(self, space_id: UUID) -> bool:
        """Check if service account has access to a space."""
        if self.service_account.allowed_spaces is None:
            return True
        return str(space_id) in self.service_account.allowed_spaces

    def _check_operation_allowed(self, operation: str) -> bool:
        """Check if operation is allowed for service account."""
        if self.service_account.allowed_operations is None:
            return True
        return operation in self.service_account.allowed_operations

    async def search_documents(
        self, params: SearchDocumentsParams
    ) -> list[DocumentResult]:
        """Search for documents."""
        if not self._check_operation_allowed("search_documents"):
            raise PermissionError("Operation not allowed")

        # Filter by allowed spaces
        space_filter = None
        if params.space_id:
            if not self._check_space_access(params.space_id):
                raise PermissionError("Access to space denied")
            space_filter = [params.space_id]
        elif self.service_account.allowed_spaces:
            space_filter = [UUID(s) for s in self.service_account.allowed_spaces]

        results = await self.search_service.search(
            query=params.query,
            space_ids=space_filter,
            limit=params.limit,
            organization_id=self.service_account.organization_id,
        )

        return [
            DocumentResult(
                id=r.id,
                title=r.title,
                space_id=r.space_id,
                space_name=r.space_name,
                excerpt=r.excerpt,
                score=r.score,
                status=r.status,
                updated_at=r.updated_at,
            )
            for r in results
        ]

    async def get_document(self, params: GetDocumentParams) -> DocumentContent:
        """Get a document by ID."""
        if not self._check_operation_allowed("get_document"):
            raise PermissionError("Operation not allowed")

        page = await self.content_service.get_page(params.document_id)
        if not page:
            raise ValueError("Document not found")

        if not self._check_space_access(page.space_id):
            raise PermissionError("Access to document denied")

        # Get content as markdown
        content_md = await self.git_service.get_page_content_as_markdown(
            page.id, page.space_id
        )

        return DocumentContent(
            id=page.id,
            title=page.title,
            content_markdown=content_md,
            content_html=None,  # Could render if needed
            metadata={
                "document_number": page.document_number,
                "version": page.version,
                "revision": page.revision,
                "owner_id": str(page.owner_id) if page.owner_id else None,
                "classification": page.classification,
            },
            version=page.version or "1.0",
            status=page.status,
            updated_at=page.updated_at,
        )

    async def get_document_content(self, params: GetDocumentParams) -> str:
        """Get document content as markdown."""
        doc = await self.get_document(params)
        return doc.content_markdown

    async def list_spaces(self, params: ListSpacesParams) -> list[SpaceInfo]:
        """List accessible spaces."""
        if not self._check_operation_allowed("list_spaces"):
            raise PermissionError("Operation not allowed")

        spaces = await self.content_service.list_spaces(
            organization_id=self.service_account.organization_id,
            workspace_id=params.workspace_id,
        )

        # Filter by allowed spaces
        if self.service_account.allowed_spaces:
            allowed = set(self.service_account.allowed_spaces)
            spaces = [s for s in spaces if str(s.id) in allowed]

        return [
            SpaceInfo(
                id=s.id,
                name=s.name,
                description=s.description,
                workspace_id=s.workspace_id,
                workspace_name=s.workspace.name if s.workspace else "",
                page_count=len(s.pages) if s.pages else 0,
            )
            for s in spaces
        ]

    async def get_document_metadata(self, params: GetDocumentParams) -> dict:
        """Get document metadata."""
        if not self._check_operation_allowed("get_document_metadata"):
            raise PermissionError("Operation not allowed")

        page = await self.content_service.get_page(params.document_id)
        if not page:
            raise ValueError("Document not found")

        if not self._check_space_access(page.space_id):
            raise PermissionError("Access to document denied")

        return {
            "id": str(page.id),
            "title": page.title,
            "document_number": page.document_number,
            "version": page.version,
            "revision": page.revision,
            "status": page.status,
            "classification": page.classification,
            "owner_id": str(page.owner_id) if page.owner_id else None,
            "effective_date": page.effective_date.isoformat() if page.effective_date else None,
            "next_review_date": page.next_review_date.isoformat() if page.next_review_date else None,
            "created_at": page.created_at.isoformat(),
            "updated_at": page.updated_at.isoformat(),
        }

    async def get_document_history(self, params: GetDocumentParams) -> list[dict]:
        """Get document version history."""
        if not self._check_operation_allowed("get_document_history"):
            raise PermissionError("Operation not allowed")

        page = await self.content_service.get_page(params.document_id)
        if not page:
            raise ValueError("Document not found")

        if not self._check_space_access(page.space_id):
            raise PermissionError("Access to document denied")

        history = await self.git_service.get_page_history(page.id, page.space_id)

        return [
            {
                "sha": h.sha,
                "message": h.message,
                "author": h.author,
                "timestamp": h.timestamp.isoformat(),
            }
            for h in history
        ]
```

### 4.2 MCP Server

**File:** `backend/src/modules/mcp/server.py`

```python
"""MCP JSON-RPC server implementation."""

import time
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.service_account import ServiceAccount
from src.modules.mcp.schemas import (
    GetDocumentParams,
    ListSpacesParams,
    McpError,
    McpRequest,
    McpResponse,
    SearchDocumentsParams,
)
from src.modules.mcp.service import ServiceAccountService
from src.modules.mcp.tools import McpTools


# MCP Error Codes (JSON-RPC standard + custom)
class McpErrorCode:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # Custom codes
    PERMISSION_DENIED = -32000
    NOT_FOUND = -32001
    RATE_LIMITED = -32002


# Tool definitions for MCP discovery
MCP_TOOLS = [
    {
        "name": "search_documents",
        "description": "Search for documents in the documentation platform",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "space_id": {"type": "string", "description": "Optional space UUID to filter"},
                "limit": {"type": "integer", "default": 10, "maximum": 100},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_document",
        "description": "Get a document by ID with full content",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "description": "Document UUID"},
            },
            "required": ["document_id"],
        },
    },
    {
        "name": "get_document_content",
        "description": "Get document content as markdown",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "description": "Document UUID"},
            },
            "required": ["document_id"],
        },
    },
    {
        "name": "list_spaces",
        "description": "List accessible documentation spaces",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string", "description": "Optional workspace UUID"},
            },
        },
    },
    {
        "name": "get_document_metadata",
        "description": "Get document metadata (status, version, dates)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "description": "Document UUID"},
            },
            "required": ["document_id"],
        },
    },
    {
        "name": "get_document_history",
        "description": "Get document version history",
        "inputSchema": {
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "description": "Document UUID"},
            },
            "required": ["document_id"],
        },
    },
]

# Resource templates for MCP discovery
MCP_RESOURCES = [
    {
        "uriTemplate": "doc://{org}/{workspace}/{space}/{page}",
        "name": "Document",
        "description": "Access a specific document by path",
    },
    {
        "uriTemplate": "space://{org}/{workspace}/{space}",
        "name": "Space",
        "description": "Access a documentation space",
    },
]


class McpServer:
    """MCP JSON-RPC server."""

    def __init__(
        self,
        db: AsyncSession,
        service_account: ServiceAccount,
    ):
        self.db = db
        self.service_account = service_account
        self.tools = McpTools(db, service_account)
        self.service = ServiceAccountService(db)

    async def handle_request(self, request: McpRequest) -> McpResponse:
        """Handle an MCP JSON-RPC request."""
        start_time = time.time()
        response_code = 200
        error_message = None

        try:
            result = await self._dispatch(request)
            return McpResponse(
                id=request.id,
                result=result,
            )
        except PermissionError as e:
            response_code = 403
            error_message = str(e)
            return McpResponse(
                id=request.id,
                error=McpError(
                    code=McpErrorCode.PERMISSION_DENIED,
                    message=str(e),
                ).model_dump(),
            )
        except ValueError as e:
            response_code = 404
            error_message = str(e)
            return McpResponse(
                id=request.id,
                error=McpError(
                    code=McpErrorCode.NOT_FOUND,
                    message=str(e),
                ).model_dump(),
            )
        except Exception as e:
            response_code = 500
            error_message = str(e)
            return McpResponse(
                id=request.id,
                error=McpError(
                    code=McpErrorCode.INTERNAL_ERROR,
                    message="Internal server error",
                ).model_dump(),
            )
        finally:
            # Record usage
            elapsed_ms = int((time.time() - start_time) * 1000)
            await self.service.record_usage(
                account_id=self.service_account.id,
                operation=request.method,
                response_code=response_code,
                response_time_ms=elapsed_ms,
                error_message=error_message,
            )

    async def _dispatch(self, request: McpRequest) -> dict[str, Any]:
        """Dispatch request to appropriate handler."""
        method = request.method
        params = request.params or {}

        # MCP protocol methods
        if method == "initialize":
            return self._handle_initialize(params)
        elif method == "tools/list":
            return self._handle_tools_list()
        elif method == "resources/list":
            return self._handle_resources_list()
        elif method == "tools/call":
            return await self._handle_tools_call(params)
        elif method == "resources/read":
            return await self._handle_resources_read(params)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _handle_initialize(self, params: dict) -> dict:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
            },
            "serverInfo": {
                "name": "DocService MCP Server",
                "version": "1.0.0",
            },
        }

    def _handle_tools_list(self) -> dict:
        """Handle tools/list request."""
        # Filter tools based on allowed operations
        allowed_ops = self.service_account.allowed_operations
        if allowed_ops:
            tools = [t for t in MCP_TOOLS if t["name"] in allowed_ops]
        else:
            tools = MCP_TOOLS

        return {"tools": tools}

    def _handle_resources_list(self) -> dict:
        """Handle resources/list request."""
        return {"resources": MCP_RESOURCES}

    async def _handle_tools_call(self, params: dict) -> dict:
        """Handle tools/call request."""
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name == "search_documents":
            search_params = SearchDocumentsParams(**tool_args)
            results = await self.tools.search_documents(search_params)
            return {"content": [{"type": "text", "text": str([r.model_dump() for r in results])}]}

        elif tool_name == "get_document":
            doc_params = GetDocumentParams(document_id=UUID(tool_args["document_id"]))
            doc = await self.tools.get_document(doc_params)
            return {"content": [{"type": "text", "text": doc.model_dump_json()}]}

        elif tool_name == "get_document_content":
            doc_params = GetDocumentParams(document_id=UUID(tool_args["document_id"]))
            content = await self.tools.get_document_content(doc_params)
            return {"content": [{"type": "text", "text": content}]}

        elif tool_name == "list_spaces":
            list_params = ListSpacesParams(**tool_args)
            spaces = await self.tools.list_spaces(list_params)
            return {"content": [{"type": "text", "text": str([s.model_dump() for s in spaces])}]}

        elif tool_name == "get_document_metadata":
            doc_params = GetDocumentParams(document_id=UUID(tool_args["document_id"]))
            metadata = await self.tools.get_document_metadata(doc_params)
            return {"content": [{"type": "text", "text": str(metadata)}]}

        elif tool_name == "get_document_history":
            doc_params = GetDocumentParams(document_id=UUID(tool_args["document_id"]))
            history = await self.tools.get_document_history(doc_params)
            return {"content": [{"type": "text", "text": str(history)}]}

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _handle_resources_read(self, params: dict) -> dict:
        """Handle resources/read request."""
        uri = params.get("uri", "")

        if uri.startswith("doc://"):
            # Parse doc://org/workspace/space/page
            parts = uri[6:].split("/")
            if len(parts) < 4:
                raise ValueError("Invalid document URI")
            page_id = parts[-1]
            doc_params = GetDocumentParams(document_id=UUID(page_id))
            content = await self.tools.get_document_content(doc_params)
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/markdown",
                        "text": content,
                    }
                ]
            }

        raise ValueError(f"Unknown resource URI: {uri}")
```

### 4.3 MCP API Endpoint

**File:** `backend/src/api/endpoints/mcp.py`

```python
"""MCP JSON-RPC endpoint."""

from fastapi import APIRouter, Request

from src.api.deps import DbSession
from src.modules.audit.audit_service import AuditService
from src.modules.mcp.auth import McpServiceAccount
from src.modules.mcp.schemas import McpRequest, McpResponse
from src.modules.mcp.server import McpServer

router = APIRouter()


@router.post("", response_model=McpResponse)
async def mcp_endpoint(
    mcp_request: McpRequest,
    request: Request,
    db: DbSession,
    service_account: McpServiceAccount,
) -> McpResponse:
    """MCP JSON-RPC endpoint.

    Authenticate using API key: Authorization: Bearer dsk_...
    """
    server = McpServer(db, service_account)
    response = await server.handle_request(mcp_request)

    # Audit log for MCP requests
    audit = AuditService(db)
    await audit.log_event(
        event_type="mcp.request",
        actor_id=service_account.created_by_id,
        actor_email=f"sa:{service_account.name}",
        actor_ip=request.client.host if request.client else None,
        resource_type="mcp",
        resource_id=service_account.id,
        resource_name=mcp_request.method,
        details={
            "method": mcp_request.method,
            "has_error": response.error is not None,
        },
    )

    await db.commit()

    return response
```

### 4.4 Router Registration

**Update:** `backend/src/api/router.py`

```python
# Add imports
from src.api.endpoints import service_accounts, mcp

# Add router registrations
api_router.include_router(
    service_accounts.router,
    prefix="/service-accounts",
    tags=["Service Accounts"],
)

api_router.include_router(
    mcp.router,
    prefix="/mcp",
    tags=["MCP"],
)
```

---

## Phase 5: Frontend Implementation (Days 9-11)

### 5.1 API Client

**Update:** `frontend/src/lib/api.ts`

```typescript
// =============================================================================
// Service Account Types
// =============================================================================

export interface ServiceAccount {
  id: string;
  organization_id: string;
  name: string;
  description: string | null;
  api_key_prefix: string;
  role: 'viewer' | 'editor' | 'admin';
  allowed_spaces: string[] | null;
  allowed_operations: string[] | null;
  ip_allowlist: string[] | null;
  rate_limit_per_minute: number;
  is_active: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_by_id: string;
  created_at: string;
  updated_at: string;
}

export interface ServiceAccountCreate {
  name: string;
  description?: string;
  role?: 'viewer' | 'editor' | 'admin';
  allowed_spaces?: string[];
  allowed_operations?: string[];
  ip_allowlist?: string[];
  rate_limit_per_minute?: number;
  expires_at?: string;
}

export interface ServiceAccountUpdate {
  name?: string;
  description?: string;
  role?: 'viewer' | 'editor' | 'admin';
  allowed_spaces?: string[];
  allowed_operations?: string[];
  ip_allowlist?: string[];
  rate_limit_per_minute?: number;
  is_active?: boolean;
  expires_at?: string;
}

export interface ServiceAccountCreateResponse extends ServiceAccount {
  api_key: string;
}

export interface ApiKeyRotateResponse {
  api_key: string;
  api_key_prefix: string;
}

export interface UsageStats {
  service_account_id: string;
  period_start: string;
  period_end: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_response_time_ms: number | null;
  requests_by_operation: Record<string, number>;
  requests_by_day: Array<{ date: string; count: number }>;
}

// =============================================================================
// Service Account API
// =============================================================================

export const serviceAccountApi = {
  list: async (includeInactive = false): Promise<{ accounts: ServiceAccount[]; total: number }> => {
    const response = await api.get('/service-accounts', {
      params: { include_inactive: includeInactive },
    });
    return response.data;
  },

  get: async (id: string): Promise<ServiceAccount> => {
    const response = await api.get(`/service-accounts/${id}`);
    return response.data;
  },

  create: async (data: ServiceAccountCreate): Promise<ServiceAccountCreateResponse> => {
    const response = await api.post('/service-accounts', data);
    return response.data;
  },

  update: async (id: string, data: ServiceAccountUpdate): Promise<ServiceAccount> => {
    const response = await api.patch(`/service-accounts/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/service-accounts/${id}`);
  },

  rotateKey: async (id: string): Promise<ApiKeyRotateResponse> => {
    const response = await api.post(`/service-accounts/${id}/rotate-key`);
    return response.data;
  },

  getUsage: async (id: string, days = 30): Promise<UsageStats> => {
    const response = await api.get(`/service-accounts/${id}/usage`, {
      params: { days },
    });
    return response.data;
  },
};
```

### 5.2 Components

**File:** `frontend/src/components/mcp/ServiceAccountList.tsx`

```typescript
/**
 * ServiceAccountList - List and manage service accounts.
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { serviceAccountApi, type ServiceAccount } from '../../lib/api';
import { ServiceAccountForm } from './ServiceAccountForm';
import { ApiKeyDisplay } from './ApiKeyDisplay';
import { UsageStats } from './UsageStats';

export function ServiceAccountList() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [editingAccount, setEditingAccount] = useState<ServiceAccount | null>(null);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [includeInactive, setIncludeInactive] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['service-accounts', includeInactive],
    queryFn: () => serviceAccountApi.list(includeInactive),
  });

  const deleteMutation = useMutation({
    mutationFn: serviceAccountApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['service-accounts'] });
    },
  });

  const rotateKeyMutation = useMutation({
    mutationFn: serviceAccountApi.rotateKey,
    onSuccess: (data) => {
      setNewApiKey(data.api_key);
      queryClient.invalidateQueries({ queryKey: ['service-accounts'] });
    },
  });

  const handleDelete = async (account: ServiceAccount) => {
    if (confirm(`Delete service account "${account.name}"? This cannot be undone.`)) {
      await deleteMutation.mutateAsync(account.id);
    }
  };

  const handleRotateKey = async (account: ServiceAccount) => {
    if (confirm(`Rotate API key for "${account.name}"? The old key will stop working immediately.`)) {
      await rotateKeyMutation.mutateAsync(account.id);
    }
  };

  if (isLoading) {
    return <div className="p-4 text-gray-500">Loading...</div>;
  }

  const accounts = data?.accounts || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Service Accounts</h2>
          <p className="text-sm text-gray-500">
            Manage API access for external integrations and AI agents
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md"
        >
          Create Service Account
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={includeInactive}
            onChange={(e) => setIncludeInactive(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded"
          />
          Show inactive accounts
        </label>
      </div>

      {/* API Key Display Modal */}
      {newApiKey && (
        <ApiKeyDisplay
          apiKey={newApiKey}
          onClose={() => setNewApiKey(null)}
        />
      )}

      {/* Create/Edit Form Modal */}
      {(showCreate || editingAccount) && (
        <ServiceAccountForm
          account={editingAccount}
          onClose={() => {
            setShowCreate(false);
            setEditingAccount(null);
          }}
          onSuccess={(apiKey) => {
            if (apiKey) setNewApiKey(apiKey);
            setShowCreate(false);
            setEditingAccount(null);
          }}
        />
      )}

      {/* Usage Stats Modal */}
      {selectedAccountId && (
        <UsageStats
          accountId={selectedAccountId}
          onClose={() => setSelectedAccountId(null)}
        />
      )}

      {/* Account List */}
      {accounts.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No service accounts yet. Create one to enable API access.
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  API Key
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Last Used
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {accounts.map((account) => (
                <tr key={account.id} className={!account.is_active ? 'bg-gray-50' : ''}>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{account.name}</div>
                    {account.description && (
                      <div className="text-xs text-gray-500">{account.description}</div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {account.api_key_prefix}...
                    </code>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      account.role === 'admin'
                        ? 'bg-purple-100 text-purple-700'
                        : account.role === 'editor'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {account.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      account.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {account.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {account.last_used_at
                      ? new Date(account.last_used_at).toLocaleDateString()
                      : 'Never'}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      onClick={() => setSelectedAccountId(account.id)}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      Usage
                    </button>
                    <button
                      onClick={() => setEditingAccount(account)}
                      className="text-sm text-gray-600 hover:text-gray-800"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleRotateKey(account)}
                      className="text-sm text-amber-600 hover:text-amber-800"
                    >
                      Rotate Key
                    </button>
                    <button
                      onClick={() => handleDelete(account)}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* MCP Connection Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900">MCP Connection</h3>
        <p className="mt-1 text-sm text-blue-700">
          Connect AI agents using the MCP endpoint:
        </p>
        <code className="mt-2 block text-xs bg-blue-100 p-2 rounded">
          POST {window.location.origin}/api/v1/mcp
          <br />
          Authorization: Bearer dsk_your_api_key
        </code>
      </div>
    </div>
  );
}

export default ServiceAccountList;
```

### 5.3 Additional Components

Create the following additional components following similar patterns:

- **`frontend/src/components/mcp/ServiceAccountForm.tsx`** - Create/edit form with validation
- **`frontend/src/components/mcp/ApiKeyDisplay.tsx`** - One-time API key display with copy button
- **`frontend/src/components/mcp/UsageStats.tsx`** - Usage statistics dashboard with charts
- **`frontend/src/components/mcp/McpEndpointInfo.tsx`** - Connection instructions and examples
- **`frontend/src/components/mcp/index.ts`** - Barrel export

### 5.4 AdminPage Integration

**Update:** `frontend/src/pages/AdminPage.tsx`

```typescript
// Add to tabs array
{ id: 'integrations', label: 'Integrations', icon: PlugIcon }

// Add to tab content switch
case 'integrations':
  return <ServiceAccountList />;
```

---

## Phase 6: Testing (Days 12-14)

### 6.1 Backend Unit Tests

**File:** `backend/tests/unit/test_service_account_service.py`

```python
"""Unit tests for ServiceAccountService."""

import pytest
from uuid import uuid4

from src.modules.mcp.service import ServiceAccountService
from src.modules.mcp.schemas import ServiceAccountCreate


class TestServiceAccountService:
    """Tests for ServiceAccountService."""

    def test_generate_api_key(self):
        """Test API key generation."""
        full_key, key_hash, key_prefix = ServiceAccountService.generate_api_key()

        assert full_key.startswith("dsk_")
        assert len(full_key) == 68  # dsk_ + 64 hex chars
        assert len(key_hash) == 64  # SHA-256 hex
        assert len(key_prefix) == 12  # dsk_ + 8 chars

    def test_hash_api_key(self):
        """Test API key hashing."""
        key = "dsk_test123"
        hash1 = ServiceAccountService.hash_api_key(key)
        hash2 = ServiceAccountService.hash_api_key(key)

        assert hash1 == hash2
        assert len(hash1) == 64

    @pytest.mark.asyncio
    async def test_create_service_account(self, db_session, test_user, test_org):
        """Test creating a service account."""
        service = ServiceAccountService(db_session)
        data = ServiceAccountCreate(
            name="Test Account",
            description="Test description",
            role="viewer",
        )

        account, api_key = await service.create(
            organization_id=test_org.id,
            created_by_id=test_user.id,
            data=data,
        )

        assert account.name == "Test Account"
        assert account.role == "viewer"
        assert api_key.startswith("dsk_")

    @pytest.mark.asyncio
    async def test_get_by_api_key(self, db_session, test_service_account):
        """Test retrieving account by API key."""
        service = ServiceAccountService(db_session)

        # This would need the actual API key from creation
        # For unit tests, we can test the hash matching logic
        pass

    @pytest.mark.asyncio
    async def test_check_ip_allowed(self, db_session):
        """Test IP allowlist checking."""
        service = ServiceAccountService(db_session)

        # Create mock account with IP allowlist
        class MockAccount:
            ip_allowlist = ["192.168.1.0/24", "10.0.0.0/8"]

        account = MockAccount()

        assert service.check_ip_allowed(account, "192.168.1.100")
        assert service.check_ip_allowed(account, "10.1.2.3")
        assert not service.check_ip_allowed(account, "172.16.0.1")

        # Test with no allowlist (all allowed)
        account.ip_allowlist = None
        assert service.check_ip_allowed(account, "1.2.3.4")
```

### 6.2 Backend Integration Tests

**File:** `backend/tests/integration/test_service_accounts_api.py`

```python
"""Integration tests for service accounts API."""

import pytest
from httpx import AsyncClient


class TestServiceAccountsAPI:
    """Tests for service accounts API endpoints."""

    @pytest.mark.asyncio
    async def test_create_service_account(self, client: AsyncClient, auth_headers):
        """Test creating a service account."""
        response = await client.post(
            "/api/v1/service-accounts",
            json={
                "name": "Test Integration Account",
                "description": "For testing",
                "role": "viewer",
                "rate_limit_per_minute": 100,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Integration Account"
        assert "api_key" in data  # Only returned on creation
        assert data["api_key"].startswith("dsk_")

    @pytest.mark.asyncio
    async def test_list_service_accounts(self, client: AsyncClient, auth_headers):
        """Test listing service accounts."""
        response = await client.get(
            "/api/v1/service-accounts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_rotate_api_key(self, client: AsyncClient, auth_headers, test_service_account):
        """Test rotating API key."""
        response = await client.post(
            f"/api/v1/service-accounts/{test_service_account.id}/rotate-key",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("dsk_")

    @pytest.mark.asyncio
    async def test_mcp_endpoint_auth(self, client: AsyncClient, test_api_key):
        """Test MCP endpoint authentication."""
        response = await client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "initialize",
                "params": {},
            },
            headers={"Authorization": f"Bearer {test_api_key}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"]["serverInfo"]["name"] == "DocService MCP Server"

    @pytest.mark.asyncio
    async def test_mcp_tools_list(self, client: AsyncClient, test_api_key):
        """Test MCP tools/list."""
        response = await client.post(
            "/api/v1/mcp",
            json={
                "jsonrpc": "2.0",
                "id": "2",
                "method": "tools/list",
            },
            headers={"Authorization": f"Bearer {test_api_key}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "tools" in data["result"]
        tool_names = [t["name"] for t in data["result"]["tools"]]
        assert "search_documents" in tool_names

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client: AsyncClient, test_api_key_low_limit):
        """Test rate limiting."""
        # Send requests until rate limited
        for i in range(10):
            response = await client.post(
                "/api/v1/mcp",
                json={"jsonrpc": "2.0", "id": str(i), "method": "tools/list"},
                headers={"Authorization": f"Bearer {test_api_key_low_limit}"},
            )
            if response.status_code == 429:
                assert "Retry-After" in response.headers
                break
        else:
            pytest.fail("Rate limiting did not trigger")
```

### 6.3 Frontend Tests

**File:** `frontend/src/components/mcp/__tests__/ServiceAccountList.test.tsx`

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ServiceAccountList } from '../ServiceAccountList';
import { serviceAccountApi } from '../../../lib/api';

jest.mock('../../../lib/api');

describe('ServiceAccountList', () => {
  const queryClient = new QueryClient();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders empty state', async () => {
    (serviceAccountApi.list as jest.Mock).mockResolvedValue({
      accounts: [],
      total: 0,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ServiceAccountList />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/No service accounts yet/)).toBeInTheDocument();
    });
  });

  it('renders service account list', async () => {
    (serviceAccountApi.list as jest.Mock).mockResolvedValue({
      accounts: [
        {
          id: '1',
          name: 'Test Account',
          api_key_prefix: 'dsk_test1234',
          role: 'viewer',
          is_active: true,
          last_used_at: null,
        },
      ],
      total: 1,
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ServiceAccountList />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Account')).toBeInTheDocument();
    });
  });
});
```

---

## Verification Checklist

### Functional Requirements

- [ ] Admin can create service accounts with name, description, role
- [ ] API key is generated and displayed only once at creation
- [ ] API key can be rotated (old key invalidated immediately)
- [ ] Service accounts can be deactivated without deletion
- [ ] Service accounts can be deleted (with usage history)
- [ ] IP allowlist restricts access by source IP
- [ ] Rate limiting enforces requests per minute
- [ ] Expiration date disables account after expiry

### MCP Protocol

- [ ] `initialize` returns protocol version and capabilities
- [ ] `tools/list` returns available tools based on permissions
- [ ] `tools/call` executes tools with proper parameter validation
- [ ] `resources/list` returns resource templates
- [ ] `resources/read` returns document content

### Security

- [ ] API keys are hashed (SHA-256) before storage
- [ ] API key prefix enables identification without exposure
- [ ] All MCP operations logged to audit trail
- [ ] Rate limiting prevents abuse
- [ ] IP allowlist enforced before processing
- [ ] Expired accounts rejected at authentication

### Frontend

- [ ] Service account list with search and filter
- [ ] Create form with validation
- [ ] API key display with copy button (one-time)
- [ ] Edit form for updating settings
- [ ] Usage statistics with charts
- [ ] MCP connection instructions

### Testing

- [ ] Unit tests for service layer (>80% coverage)
- [ ] Integration tests for API endpoints
- [ ] Rate limiting tests
- [ ] Frontend component tests
- [ ] E2E test for full workflow

---

## File Summary

### New Backend Files

```
backend/
├── alembic/versions/011_mcp_integration.py
└── src/
    ├── db/models/service_account.py
    ├── modules/mcp/
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── rate_limiter.py
    │   ├── schemas.py
    │   ├── server.py
    │   ├── service.py
    │   └── tools.py
    └── api/endpoints/
        ├── service_accounts.py
        └── mcp.py
```

### New Frontend Files

```
frontend/src/
├── components/mcp/
│   ├── ApiKeyDisplay.tsx
│   ├── McpEndpointInfo.tsx
│   ├── ServiceAccountForm.tsx
│   ├── ServiceAccountList.tsx
│   ├── UsageStats.tsx
│   └── index.ts
└── lib/api.ts (updated)
```

### Modified Files

```
backend/src/api/router.py
backend/src/db/models/__init__.py
backend/src/db/models/organization.py
frontend/src/pages/AdminPage.tsx
```

---

## Commands Reference

```bash
# Run backend tests
cd backend && pytest tests/unit/test_service_account*.py -v
cd backend && pytest tests/integration/test_service_accounts*.py -v
cd backend && pytest tests/integration/test_mcp*.py -v

# Run migrations
docker exec docservice-backend alembic upgrade head

# Run frontend tests
cd frontend && npm test -- --grep "ServiceAccount"

# Type checking
cd frontend && npx tsc --noEmit
```
