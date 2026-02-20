"""Access service for published sites.

Sprint D: Integrated Access Control

Checks access to documents on published sites using layered access model:
1. Site visibility (first gate) - who can reach the site
2. Document classification + ACLs (second gate) - what they can see

Principle: Most restrictive wins - both classification AND ACLs must grant access.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.page import Page
from src.db.models.published_site import PublishedSite, SiteVisibility
from src.db.models.site_visitor import SiteVisitor
from src.db.models.site_visitor_role import SiteVisitorRole
from src.db.models.user import User
from src.db.models.permission import Permission, Role
from src.modules.access.classification_service import ClassificationService


@dataclass
class AccessResult:
    """Result of an access check."""

    allowed: bool
    reason: str
    show_placeholder: bool = False

    @property
    def denied(self) -> bool:
        return not self.allowed


class PublishedSiteAccessService:
    """Service for checking access to content on published sites."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.classification_service = ClassificationService(db)

    async def get_visitor_role(
        self,
        visitor_id: str,
        site_id: str,
    ) -> Optional[SiteVisitorRole]:
        """Get visitor's role for a specific site."""
        result = await self.db.execute(
            select(SiteVisitorRole).where(
                and_(
                    SiteVisitorRole.visitor_id == visitor_id,
                    SiteVisitorRole.site_id == site_id,
                )
            )
        )
        role = result.scalar_one_or_none()

        # Check if role is still valid
        if role and not role.is_valid():
            return None

        return role

    def get_visitor_clearance(
        self,
        site: PublishedSite,
        visitor: Optional[SiteVisitor],
        internal_user: Optional[User],
        visitor_role: Optional[SiteVisitorRole],
    ) -> int:
        """Get effective clearance level for a site visitor.

        Resolution order:
        1. Internal user (via SSO) - use their clearance_level
        2. External visitor with role - use role's clearance_level
        3. Anonymous or visitor without role - clearance 0 (public only)
        """
        # Anonymous visitor
        if not visitor and not internal_user:
            return 0

        # Internal user via SSO
        if internal_user:
            return internal_user.clearance_level

        # External visitor with role assignment
        if visitor_role:
            return visitor_role.clearance_level

        # External visitor without role (default to public only)
        return 0

    async def check_site_visibility(
        self,
        site: PublishedSite,
        visitor: Optional[SiteVisitor],
        internal_user: Optional[User],
    ) -> AccessResult:
        """Check if visitor can access the site at all (first gate).

        Site visibility levels:
        - PUBLIC: Anyone can access
        - AUTHENTICATED: Must be logged in (visitor or internal user)
        - RESTRICTED: Must be from allowed email domains
        """
        # Public sites are accessible to everyone
        if site.visibility == SiteVisibility.PUBLIC.value:
            return AccessResult(allowed=True, reason="Public site")

        # Need some form of authentication for non-public sites
        has_identity = visitor is not None or internal_user is not None

        if site.visibility == SiteVisibility.AUTHENTICATED.value:
            if has_identity:
                return AccessResult(allowed=True, reason="Authenticated user")
            return AccessResult(
                allowed=False,
                reason="Authentication required",
                show_placeholder=False,
            )

        if site.visibility == SiteVisibility.RESTRICTED.value:
            if not has_identity:
                return AccessResult(
                    allowed=False,
                    reason="Authentication required",
                    show_placeholder=False,
                )

            # Check email domain
            email = None
            if internal_user:
                email = internal_user.email
            elif visitor:
                email = visitor.email

            if not email:
                return AccessResult(
                    allowed=False,
                    reason="Email required for restricted site",
                    show_placeholder=False,
                )

            # Check against allowed domains
            if not site.allowed_email_domains:
                # No domains configured = no one allowed (except maybe internal)
                if internal_user:
                    return AccessResult(allowed=True, reason="Internal user access")
                return AccessResult(
                    allowed=False,
                    reason="No allowed email domains configured",
                    show_placeholder=False,
                )

            domain = email.split("@")[-1].lower() if "@" in email else ""
            allowed_domains = [d.lower() for d in site.allowed_email_domains]

            if domain in allowed_domains:
                return AccessResult(allowed=True, reason=f"Email domain {domain} allowed")

            return AccessResult(
                allowed=False,
                reason=f"Email domain {domain} not in allowed list",
                show_placeholder=False,
            )

        # Unknown visibility - deny
        return AccessResult(
            allowed=False,
            reason=f"Unknown visibility: {site.visibility}",
            show_placeholder=False,
        )

    async def check_page_classification(
        self,
        page: Page,
        clearance: int,
    ) -> AccessResult:
        """Check if clearance level allows access to page classification."""
        page_classification = await self.classification_service.get_effective_classification(page)

        if clearance >= page_classification:
            return AccessResult(
                allowed=True,
                reason=f"Clearance {clearance} >= classification {page_classification}",
            )

        return AccessResult(
            allowed=False,
            reason=f"Clearance {clearance} < classification {page_classification}",
            show_placeholder=True,  # May show placeholder based on settings
        )

    async def check_page_acls(
        self,
        page: Page,
        visitor: Optional[SiteVisitor],
        internal_user: Optional[User],
        visitor_role: Optional[SiteVisitorRole],
    ) -> AccessResult:
        """Check if visitor passes ACL restrictions.

        ACLs are checked at page and space level.
        If no ACLs exist, access is allowed (classification already checked).
        If ACLs exist, visitor must be in at least one.
        """
        # Check for explicit page access in visitor role
        if visitor_role and visitor_role.has_explicit_access(page.id):
            return AccessResult(allowed=True, reason="Explicit page access granted")

        # For internal users, check normal permission system
        if internal_user:
            # Check if there are any page-level permissions
            result = await self.db.execute(
                select(Permission).where(
                    and_(
                        Permission.resource_type == "page",
                        Permission.resource_id == page.id,
                        Permission.is_active == True,
                    )
                ).limit(1)
            )
            page_permissions = result.scalar_one_or_none()

            if page_permissions:
                # There are page-level permissions, check if user has one
                result = await self.db.execute(
                    select(Permission).where(
                        and_(
                            Permission.resource_type == "page",
                            Permission.resource_id == page.id,
                            Permission.user_id == internal_user.id,
                            Permission.is_active == True,
                        )
                    )
                )
                user_permission = result.scalar_one_or_none()
                if not user_permission:
                    return AccessResult(
                        allowed=False,
                        reason="Page has ACL restrictions, user not in list",
                        show_placeholder=True,
                    )

            # Check space-level permissions
            result = await self.db.execute(
                select(Permission).where(
                    and_(
                        Permission.resource_type == "space",
                        Permission.resource_id == page.space_id,
                        Permission.is_active == True,
                    )
                ).limit(1)
            )
            space_permissions = result.scalar_one_or_none()

            if space_permissions:
                # There are space-level permissions, check if user has one
                result = await self.db.execute(
                    select(Permission).where(
                        and_(
                            Permission.resource_type == "space",
                            Permission.resource_id == page.space_id,
                            Permission.user_id == internal_user.id,
                            Permission.is_active == True,
                        )
                    )
                )
                user_permission = result.scalar_one_or_none()
                if not user_permission:
                    return AccessResult(
                        allowed=False,
                        reason="Space has ACL restrictions, user not in list",
                        show_placeholder=True,
                    )

        # External visitors don't have ACL entries (they use visitor roles)
        # If we got here, no ACL restrictions apply
        return AccessResult(allowed=True, reason="No ACL restrictions or user is allowed")

    def should_show_placeholder(
        self,
        site: PublishedSite,
        page: Page,
    ) -> bool:
        """Determine if a restricted page should show a placeholder.

        Resolution:
        1. Page-level override (show_when_restricted) takes precedence
        2. Fall back to site-level setting (show_restricted_as_placeholder)
        """
        # Page-level override
        if page.show_when_restricted is not None:
            return page.show_when_restricted

        # Site-level default
        return site.show_restricted_as_placeholder

    async def can_access_page(
        self,
        site: PublishedSite,
        page: Page,
        visitor: Optional[SiteVisitor],
        internal_user: Optional[User],
    ) -> AccessResult:
        """Check if visitor can access a page on a published site.

        This is the main access check method combining all gates:
        1. Site visibility (first gate)
        2. Classification check
        3. ACL check

        All checks must pass for access to be granted.
        """
        # Get visitor's role for this site
        visitor_role = None
        if visitor:
            visitor_role = await self.get_visitor_role(visitor.id, site.id)

        # Gate 1: Site visibility
        visibility_result = await self.check_site_visibility(site, visitor, internal_user)
        if not visibility_result.allowed:
            return visibility_result

        # Gate 2: Classification
        clearance = self.get_visitor_clearance(site, visitor, internal_user, visitor_role)
        classification_result = await self.check_page_classification(page, clearance)
        if not classification_result.allowed:
            # Determine if we should show placeholder
            show_placeholder = self.should_show_placeholder(site, page)
            return AccessResult(
                allowed=False,
                reason=classification_result.reason,
                show_placeholder=show_placeholder,
            )

        # Gate 3: ACLs
        acl_result = await self.check_page_acls(page, visitor, internal_user, visitor_role)
        if not acl_result.allowed:
            show_placeholder = self.should_show_placeholder(site, page)
            return AccessResult(
                allowed=False,
                reason=acl_result.reason,
                show_placeholder=show_placeholder,
            )

        return AccessResult(allowed=True, reason="Access granted")

    async def filter_accessible_pages(
        self,
        site: PublishedSite,
        pages: list[Page],
        visitor: Optional[SiteVisitor],
        internal_user: Optional[User],
    ) -> tuple[list[Page], list[tuple[Page, str]]]:
        """Filter a list of pages to only those the visitor can access.

        Returns:
            Tuple of (accessible_pages, placeholder_pages)
            where placeholder_pages is list of (page, message) tuples
            for pages that should show as placeholders.
        """
        accessible = []
        placeholders = []

        for page in pages:
            result = await self.can_access_page(site, page, visitor, internal_user)

            if result.allowed:
                accessible.append(page)
            elif result.show_placeholder:
                message = site.restricted_placeholder_message or "Access Restricted"
                placeholders.append((page, message))
            # else: completely hidden

        return accessible, placeholders


# Convenience function for dependency injection
async def get_published_site_access_service(db: AsyncSession) -> PublishedSiteAccessService:
    """Get published site access service instance."""
    return PublishedSiteAccessService(db)
