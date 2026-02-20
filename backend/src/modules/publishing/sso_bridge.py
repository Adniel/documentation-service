"""SSO Bridge for published sites.

Sprint D: Integrated Access Control

Bridges internal users (authenticated via main app SSO) to published sites.
Allows internal users to access published sites with their clearance level
without needing separate visitor accounts.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.site_visitor import SiteVisitor
from src.db.models.site_visitor_role import SiteVisitorRole
from src.db.models.published_site import PublishedSite, SiteVisibility
from src.db.models.user import User


@dataclass
class SSOBridgeResult:
    """Result of SSO bridge operation."""

    success: bool
    visitor: Optional[SiteVisitor]
    internal_user: Optional[User]
    clearance_level: int
    reason: str


class SSOBridge:
    """Bridges internal users to published site access.

    When an internal user accesses a published site:
    1. Check if they're authenticated via main app SSO
    2. If so, create/link a SiteVisitor record for them
    3. Apply their internal clearance level to site access
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_visitor_for_internal_user(
        self,
        user: User,
    ) -> Optional[SiteVisitor]:
        """Get site visitor linked to an internal user."""
        result = await self.db.execute(
            select(SiteVisitor).where(SiteVisitor.internal_user_id == user.id)
        )
        return result.scalar_one_or_none()

    async def link_internal_user(
        self,
        user: User,
    ) -> SiteVisitor:
        """Create or get site visitor for an internal user.

        Links the internal user to a site visitor record for
        consistent tracking across published sites.
        """
        # Check for existing link
        visitor = await self.get_visitor_for_internal_user(user)
        if visitor:
            # Update display name if changed
            if visitor.display_name != user.display_name:
                visitor.display_name = user.display_name
                await self.db.flush()
            return visitor

        # Check if visitor exists with same email (might be invited externally first)
        result = await self.db.execute(
            select(SiteVisitor).where(SiteVisitor.email == user.email.lower())
        )
        visitor = result.scalar_one_or_none()

        if visitor:
            # Link existing visitor to internal user
            visitor.internal_user_id = user.id
            visitor.display_name = user.display_name
            await self.db.flush()
            return visitor

        # Create new visitor linked to internal user
        visitor = SiteVisitor(
            id=str(uuid4()),
            email=user.email.lower(),
            display_name=user.display_name,
            internal_user_id=user.id,
            created_at=datetime.utcnow(),
        )
        self.db.add(visitor)
        await self.db.flush()
        return visitor

    async def check_site_access(
        self,
        user: User,
        site: PublishedSite,
    ) -> SSOBridgeResult:
        """Check if internal user can access a published site.

        Returns SSO bridge result with access decision and clearance level.
        """
        # Public sites are always accessible
        if site.visibility == SiteVisibility.PUBLIC.value:
            visitor = await self.link_internal_user(user)
            return SSOBridgeResult(
                success=True,
                visitor=visitor,
                internal_user=user,
                clearance_level=user.clearance_level,
                reason="Public site access with internal clearance",
            )

        # Authenticated sites require valid internal user
        if site.visibility == SiteVisibility.AUTHENTICATED.value:
            visitor = await self.link_internal_user(user)
            return SSOBridgeResult(
                success=True,
                visitor=visitor,
                internal_user=user,
                clearance_level=user.clearance_level,
                reason="Authenticated site access with internal clearance",
            )

        # Restricted sites check email domain
        if site.visibility == SiteVisibility.RESTRICTED.value:
            if not site.allowed_email_domains:
                # No domains = internal users only allowed
                visitor = await self.link_internal_user(user)
                return SSOBridgeResult(
                    success=True,
                    visitor=visitor,
                    internal_user=user,
                    clearance_level=user.clearance_level,
                    reason="Internal user access to restricted site",
                )

            # Check if user's email domain is allowed
            domain = user.email.split("@")[-1].lower() if "@" in user.email else ""
            allowed_domains = [d.lower() for d in site.allowed_email_domains]

            if domain in allowed_domains:
                visitor = await self.link_internal_user(user)
                return SSOBridgeResult(
                    success=True,
                    visitor=visitor,
                    internal_user=user,
                    clearance_level=user.clearance_level,
                    reason=f"Internal user with allowed domain: {domain}",
                )

            return SSOBridgeResult(
                success=False,
                visitor=None,
                internal_user=user,
                clearance_level=0,
                reason=f"Internal user domain {domain} not in allowed list",
            )

        return SSOBridgeResult(
            success=False,
            visitor=None,
            internal_user=user,
            clearance_level=0,
            reason=f"Unknown site visibility: {site.visibility}",
        )

    async def get_effective_clearance(
        self,
        user: User,
        site: PublishedSite,
    ) -> int:
        """Get effective clearance level for internal user on a site.

        Uses the internal user's clearance level directly, as they
        are already authenticated and authorized within the main system.
        """
        return user.clearance_level

    async def has_explicit_page_access(
        self,
        user: User,
        site: PublishedSite,
        page_id: str,
    ) -> bool:
        """Check if internal user has explicit access to a specific page.

        Internal users inherit their main system permissions, so we check
        if they have permissions on the page in the main system.
        """
        # For internal users, we rely on the main permission system
        # This is handled by the access_service which checks both
        # classification and ACLs using the internal User object
        return False  # No special visitor role overrides for internal users

    async def unlink_internal_user(
        self,
        user: User,
    ) -> bool:
        """Unlink an internal user from their site visitor record.

        Useful when an internal user is deactivated.
        Returns True if a visitor was unlinked.
        """
        visitor = await self.get_visitor_for_internal_user(user)
        if not visitor:
            return False

        visitor.internal_user_id = None
        await self.db.flush()
        return True

    async def sync_internal_user_changes(
        self,
        user: User,
    ) -> Optional[SiteVisitor]:
        """Sync internal user changes to linked visitor.

        Call this when internal user profile is updated to keep
        visitor record in sync (e.g., email change, display name).
        """
        visitor = await self.get_visitor_for_internal_user(user)
        if not visitor:
            return None

        # Update synchronized fields
        visitor.email = user.email.lower()
        visitor.display_name = user.display_name

        await self.db.flush()
        return visitor

    async def migrate_external_to_internal(
        self,
        visitor: SiteVisitor,
        user: User,
    ) -> SiteVisitor:
        """Migrate an external visitor to internal user.

        Use when an external visitor becomes an internal user.
        Links their existing visitor record to the new internal user.
        """
        # Check if user already has a visitor
        existing = await self.get_visitor_for_internal_user(user)
        if existing and existing.id != visitor.id:
            # Merge roles from old visitor to existing
            await self._merge_visitor_roles(visitor, existing)
            return existing

        # Link visitor to internal user
        visitor.internal_user_id = user.id
        visitor.display_name = user.display_name
        visitor.email = user.email.lower()

        await self.db.flush()
        return visitor

    async def _merge_visitor_roles(
        self,
        from_visitor: SiteVisitor,
        to_visitor: SiteVisitor,
    ) -> None:
        """Merge roles from one visitor to another.

        Used when consolidating visitor records (e.g., external becomes internal).
        """
        result = await self.db.execute(
            select(SiteVisitorRole).where(
                and_(
                    SiteVisitorRole.visitor_id == from_visitor.id,
                    SiteVisitorRole.is_active == True,
                )
            )
        )
        old_roles = result.scalars().all()

        for old_role in old_roles:
            # Check if target already has role for this site
            result = await self.db.execute(
                select(SiteVisitorRole).where(
                    and_(
                        SiteVisitorRole.visitor_id == to_visitor.id,
                        SiteVisitorRole.site_id == old_role.site_id,
                    )
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Keep higher clearance level
                if old_role.clearance_level > existing.clearance_level:
                    existing.clearance_level = old_role.clearance_level
                # Merge allowed pages
                merged_pages = list(set(
                    existing.allowed_page_ids + old_role.allowed_page_ids
                ))
                existing.allowed_page_ids = merged_pages
            else:
                # Create new role for target visitor
                new_role = SiteVisitorRole(
                    id=str(uuid4()),
                    visitor_id=to_visitor.id,
                    site_id=old_role.site_id,
                    clearance_level=old_role.clearance_level,
                    allowed_page_ids=old_role.allowed_page_ids,
                    expires_at=old_role.expires_at,
                    assigned_by_id=old_role.assigned_by_id,
                    is_active=True,
                    created_at=datetime.utcnow(),
                )
                self.db.add(new_role)

            # Deactivate old role
            old_role.is_active = False

        await self.db.flush()


# Convenience function for dependency injection
async def get_sso_bridge(db: AsyncSession) -> SSOBridge:
    """Get SSO bridge instance."""
    return SSOBridge(db)
