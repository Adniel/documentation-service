"""Git module - Remote repository synchronization.

Sprint 13: Git Remote Support

This module provides:
- Credential management with AES-256 encryption
- Remote configuration and sync operations
- Webhook handling for GitHub/GitLab
- Sync event logging
"""

from src.modules.git.schemas import (
    RemoteConfigCreate,
    RemoteConfigUpdate,
    RemoteConfigResponse,
    CredentialCreate,
    CredentialResponse,
    SyncRequest,
    SyncResponse,
    SyncHistoryResponse,
    WebhookInfo,
)

__all__ = [
    "RemoteConfigCreate",
    "RemoteConfigUpdate",
    "RemoteConfigResponse",
    "CredentialCreate",
    "CredentialResponse",
    "SyncRequest",
    "SyncResponse",
    "SyncHistoryResponse",
    "WebhookInfo",
]
