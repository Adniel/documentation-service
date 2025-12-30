"""Git module schemas - Pydantic models for API.

Sprint 13: Git Remote Support
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class GitProvider(str, Enum):
    """Supported Git hosting providers."""

    GITHUB = "github"
    GITLAB = "gitlab"
    GITEA = "gitea"
    CUSTOM = "custom"


class SyncStrategy(str, Enum):
    """Git sync strategies."""

    PUSH_ONLY = "push_only"
    PULL_ONLY = "pull_only"
    BIDIRECTIONAL = "bidirectional"


class SyncStatusType(str, Enum):
    """Status of sync configuration."""

    SYNCED = "synced"
    PENDING = "pending"
    ERROR = "error"
    CONFLICT = "conflict"
    NOT_CONFIGURED = "not_configured"


class CredentialTypeEnum(str, Enum):
    """Types of Git credentials."""

    SSH_KEY = "ssh_key"
    HTTPS_TOKEN = "https_token"
    DEPLOY_KEY = "deploy_key"


# =============================================================================
# Remote Configuration
# =============================================================================


class RemoteConfigCreate(BaseModel):
    """Create remote configuration for an organization."""

    remote_url: str = Field(..., min_length=1, max_length=500)
    provider: GitProvider
    sync_strategy: SyncStrategy = SyncStrategy.PUSH_ONLY
    default_branch: str = Field(default="main", min_length=1, max_length=100)
    sync_enabled: bool = False

    @field_validator("remote_url")
    @classmethod
    def validate_remote_url(cls, v: str) -> str:
        """Validate Git remote URL format."""
        v = v.strip()
        if not (
            v.startswith("git@")
            or v.startswith("https://")
            or v.startswith("ssh://")
        ):
            raise ValueError(
                "Remote URL must start with git@, https://, or ssh://"
            )
        return v


class RemoteConfigUpdate(BaseModel):
    """Update remote configuration."""

    remote_url: Optional[str] = Field(None, min_length=1, max_length=500)
    provider: Optional[GitProvider] = None
    sync_strategy: Optional[SyncStrategy] = None
    default_branch: Optional[str] = Field(None, min_length=1, max_length=100)
    sync_enabled: Optional[bool] = None

    @field_validator("remote_url")
    @classmethod
    def validate_remote_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate Git remote URL format if provided."""
        if v is None:
            return v
        v = v.strip()
        if not (
            v.startswith("git@")
            or v.startswith("https://")
            or v.startswith("ssh://")
        ):
            raise ValueError(
                "Remote URL must start with git@, https://, or ssh://"
            )
        return v


class RemoteConfigResponse(BaseModel):
    """Response for remote configuration."""

    organization_id: str
    remote_url: Optional[str] = None
    provider: Optional[str] = None
    sync_enabled: bool = False
    sync_strategy: Optional[str] = None
    default_branch: str = "main"
    last_sync_at: Optional[datetime] = None
    sync_status: Optional[str] = None
    has_credentials: bool = False

    model_config = {"from_attributes": True}


# =============================================================================
# Credentials
# =============================================================================


class CredentialCreate(BaseModel):
    """Create Git credentials."""

    credential_type: CredentialTypeEnum
    value: str = Field(..., min_length=1)
    label: Optional[str] = Field(None, max_length=100)
    expires_at: Optional[datetime] = None


class CredentialResponse(BaseModel):
    """Response for credential (without secret value)."""

    id: str
    organization_id: str
    credential_type: str
    key_fingerprint: Optional[str] = None
    label: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_expired: bool = False
    created_at: datetime
    created_by_id: str

    model_config = {"from_attributes": True}


# =============================================================================
# Sync Operations
# =============================================================================


class SyncRequest(BaseModel):
    """Request to trigger a sync operation."""

    branch: Optional[str] = None  # Uses default branch if not specified
    force: bool = False  # Force push/pull (dangerous)


class SyncResponse(BaseModel):
    """Response from sync operation."""

    success: bool
    event_id: str
    event_type: str
    status: str
    branch: str
    commit_sha_before: Optional[str] = None
    commit_sha_after: Optional[str] = None
    message: Optional[str] = None
    files_changed: list[str] = Field(default_factory=list)


class SyncHistoryItem(BaseModel):
    """Single sync event in history."""

    id: str
    event_type: str
    direction: str
    status: str
    branch_name: str
    commit_sha_before: Optional[str] = None
    commit_sha_after: Optional[str] = None
    error_message: Optional[str] = None
    trigger_source: Optional[str] = None
    triggered_by_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    model_config = {"from_attributes": True}


class SyncHistoryResponse(BaseModel):
    """Response for sync history."""

    events: list[SyncHistoryItem]
    total: int


# =============================================================================
# Webhooks
# =============================================================================


class WebhookInfo(BaseModel):
    """Webhook configuration info."""

    webhook_url: str
    has_secret: bool


class WebhookRegenerateResponse(BaseModel):
    """Response after regenerating webhook secret."""

    webhook_url: str
    secret: str  # Only returned once on regeneration


# =============================================================================
# Connection Test
# =============================================================================


class ConnectionTestResult(BaseModel):
    """Result of testing remote connection."""

    success: bool
    message: str
    remote_url: Optional[str] = None
    default_branch: Optional[str] = None
    last_commit: Optional[str] = None
