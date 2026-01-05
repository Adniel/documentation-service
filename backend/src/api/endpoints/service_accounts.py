"""Service account management API endpoints.

Sprint C: MCP Integration
"""

from fastapi import APIRouter, HTTPException, Query, Request, status

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
    # Get organization from current user
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization",
        )

    service = ServiceAccountService(db)
    account, api_key = await service.create(
        organization_id=current_user.organization_id,
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

    response_data = ServiceAccountResponse.model_validate(account).model_dump()
    return ServiceAccountCreateResponse(**response_data, api_key=api_key)


@router.get("", response_model=ServiceAccountListResponse)
async def list_service_accounts(
    db: DbSession,
    current_user: CurrentUser,
    include_inactive: bool = Query(False),
) -> ServiceAccountListResponse:
    """List service accounts for the organization."""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization",
        )

    service = ServiceAccountService(db)
    accounts = await service.list_by_organization(
        current_user.organization_id, include_inactive=include_inactive
    )

    return ServiceAccountListResponse(
        accounts=[ServiceAccountResponse.model_validate(a) for a in accounts],
        total=len(accounts),
    )


@router.get("/{account_id}", response_model=ServiceAccountResponse)
async def get_service_account(
    account_id: str,
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
    account_id: str,
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
    account_id: str,
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
    account_id: str,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiKeyRotateResponse:
    """Rotate the API key for a service account.

    The new API key is only returned once. Store it securely.
    The old key will stop working immediately.
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
    account_id: str,
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
