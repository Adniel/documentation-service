"""Git remote API endpoints.

Sprint 13: Git Remote Support
"""

import secrets
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from sqlalchemy import select

from src.api.deps import DbSession, CurrentUser
from src.db.models.organization import Organization
from src.db.models.git_credential import CredentialType
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
    WebhookRegenerateResponse,
    ConnectionTestResult,
)
from src.modules.git.credential_service import CredentialService, CredentialError
from src.modules.git.sync_service import SyncService, SyncError
from src.modules.audit.audit_service import AuditService

router = APIRouter()


async def get_org(db: DbSession, org_id: str) -> Organization:
    """Get organization or raise 404."""
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    return org


# =============================================================================
# Remote Configuration
# =============================================================================


@router.get("/organizations/{org_id}/remote", response_model=RemoteConfigResponse)
async def get_remote_config(
    org_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> RemoteConfigResponse:
    """Get remote configuration for an organization."""
    org = await get_org(db, org_id)

    # Check if credentials exist
    cred_service = CredentialService(db)
    credential = await cred_service.get_credential(org_id)

    return RemoteConfigResponse(
        organization_id=str(org.id),
        remote_url=org.git_remote_url,
        provider=org.git_remote_provider,
        sync_enabled=org.git_sync_enabled,
        sync_strategy=org.git_sync_strategy,
        default_branch=org.git_default_branch,
        last_sync_at=org.git_last_sync_at,
        sync_status=org.git_sync_status,
        has_credentials=credential is not None,
    )


@router.put("/organizations/{org_id}/remote", response_model=RemoteConfigResponse)
async def configure_remote(
    org_id: str,
    config: RemoteConfigCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> RemoteConfigResponse:
    """Configure remote for an organization."""
    org = await get_org(db, org_id)

    # Update organization
    org.git_remote_url = config.remote_url
    org.git_remote_provider = config.provider.value
    org.git_sync_enabled = config.sync_enabled
    org.git_sync_strategy = config.sync_strategy.value
    org.git_default_branch = config.default_branch
    org.git_sync_status = "not_configured"

    # Generate webhook secret if not exists
    if not org.git_webhook_secret:
        org.git_webhook_secret = secrets.token_urlsafe(32)

    await db.flush()

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="git.remote_configured",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="organization",
        resource_id=str(org.id),
        details={
            "remote_url": config.remote_url,
            "provider": config.provider.value,
            "sync_strategy": config.sync_strategy.value,
        },
    )
    await db.commit()

    cred_service = CredentialService(db)
    credential = await cred_service.get_credential(org_id)

    return RemoteConfigResponse(
        organization_id=str(org.id),
        remote_url=org.git_remote_url,
        provider=org.git_remote_provider,
        sync_enabled=org.git_sync_enabled,
        sync_strategy=org.git_sync_strategy,
        default_branch=org.git_default_branch,
        last_sync_at=org.git_last_sync_at,
        sync_status=org.git_sync_status,
        has_credentials=credential is not None,
    )


@router.patch("/organizations/{org_id}/remote", response_model=RemoteConfigResponse)
async def update_remote_config(
    org_id: str,
    config: RemoteConfigUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> RemoteConfigResponse:
    """Update remote configuration for an organization."""
    org = await get_org(db, org_id)

    # Update only provided fields
    if config.remote_url is not None:
        org.git_remote_url = config.remote_url
    if config.provider is not None:
        org.git_remote_provider = config.provider.value
    if config.sync_enabled is not None:
        org.git_sync_enabled = config.sync_enabled
    if config.sync_strategy is not None:
        org.git_sync_strategy = config.sync_strategy.value
    if config.default_branch is not None:
        org.git_default_branch = config.default_branch

    await db.flush()

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="git.remote_updated",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="organization",
        resource_id=str(org.id),
        details=config.model_dump(exclude_unset=True),
    )
    await db.commit()

    cred_service = CredentialService(db)
    credential = await cred_service.get_credential(org_id)

    return RemoteConfigResponse(
        organization_id=str(org.id),
        remote_url=org.git_remote_url,
        provider=org.git_remote_provider,
        sync_enabled=org.git_sync_enabled,
        sync_strategy=org.git_sync_strategy,
        default_branch=org.git_default_branch,
        last_sync_at=org.git_last_sync_at,
        sync_status=org.git_sync_status,
        has_credentials=credential is not None,
    )


@router.delete("/organizations/{org_id}/remote", status_code=status.HTTP_204_NO_CONTENT)
async def remove_remote_config(
    org_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Remove remote configuration from an organization."""
    org = await get_org(db, org_id)

    # Clear remote configuration
    org.git_remote_url = None
    org.git_remote_provider = None
    org.git_sync_enabled = False
    org.git_sync_strategy = None
    org.git_sync_status = None
    org.git_webhook_secret = None

    # Delete credential if exists
    cred_service = CredentialService(db)
    await cred_service.delete_credential(org_id)

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="git.remote_removed",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="organization",
        resource_id=str(org.id),
    )
    await db.commit()


@router.post("/organizations/{org_id}/remote/test", response_model=ConnectionTestResult)
async def test_remote_connection(
    org_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> ConnectionTestResult:
    """Test connection to remote repository."""
    org = await get_org(db, org_id)

    sync_service = SyncService(db)
    result = await sync_service.test_connection(org_id)

    return ConnectionTestResult(**result)


# =============================================================================
# Credentials
# =============================================================================


@router.post("/organizations/{org_id}/credentials", response_model=CredentialResponse)
async def create_credential(
    org_id: str,
    cred: CredentialCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> CredentialResponse:
    """Create or replace credentials for an organization."""
    org = await get_org(db, org_id)

    cred_service = CredentialService(db)

    # Delete existing credential if present
    existing = await cred_service.get_credential(org_id)
    if existing:
        await cred_service.delete_credential(org_id)

    try:
        credential = await cred_service.create_credential(
            organization_id=org_id,
            credential_type=CredentialType(cred.credential_type.value),
            value=cred.value,
            created_by_id=str(current_user.id),
            label=cred.label,
            expires_at=cred.expires_at,
            provider=org.git_remote_provider,
        )
    except CredentialError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="git.credential_added",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="organization",
        resource_id=str(org.id),
        details={
            "credential_type": credential.credential_type.value,
            "label": credential.label,
        },
    )
    await db.commit()

    return CredentialResponse(
        id=str(credential.id),
        organization_id=str(credential.organization_id),
        credential_type=credential.credential_type.value,
        key_fingerprint=credential.key_fingerprint,
        label=credential.label,
        expires_at=credential.expires_at,
        is_expired=credential.is_expired,
        created_at=credential.created_at,
        created_by_id=str(credential.created_by_id),
    )


@router.get("/organizations/{org_id}/credentials", response_model=CredentialResponse)
async def get_credential(
    org_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> CredentialResponse:
    """Get credential metadata (not the secret value)."""
    await get_org(db, org_id)

    cred_service = CredentialService(db)
    credential = await cred_service.get_credential(org_id)

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No credential found for this organization",
        )

    return CredentialResponse(
        id=str(credential.id),
        organization_id=str(credential.organization_id),
        credential_type=credential.credential_type.value,
        key_fingerprint=credential.key_fingerprint,
        label=credential.label,
        expires_at=credential.expires_at,
        is_expired=credential.is_expired,
        created_at=credential.created_at,
        created_by_id=str(credential.created_by_id),
    )


@router.delete("/organizations/{org_id}/credentials", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    org_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete credential for an organization."""
    await get_org(db, org_id)

    cred_service = CredentialService(db)
    deleted = await cred_service.delete_credential(org_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No credential found for this organization",
        )

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="git.credential_removed",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="organization",
        resource_id=org_id,
    )
    await db.commit()


# =============================================================================
# Sync Operations
# =============================================================================


@router.post("/organizations/{org_id}/sync", response_model=SyncResponse)
async def trigger_sync(
    org_id: str,
    sync_request: SyncRequest,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> SyncResponse:
    """Trigger a sync operation."""
    await get_org(db, org_id)

    sync_service = SyncService(db)

    try:
        result = await sync_service.sync(
            org_id=org_id,
            branch=sync_request.branch,
            triggered_by_id=str(current_user.id),
            trigger_source="manual",
            force=sync_request.force,
        )
        await db.commit()
    except SyncError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return SyncResponse(
        success=result.get("success", False),
        event_id=result.get("event_id", ""),
        event_type=result.get("event_type", ""),
        status=result.get("status", ""),
        branch=result.get("branch", ""),
        commit_sha_before=result.get("commit_sha_before"),
        commit_sha_after=result.get("commit_sha_after"),
        message=result.get("message"),
        files_changed=result.get("files_changed", []),
    )


@router.get("/organizations/{org_id}/sync/status")
async def get_sync_status(
    org_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Get sync status for an organization."""
    await get_org(db, org_id)

    sync_service = SyncService(db)

    try:
        return await sync_service.get_sync_status(org_id)
    except SyncError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/organizations/{org_id}/sync/history", response_model=SyncHistoryResponse)
async def get_sync_history(
    org_id: str,
    db: DbSession,
    current_user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> SyncHistoryResponse:
    """Get sync history for an organization."""
    await get_org(db, org_id)

    sync_service = SyncService(db)
    result = await sync_service.get_sync_history(org_id, limit, offset)

    return SyncHistoryResponse(
        events=result["events"],
        total=result["total"],
    )


# =============================================================================
# Webhooks
# =============================================================================


@router.get("/organizations/{org_id}/webhook", response_model=WebhookInfo)
async def get_webhook_info(
    org_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> WebhookInfo:
    """Get webhook URL and secret status."""
    org = await get_org(db, org_id)

    # Construct webhook URL
    base_url = str(request.base_url).rstrip("/")
    webhook_url = f"{base_url}/api/v1/webhooks/git/{org_id}"

    return WebhookInfo(
        webhook_url=webhook_url,
        has_secret=org.git_webhook_secret is not None,
    )


@router.post("/organizations/{org_id}/webhook/regenerate", response_model=WebhookRegenerateResponse)
async def regenerate_webhook_secret(
    org_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> WebhookRegenerateResponse:
    """Regenerate webhook secret."""
    org = await get_org(db, org_id)

    # Generate new secret
    new_secret = secrets.token_urlsafe(32)
    org.git_webhook_secret = new_secret

    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="git.webhook_secret_regenerated",
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_ip=request.client.host if request.client else None,
        resource_type="organization",
        resource_id=str(org.id),
    )
    await db.commit()

    # Construct webhook URL
    base_url = str(request.base_url).rstrip("/")
    webhook_url = f"{base_url}/api/v1/webhooks/git/{org_id}"

    return WebhookRegenerateResponse(
        webhook_url=webhook_url,
        secret=new_secret,
    )
