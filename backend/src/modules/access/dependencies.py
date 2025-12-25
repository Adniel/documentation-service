"""Access control dependencies for FastAPI.

Provides dependency injection for permission checking in API endpoints.

Usage:
    @router.get("/pages/{page_id}")
    async def get_page(
        page_id: str,
        _: None = Depends(require_permission(ResourceType.PAGE, Role.VIEWER)),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        ...

Compliance: ISO 9001 §7.5.3, 21 CFR §11.10(d)
"""

from functools import wraps
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.db.models.user import User
from src.db.models.permission import Role, ResourceType
from src.modules.access.permission_service import PermissionService, PermissionDeniedError
from src.modules.audit import AuditService


async def get_permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    """Dependency to get permission service."""
    return PermissionService(db)


class PermissionChecker:
    """Dependency class for checking permissions.

    Can be used as a FastAPI dependency to check permissions before
    endpoint execution.
    """

    def __init__(
        self,
        resource_type: str,
        required_role: Role,
        resource_id_param: str = "page_id",
        check_classification: bool = True,
    ):
        """Initialize permission checker.

        Args:
            resource_type: Type of resource to check
            required_role: Minimum role required
            resource_id_param: Name of path parameter containing resource ID
            check_classification: Whether to check classification clearance
        """
        self.resource_type = resource_type
        self.required_role = required_role
        self.resource_id_param = resource_id_param
        self.check_classification = check_classification

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service),
    ) -> None:
        """Check permission for the current request."""
        # Get resource ID from path parameters
        resource_id = request.path_params.get(self.resource_id_param)
        if not resource_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing path parameter: {self.resource_id_param}",
            )

        # Check permission
        allowed, reason = await permission_service.check_access(
            user_id=str(current_user.id),
            resource_type=self.resource_type,
            resource_id=resource_id,
            required_role=self.required_role,
            check_classification=self.check_classification,
        )

        if not allowed:
            # Log access denial for security monitoring (21 CFR §11.10(d))
            audit_service = AuditService(permission_service.db)
            effective_role = await permission_service.get_effective_role(
                str(current_user.id), self.resource_type, resource_id
            )
            await audit_service.log_access_denied(
                user_id=str(current_user.id),
                user_email=current_user.email,
                resource_type=self.resource_type,
                resource_id=resource_id,
                required_role=self.required_role.name.lower(),
                user_role=effective_role.name.lower() if effective_role else None,
                reason=reason,
                ip_address=request.client.host if request.client else None,
            )
            await permission_service.db.commit()

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=reason,
            )


def require_permission(
    resource_type: str,
    required_role: Role,
    resource_id_param: str = "page_id",
    check_classification: bool = True,
) -> PermissionChecker:
    """Create a permission checker dependency.

    Usage:
        @router.get("/pages/{page_id}")
        async def get_page(
            page_id: str,
            _: None = Depends(require_permission(ResourceType.PAGE, Role.VIEWER)),
        ):
            ...
    """
    return PermissionChecker(
        resource_type=resource_type,
        required_role=required_role,
        resource_id_param=resource_id_param,
        check_classification=check_classification,
    )


# Convenience dependencies for common permission checks
def require_page_viewer(page_id_param: str = "page_id") -> PermissionChecker:
    """Require viewer permission for a page."""
    return require_permission(ResourceType.PAGE, Role.VIEWER, page_id_param)


def require_page_editor(page_id_param: str = "page_id") -> PermissionChecker:
    """Require editor permission for a page."""
    return require_permission(ResourceType.PAGE, Role.EDITOR, page_id_param)


def require_page_admin(page_id_param: str = "page_id") -> PermissionChecker:
    """Require admin permission for a page."""
    return require_permission(ResourceType.PAGE, Role.ADMIN, page_id_param)


def require_space_viewer(space_id_param: str = "space_id") -> PermissionChecker:
    """Require viewer permission for a space."""
    return require_permission(ResourceType.SPACE, Role.VIEWER, space_id_param)


def require_space_editor(space_id_param: str = "space_id") -> PermissionChecker:
    """Require editor permission for a space."""
    return require_permission(ResourceType.SPACE, Role.EDITOR, space_id_param)


def require_space_admin(space_id_param: str = "space_id") -> PermissionChecker:
    """Require admin permission for a space."""
    return require_permission(ResourceType.SPACE, Role.ADMIN, space_id_param)


def require_workspace_viewer(workspace_id_param: str = "workspace_id") -> PermissionChecker:
    """Require viewer permission for a workspace."""
    return require_permission(ResourceType.WORKSPACE, Role.VIEWER, workspace_id_param)


def require_workspace_admin(workspace_id_param: str = "workspace_id") -> PermissionChecker:
    """Require admin permission for a workspace."""
    return require_permission(ResourceType.WORKSPACE, Role.ADMIN, workspace_id_param)


def require_org_admin(org_id_param: str = "org_id") -> PermissionChecker:
    """Require admin permission for an organization."""
    return require_permission(ResourceType.ORGANIZATION, Role.ADMIN, org_id_param)


def require_org_owner(org_id_param: str = "org_id") -> PermissionChecker:
    """Require owner permission for an organization."""
    return require_permission(ResourceType.ORGANIZATION, Role.OWNER, org_id_param)


class RequireSuperuser:
    """Dependency to require superuser access."""

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Check if current user is superuser."""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superuser access required",
            )
        return current_user


require_superuser = RequireSuperuser()


class RequireAdminOrOwner:
    """Dependency to require admin or owner for resource management."""

    def __init__(self, resource_type: str, resource_id_param: str):
        self.resource_type = resource_type
        self.resource_id_param = resource_id_param

    async def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service),
    ) -> User:
        """Check if user is admin or owner."""
        resource_id = request.path_params.get(self.resource_id_param)
        if not resource_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing path parameter: {self.resource_id_param}",
            )

        # Superusers always have access
        if current_user.is_superuser:
            return current_user

        effective_role = await permission_service.get_effective_role(
            user_id=str(current_user.id),
            resource_type=self.resource_type,
            resource_id=resource_id,
        )

        if effective_role is None or not effective_role.can_perform(Role.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin or owner role required",
            )

        return current_user
