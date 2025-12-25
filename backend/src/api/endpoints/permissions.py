"""Permission management API endpoints.

Sprint 5: Access Control
Compliance: ISO 9001 §7.5.3, ISO 13485 §4.2.4, 21 CFR §11.10(d)
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.db.models.user import User
from src.db.models.permission import Permission, Role, ResourceType, ROLE_CAPABILITIES
from src.modules.access.permission_service import PermissionService, PermissionDeniedError
from src.modules.access.dependencies import get_permission_service, require_superuser
from src.modules.audit import AuditService
from src.modules.access.schemas import (
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
    PermissionListResponse,
    EffectivePermission,
    EffectivePermissionsResponse,
    EffectivePermissionSource,
    AccessCheckRequest,
    AccessCheckResponse,
    ClearanceUpdateRequest,
    ClearanceUpdateResponse,
    RoleCapability,
    RoleCapabilitiesResponse,
    RoleEnum,
    ResourceTypeEnum,
)

router = APIRouter(prefix="/permissions", tags=["Permissions"])


def _permission_to_response(permission: Permission) -> PermissionResponse:
    """Convert Permission model to response schema."""
    return PermissionResponse(
        id=str(permission.id),
        user_id=str(permission.user_id),
        user_name=permission.user.full_name if permission.user else None,
        user_email=permission.user.email if permission.user else None,
        resource_type=permission.resource_type,
        resource_id=str(permission.resource_id),
        role=Role(permission.role).name.lower(),
        granted_by_id=str(permission.granted_by_id),
        granted_by_name=permission.granted_by.full_name if permission.granted_by else None,
        granted_at=permission.granted_at,
        reason=permission.reason,
        is_active=permission.is_active,
        expires_at=permission.expires_at,
        created_at=permission.created_at,
        updated_at=permission.updated_at,
    )


@router.get("", response_model=PermissionListResponse)
async def list_permissions(
    resource_type: Optional[ResourceTypeEnum] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    include_inactive: bool = Query(False, description="Include inactive permissions"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
    db: AsyncSession = Depends(get_db),
) -> PermissionListResponse:
    """List permissions with optional filters.

    Requires authenticated user. Results are filtered based on user's
    access to the resources.
    """
    permissions = await permission_service.list_permissions(
        resource_type=resource_type.value if resource_type else None,
        resource_id=resource_id,
        user_id=user_id,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )

    # Count total
    query = select(func.count(Permission.id))
    conditions = []
    if resource_type:
        conditions.append(Permission.resource_type == resource_type.value)
    if resource_id:
        conditions.append(Permission.resource_id == resource_id)
    if user_id:
        conditions.append(Permission.user_id == user_id)
    if not include_inactive:
        conditions.append(Permission.is_active == True)

    if conditions:
        from sqlalchemy import and_
        query = query.where(and_(*conditions))

    result = await db.execute(query)
    total = result.scalar() or 0

    return PermissionListResponse(
        items=[_permission_to_response(p) for p in permissions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def grant_permission(
    request: Request,
    data: PermissionCreate,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
    db: AsyncSession = Depends(get_db),
) -> PermissionResponse:
    """Grant a permission to a user.

    Requirements:
    - Caller must have Admin or Owner role at the target scope
    - Cannot grant role higher than caller's own role
    """
    try:
        # Convert enum to Role
        role = Role[data.role.value.upper()]

        permission = await permission_service.grant_permission(
            user_id=data.user_id,
            resource_type=data.resource_type.value,
            resource_id=data.resource_id,
            role=role,
            granted_by_id=str(current_user.id),
            reason=data.reason,
            expires_at=data.expires_at,
        )

        # Log access grant to audit trail
        audit_service = AuditService(db)
        await audit_service.log_access_granted(
            granted_by_id=str(current_user.id),
            granted_by_email=current_user.email,
            user_id=data.user_id,
            user_email=permission.user.email if permission.user else "",
            resource_type=data.resource_type.value,
            resource_id=data.resource_id,
            role=role.name.lower(),
            reason=data.reason,
            ip_address=request.client.host if request.client else None,
        )
        await db.commit()

        return _permission_to_response(permission)

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PermissionResponse:
    """Get a specific permission by ID."""
    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    return _permission_to_response(permission)


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_permission(
    request: Request,
    permission_id: str,
    reason: Optional[str] = Query(None, description="Reason for revoking"),
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Revoke a permission.

    Requirements:
    - Caller must have Admin or Owner role at the target scope
    - Cannot revoke if it would leave resource without owner
    """
    # Get permission first for audit logging
    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    permission = result.scalar_one_or_none()

    try:
        success = await permission_service.revoke_permission(
            permission_id=permission_id,
            revoked_by_id=str(current_user.id),
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found",
            )

        # Log access revocation to audit trail
        if permission:
            audit_service = AuditService(db)
            await audit_service.log_access_revoked(
                revoked_by_id=str(current_user.id),
                revoked_by_email=current_user.email,
                user_id=str(permission.user_id),
                user_email=permission.user.email if permission.user else "",
                resource_type=permission.resource_type,
                resource_id=str(permission.resource_id),
                reason=reason,
                ip_address=request.client.host if request.client else None,
            )
        await db.commit()

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/resource/{resource_type}/{resource_id}",
    response_model=PermissionListResponse,
)
async def get_resource_permissions(
    resource_type: ResourceTypeEnum,
    resource_id: str,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
) -> PermissionListResponse:
    """Get all direct permissions for a specific resource.

    Does not include inherited permissions.
    """
    permissions = await permission_service.list_permissions(
        resource_type=resource_type.value,
        resource_id=resource_id,
    )

    return PermissionListResponse(
        items=[_permission_to_response(p) for p in permissions],
        total=len(permissions),
        limit=len(permissions),
        offset=0,
    )


