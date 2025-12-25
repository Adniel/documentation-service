"""Permission service for Sprint 5 Access Control.

Implements permission checking with inheritance through the content hierarchy:
Organization → Workspace → Space → Page

Access requires BOTH:
1. Hierarchical role permission (inherited or explicit)
2. Classification clearance (user clearance >= resource classification)

Compliance: ISO 9001 §7.5.3, ISO 13485 §4.2.4, 21 CFR §11.10(d)
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.permission import (
    Permission,
    Role,
    ResourceType,
    ClassificationLevel,
    ROLE_CAPABILITIES,
)
from src.db.models.user import User
from src.db.models.organization import Organization
from src.db.models.workspace import Workspace
from src.db.models.space import Space
from src.db.models.page import Page


class PermissionDeniedError(Exception):
    """Raised when permission check fails."""

    def __init__(
        self,
        message: str = "Permission denied",
        required_role: Optional[Role] = None,
        user_role: Optional[Role] = None,
        required_clearance: Optional[int] = None,
        user_clearance: Optional[int] = None,
    ):
        self.message = message
        self.required_role = required_role
        self.user_role = user_role
        self.required_clearance = required_clearance
        self.user_clearance = user_clearance
        super().__init__(message)


class PermissionService:
    """Service for managing and checking permissions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------------------------------
    # Permission Resolution
    # -------------------------------------------------------------------------

    async def get_resource_hierarchy(
        self,
        resource_type: str,
        resource_id: str,
    ) -> list[tuple[str, str]]:
        """Get the hierarchy of parent resources for inheritance.

        Returns list of (resource_type, resource_id) from root to leaf.
        """
        hierarchy: list[tuple[str, str]] = []

        if resource_type == ResourceType.ORGANIZATION:
            hierarchy.append((ResourceType.ORGANIZATION, resource_id))

        elif resource_type == ResourceType.WORKSPACE:
            # Get workspace to find organization
            result = await self.db.execute(
                select(Workspace).where(Workspace.id == resource_id)
            )
            workspace = result.scalar_one_or_none()
            if workspace:
                hierarchy.append((ResourceType.ORGANIZATION, str(workspace.organization_id)))
                hierarchy.append((ResourceType.WORKSPACE, resource_id))

        elif resource_type == ResourceType.SPACE:
            # Get space to find workspace and organization
            result = await self.db.execute(
                select(Space).options(selectinload(Space.workspace)).where(Space.id == resource_id)
            )
            space = result.scalar_one_or_none()
            if space and space.workspace:
                hierarchy.append((ResourceType.ORGANIZATION, str(space.workspace.organization_id)))
                hierarchy.append((ResourceType.WORKSPACE, str(space.workspace_id)))
                hierarchy.append((ResourceType.SPACE, resource_id))

        elif resource_type == ResourceType.PAGE:
            # Get page to find space, workspace, and organization
            result = await self.db.execute(
                select(Page)
                .options(
                    selectinload(Page.space).selectinload(Space.workspace)
                )
                .where(Page.id == resource_id)
            )
            page = result.scalar_one_or_none()
            if page and page.space and page.space.workspace:
                hierarchy.append((ResourceType.ORGANIZATION, str(page.space.workspace.organization_id)))
                hierarchy.append((ResourceType.WORKSPACE, str(page.space.workspace_id)))
                hierarchy.append((ResourceType.SPACE, str(page.space_id)))
                hierarchy.append((ResourceType.PAGE, resource_id))

        return hierarchy

    async def get_effective_role(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
    ) -> Optional[Role]:
        """Get user's effective role at a resource after inheritance resolution.

        Permission inheritance:
        - Permissions are inherited from parent to child
        - Child-level permissions override parent permissions
        - Most permissive role at the resource level wins

        Returns None if user has no permission.
        """
        # Get the hierarchy from root to leaf
        hierarchy = await self.get_resource_hierarchy(resource_type, resource_id)
        if not hierarchy:
            return None

        # Build query to get all permissions in the hierarchy
        conditions = [
            and_(
                Permission.resource_type == rtype,
                Permission.resource_id == rid,
            )
            for rtype, rid in hierarchy
        ]

        result = await self.db.execute(
            select(Permission).where(
                and_(
                    Permission.user_id == user_id,
                    Permission.is_active == True,
                    or_(*conditions),
                    or_(
                        Permission.expires_at == None,
                        Permission.expires_at > datetime.utcnow(),
                    ),
                )
            )
        )
        permissions = result.scalars().all()

        if not permissions:
            return None

        # Map hierarchy levels for sorting
        hierarchy_order = {(rtype, rid): i for i, (rtype, rid) in enumerate(hierarchy)}

        # Sort by hierarchy level (most specific first)
        permissions_sorted = sorted(
            permissions,
            key=lambda p: hierarchy_order.get((p.resource_type, p.resource_id), 999),
            reverse=True,
        )

        # Return the most permissive role
        # If there's a permission at the most specific level, use that
        # Otherwise, inherit from parent
        best_role: Optional[Role] = None
        for perm in permissions_sorted:
            role = Role(perm.role)
            if best_role is None or role.value > best_role.value:
                best_role = role

        return best_role

    async def get_resource_classification(
        self,
        resource_type: str,
        resource_id: str,
    ) -> int:
        """Get the classification level of a resource."""
        if resource_type == ResourceType.ORGANIZATION:
            # Organizations don't have classification
            return ClassificationLevel.PUBLIC

        elif resource_type == ResourceType.WORKSPACE:
            # Workspaces don't have classification (inherit from org)
            return ClassificationLevel.PUBLIC

        elif resource_type == ResourceType.SPACE:
            result = await self.db.execute(
                select(Space.classification).where(Space.id == resource_id)
            )
            classification = result.scalar_one_or_none()
            return classification if classification is not None else ClassificationLevel.PUBLIC

        elif resource_type == ResourceType.PAGE:
            result = await self.db.execute(
                select(Page.classification).where(Page.id == resource_id)
            )
            classification = result.scalar_one_or_none()
            return classification if classification is not None else ClassificationLevel.PUBLIC

        return ClassificationLevel.PUBLIC

    async def get_user_clearance(self, user_id: str) -> int:
        """Get user's clearance level."""
        result = await self.db.execute(
            select(User.clearance_level).where(User.id == user_id)
        )
        clearance = result.scalar_one_or_none()
        return clearance if clearance is not None else ClassificationLevel.PUBLIC

    # -------------------------------------------------------------------------
    # Permission Checking
    # -------------------------------------------------------------------------

    async def check_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        required_role: Role,
        check_classification: bool = True,
    ) -> tuple[bool, str]:
        """Check if user has access to a resource.

        Returns (allowed, reason) tuple.

        Access requires:
        1. User has effective role >= required_role
        2. User clearance >= resource classification (if check_classification=True)
        """
        # Check if user is superuser
        result = await self.db.execute(
            select(User.is_superuser).where(User.id == user_id)
        )
        is_superuser = result.scalar_one_or_none()
        if is_superuser:
            return True, "Superuser access"

        # Get effective role
        effective_role = await self.get_effective_role(user_id, resource_type, resource_id)
        if effective_role is None:
            return False, "No permission for this resource"

        # Check role level
        if not effective_role.can_perform(required_role):
            return False, f"Requires {required_role.name.lower()} role or higher, user has {effective_role.name.lower()}"

        # Check classification if needed
        if check_classification:
            classification = await self.get_resource_classification(resource_type, resource_id)
            clearance = await self.get_user_clearance(user_id)

            if clearance < classification:
                return False, f"Resource classification ({classification}) exceeds user clearance ({clearance})"

        return True, f"Access granted with {effective_role.name.lower()} role"

    async def require_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        required_role: Role,
        check_classification: bool = True,
    ) -> None:
        """Require access or raise PermissionDeniedError."""
        allowed, reason = await self.check_access(
            user_id, resource_type, resource_id, required_role, check_classification
        )
        if not allowed:
            raise PermissionDeniedError(reason)

    async def can_perform_action(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
    ) -> tuple[bool, str]:
        """Check if user can perform a specific action.

        Actions:
        - read: View content
        - comment: Add comments
        - edit: Modify content
        - delete_own: Delete own content
        - delete_any: Delete any content
        - approve: Approve changes
        - manage_members: Manage user permissions
        - manage_settings: Modify resource settings
        - delete_resource: Delete the resource itself
        """
        # Map action to required role
        action_role_map = {
            "read": Role.VIEWER,
            "comment": Role.REVIEWER,
            "edit": Role.EDITOR,
            "delete_own": Role.EDITOR,
            "delete_any": Role.ADMIN,
            "approve": Role.REVIEWER,
            "manage_members": Role.ADMIN,
            "manage_settings": Role.ADMIN,
            "delete_resource": Role.OWNER,
        }

        required_role = action_role_map.get(action)
        if required_role is None:
            return False, f"Unknown action: {action}"

        return await self.check_access(user_id, resource_type, resource_id, required_role)

    # -------------------------------------------------------------------------
    # Permission Management
    # -------------------------------------------------------------------------

    async def grant_permission(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        role: Role,
        granted_by_id: str,
        reason: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Permission:
        """Grant a permission to a user.

        Raises PermissionDeniedError if granter doesn't have sufficient permissions.
        """
        # Check if granter has permission to grant
        granter_role = await self.get_effective_role(granted_by_id, resource_type, resource_id)

        # Check if granter is superuser
        result = await self.db.execute(
            select(User.is_superuser).where(User.id == granted_by_id)
        )
        is_superuser = result.scalar_one_or_none()

        if not is_superuser:
            if granter_role is None:
                raise PermissionDeniedError("No permission to grant permissions on this resource")
            if not granter_role.can_perform(Role.ADMIN):
                raise PermissionDeniedError("Requires admin role to grant permissions")
            if role.value > granter_role.value:
                raise PermissionDeniedError("Cannot grant role higher than your own")

        # Check if permission already exists
        result = await self.db.execute(
            select(Permission).where(
                and_(
                    Permission.user_id == user_id,
                    Permission.resource_type == resource_type,
                    Permission.resource_id == resource_id,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing permission
            existing.role = role.value
            existing.granted_by_id = granted_by_id
            existing.granted_at = datetime.utcnow()
            existing.reason = reason
            existing.expires_at = expires_at
            existing.is_active = True
            await self.db.flush()
            return existing

        # Create new permission
        permission = Permission(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            role=role.value,
            granted_by_id=granted_by_id,
            granted_at=datetime.utcnow(),
            reason=reason,
            expires_at=expires_at,
        )
        self.db.add(permission)
        await self.db.flush()
        return permission

    async def revoke_permission(
        self,
        permission_id: str,
        revoked_by_id: str,
    ) -> bool:
        """Revoke a permission (soft delete).

        Returns True if revoked, False if not found.
        """
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            return False

        # Check if revoker has permission
        revoker_role = await self.get_effective_role(
            revoked_by_id, permission.resource_type, permission.resource_id
        )

        # Check if revoker is superuser
        result = await self.db.execute(
            select(User.is_superuser).where(User.id == revoked_by_id)
        )
        is_superuser = result.scalar_one_or_none()

        if not is_superuser:
            if revoker_role is None or not revoker_role.can_perform(Role.ADMIN):
                raise PermissionDeniedError("Requires admin role to revoke permissions")

        permission.is_active = False
        await self.db.flush()
        return True

    async def list_permissions(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        include_inactive: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Permission]:
        """List permissions with optional filters."""
        query = select(Permission)

        conditions = []
        if resource_type:
            conditions.append(Permission.resource_type == resource_type)
        if resource_id:
            conditions.append(Permission.resource_id == resource_id)
        if user_id:
            conditions.append(Permission.user_id == user_id)
        if not include_inactive:
            conditions.append(Permission.is_active == True)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Permission.granted_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_effective_permissions(
        self,
        resource_type: str,
        resource_id: str,
    ) -> list[dict]:
        """Get all effective permissions for a resource including inheritance.

        Returns list of {user_id, user_name, user_email, effective_role, source}.
        """
        hierarchy = await self.get_resource_hierarchy(resource_type, resource_id)
        if not hierarchy:
            return []

        # Get all permissions in hierarchy
        conditions = [
            and_(
                Permission.resource_type == rtype,
                Permission.resource_id == rid,
            )
            for rtype, rid in hierarchy
        ]

        result = await self.db.execute(
            select(Permission)
            .options(selectinload(Permission.user))
            .where(
                and_(
                    Permission.is_active == True,
                    or_(*conditions),
                    or_(
                        Permission.expires_at == None,
                        Permission.expires_at > datetime.utcnow(),
                    ),
                )
            )
        )
        permissions = result.scalars().all()

        # Group by user and find effective role
        user_permissions: dict[str, dict] = {}
        for perm in permissions:
            uid = str(perm.user_id)
            role = Role(perm.role)

            if uid not in user_permissions:
                user_permissions[uid] = {
                    "user_id": uid,
                    "user_name": perm.user.full_name if perm.user else None,
                    "user_email": perm.user.email if perm.user else None,
                    "effective_role": role,
                    "sources": [],
                }
            else:
                # Update if higher role
                if role.value > user_permissions[uid]["effective_role"].value:
                    user_permissions[uid]["effective_role"] = role

            user_permissions[uid]["sources"].append({
                "resource_type": perm.resource_type,
                "resource_id": perm.resource_id,
                "role": role.name.lower(),
            })

        return list(user_permissions.values())


# Convenience functions for dependency injection
async def get_permission_service(db: AsyncSession) -> PermissionService:
    """Get permission service instance."""
    return PermissionService(db)