@router.get(
    "/effective/{resource_type}/{resource_id}",
    response_model=EffectivePermissionsResponse,
)
async def get_effective_permissions(
    resource_type: ResourceTypeEnum,
    resource_id: str,
    user_id: Optional[str] = Query(None, description="Filter to specific user"),
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
) -> EffectivePermissionsResponse:
    """Get effective permissions for a resource after inheritance resolution.

    Includes all users who have access through any level of the hierarchy.
    """
    # Get classification
    classification = await permission_service.get_resource_classification(
        resource_type.value, resource_id
    )

    # Get effective permissions
    effective_perms = await permission_service.get_effective_permissions(
        resource_type.value, resource_id
    )

    # Filter by user if specified
    if user_id:
        effective_perms = [p for p in effective_perms if p["user_id"] == user_id]

    # Convert to response format
    permissions = []
    for perm in effective_perms:
        # Check clearance
        user_clearance = await permission_service.get_user_clearance(perm["user_id"])
        has_access = user_clearance >= classification

        permissions.append(EffectivePermission(
            user_id=perm["user_id"],
            user_name=perm.get("user_name"),
            user_email=perm.get("user_email"),
            effective_role=perm["effective_role"].name.lower(),
            clearance_level=user_clearance,
            has_access=has_access,
            sources=[
                EffectivePermissionSource(
                    resource_type=s["resource_type"],
                    resource_id=s["resource_id"],
                    role=s["role"],
                )
                for s in perm.get("sources", [])
            ],
        ))

    return EffectivePermissionsResponse(
        resource_type=resource_type.value,
        resource_id=resource_id,
        classification=classification,
        effective_permissions=permissions,
    )


@router.post("/check", response_model=AccessCheckResponse)
async def check_access(
    data: AccessCheckRequest,
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
) -> AccessCheckResponse:
    """Check if a user can perform a specific action on a resource.

    This is the primary authorization check endpoint.
    """
    # Get effective role
    effective_role = await permission_service.get_effective_role(
        data.user_id, data.resource_type.value, data.resource_id
    )

    # Get classification info
    classification = await permission_service.get_resource_classification(
        data.resource_type.value, data.resource_id
    )
    user_clearance = await permission_service.get_user_clearance(data.user_id)

    # Check action permission
    allowed, reason = await permission_service.can_perform_action(
        user_id=data.user_id,
        resource_type=data.resource_type.value,
        resource_id=data.resource_id,
        action=data.action.value,
    )

    return AccessCheckResponse(
        allowed=allowed,
        reason=reason,
        effective_role=effective_role.name.lower() if effective_role else None,
        clearance_sufficient=user_clearance >= classification,
        required_clearance=classification,
        user_clearance=user_clearance,
    )


@router.get("/roles/capabilities", response_model=RoleCapabilitiesResponse)
async def get_role_capabilities(
    current_user: User = Depends(get_current_user),
) -> RoleCapabilitiesResponse:
    """Get the capability matrix for all roles."""
    roles = {}
    for role, caps in ROLE_CAPABILITIES.items():
        roles[role.name.lower()] = RoleCapability(**caps)

    return RoleCapabilitiesResponse(roles=roles)


# -------------------------------------------------------------------------
# User clearance endpoints
# -------------------------------------------------------------------------

@router.patch(
    "/users/{user_id}/clearance",
    response_model=ClearanceUpdateResponse,
)
async def update_user_clearance(
    request: Request,
    user_id: str,
    data: ClearanceUpdateRequest,
    current_user: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
) -> ClearanceUpdateResponse:
    """Update a user's classification clearance level.

    Requires superuser access.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    previous_clearance = user.clearance_level
    user.clearance_level = data.clearance_level
    await db.flush()

    # Log clearance change to audit trail
    audit_service = AuditService(db)
    await audit_service.log_clearance_change(
        changed_by_id=str(current_user.id),
        changed_by_email=current_user.email,
        user_id=user_id,
        user_email=user.email,
        previous_clearance=previous_clearance,
        new_clearance=data.clearance_level,
        reason=data.reason,
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    return ClearanceUpdateResponse(
        user_id=str(user.id),
        previous_clearance=previous_clearance,
        new_clearance=data.clearance_level,
        updated_by=str(current_user.id),
        reason=data.reason,
        updated_at=datetime.utcnow(),
    )


@router.get("/users/{user_id}/permissions", response_model=PermissionListResponse)
async def get_user_permissions(
    user_id: str,
    scope: Optional[ResourceTypeEnum] = Query(None, description="Filter by scope"),
    current_user: User = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service),
) -> PermissionListResponse:
    """Get all permissions for a specific user."""
    # Users can view their own permissions, admins can view any
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own permissions unless superuser",
        )

    permissions = await permission_service.list_permissions(
        user_id=user_id,
        resource_type=scope.value if scope else None,
    )

    return PermissionListResponse(
        items=[_permission_to_response(p) for p in permissions],
        total=len(permissions),
        limit=len(permissions),
        offset=0,
    )
