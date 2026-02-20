"""Visitor management service for published sites.

Sprint D: Integrated Access Control

Manages external visitors to published sites:
- Email-based authentication with magic links
- Role assignment with clearance levels
- Visitor sessions and token management
"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.site_visitor import SiteVisitor
from src.db.models.site_visitor_role import SiteVisitorRole
from src.db.models.published_site import PublishedSite
from src.db.models.user import User


@dataclass
class MagicLinkResult:
    """Result of magic link generation."""

    token: str
    expires_at: datetime
    login_url: str


@dataclass
class VisitorSession:
    """Active visitor session."""

    visitor_id: str
    site_id: str
    clearance_level: int
    expires_at: datetime
    token: str


class VisitorService:
    """Service for managing site visitors."""

    # Magic link validity period
    MAGIC_LINK_EXPIRY_MINUTES = 30

    # Session token validity
    SESSION_EXPIRY_HOURS = 24

    def __init__(self, db: AsyncSession, base_url: str = ""):
        self.db = db
        self.base_url = base_url

    async def get_visitor_by_email(self, email: str) -> Optional[SiteVisitor]:
        """Get visitor by email address."""
        result = await self.db.execute(
            select(SiteVisitor).where(SiteVisitor.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_visitor_by_id(self, visitor_id: str) -> Optional[SiteVisitor]:
        """Get visitor by ID."""
        result = await self.db.execute(
            select(SiteVisitor).where(SiteVisitor.id == visitor_id)
        )
        return result.scalar_one_or_none()

    async def get_visitor_by_token(self, token: str) -> Optional[SiteVisitor]:
        """Get visitor by session token (validates expiration)."""
        result = await self.db.execute(
            select(SiteVisitor).where(
                and_(
                    SiteVisitor.session_token == token,
                    SiteVisitor.session_expires_at > datetime.utcnow(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_visitor(
        self,
        email: str,
        display_name: Optional[str] = None,
    ) -> SiteVisitor:
        """Create a new site visitor."""
        visitor = SiteVisitor(
            id=str(uuid4()),
            email=email.lower(),
            display_name=display_name or email.split("@")[0],
            created_at=datetime.utcnow(),
        )
        self.db.add(visitor)
        await self.db.flush()
        return visitor

    async def get_or_create_visitor(
        self,
        email: str,
        display_name: Optional[str] = None,
    ) -> tuple[SiteVisitor, bool]:
        """Get existing visitor or create new one.

        Returns (visitor, created) tuple.
        """
        visitor = await self.get_visitor_by_email(email)
        if visitor:
            return visitor, False

        visitor = await self.create_visitor(email, display_name)
        return visitor, True

    async def generate_magic_link(
        self,
        email: str,
        site: PublishedSite,
        display_name: Optional[str] = None,
    ) -> MagicLinkResult:
        """Generate magic link for visitor authentication.

        Creates visitor if needed, generates one-time token.
        """
        visitor, _ = await self.get_or_create_visitor(email, display_name)

        # Generate magic link token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=self.MAGIC_LINK_EXPIRY_MINUTES)

        # Store token on visitor
        visitor.magic_link_token = token
        visitor.magic_link_expires_at = expires_at

        await self.db.flush()

        # Build login URL
        login_url = f"{self.base_url}/sites/{site.slug}/auth/verify?token={token}"

        return MagicLinkResult(
            token=token,
            expires_at=expires_at,
            login_url=login_url,
        )

    async def verify_magic_link(self, token: str) -> Optional[SiteVisitor]:
        """Verify magic link token and establish session.

        Returns visitor if token is valid, None otherwise.
        Clears magic link token after successful verification.
        """
        result = await self.db.execute(
            select(SiteVisitor).where(
                and_(
                    SiteVisitor.magic_link_token == token,
                    SiteVisitor.magic_link_expires_at > datetime.utcnow(),
                )
            )
        )
        visitor = result.scalar_one_or_none()

        if not visitor:
            return None

        # Clear magic link (one-time use)
        visitor.magic_link_token = None
        visitor.magic_link_expires_at = None

        # Update last login
        visitor.last_login_at = datetime.utcnow()

        # Create session token
        visitor.session_token = secrets.token_urlsafe(32)
        visitor.session_expires_at = datetime.utcnow() + timedelta(
            hours=self.SESSION_EXPIRY_HOURS
        )

        await self.db.flush()
        return visitor

    async def create_session(self, visitor: SiteVisitor) -> VisitorSession:
        """Create or refresh session for visitor."""
        visitor.session_token = secrets.token_urlsafe(32)
        visitor.session_expires_at = datetime.utcnow() + timedelta(
            hours=self.SESSION_EXPIRY_HOURS
        )
        visitor.last_login_at = datetime.utcnow()

        await self.db.flush()

        # Get visitor's highest clearance for any site
        result = await self.db.execute(
            select(SiteVisitorRole).where(
                and_(
                    SiteVisitorRole.visitor_id == visitor.id,
                    SiteVisitorRole.is_active == True,
                )
            )
        )
        roles = result.scalars().all()
        max_clearance = max((r.clearance_level for r in roles), default=0)

        return VisitorSession(
            visitor_id=visitor.id,
            site_id="",  # Will be set per-site
            clearance_level=max_clearance,
            expires_at=visitor.session_expires_at,
            token=visitor.session_token,
        )

    async def end_session(self, visitor: SiteVisitor) -> None:
        """End visitor session (logout)."""
        visitor.session_token = None
        visitor.session_expires_at = None
        await self.db.flush()

    # Role management

    async def assign_role(
        self,
        visitor: SiteVisitor,
        site: PublishedSite,
        clearance_level: int = 0,
        allowed_page_ids: Optional[list[str]] = None,
        expires_at: Optional[datetime] = None,
        assigned_by_id: Optional[str] = None,
    ) -> SiteVisitorRole:
        """Assign or update role for visitor on a site."""
        # Check for existing role
        result = await self.db.execute(
            select(SiteVisitorRole).where(
                and_(
                    SiteVisitorRole.visitor_id == visitor.id,
                    SiteVisitorRole.site_id == site.id,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing role
            existing.clearance_level = clearance_level
            existing.allowed_page_ids = allowed_page_ids or []
            existing.expires_at = expires_at
            existing.assigned_by_id = assigned_by_id
            existing.is_active = True
            await self.db.flush()
            return existing

        # Create new role
        role = SiteVisitorRole(
            id=str(uuid4()),
            visitor_id=visitor.id,
            site_id=site.id,
            clearance_level=clearance_level,
            allowed_page_ids=allowed_page_ids or [],
            expires_at=expires_at,
            assigned_by_id=assigned_by_id,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(role)
        await self.db.flush()
        return role

    async def revoke_role(
        self,
        visitor: SiteVisitor,
        site: PublishedSite,
    ) -> bool:
        """Revoke visitor's role for a site.

        Returns True if role existed and was revoked.
        """
        result = await self.db.execute(
            select(SiteVisitorRole).where(
                and_(
                    SiteVisitorRole.visitor_id == visitor.id,
                    SiteVisitorRole.site_id == site.id,
                )
            )
        )
        role = result.scalar_one_or_none()

        if not role:
            return False

        role.is_active = False
        await self.db.flush()
        return True

    async def get_visitor_role(
        self,
        visitor: SiteVisitor,
        site: PublishedSite,
    ) -> Optional[SiteVisitorRole]:
        """Get visitor's role for a specific site."""
        result = await self.db.execute(
            select(SiteVisitorRole).where(
                and_(
                    SiteVisitorRole.visitor_id == visitor.id,
                    SiteVisitorRole.site_id == site.id,
                    SiteVisitorRole.is_active == True,
                )
            )
        )
        role = result.scalar_one_or_none()

        # Check if expired
        if role and not role.is_valid():
            return None

        return role

    async def get_site_visitors(
        self,
        site: PublishedSite,
        active_only: bool = True,
    ) -> list[tuple[SiteVisitor, SiteVisitorRole]]:
        """Get all visitors for a site with their roles."""
        query = (
            select(SiteVisitor, SiteVisitorRole)
            .join(SiteVisitorRole, SiteVisitor.id == SiteVisitorRole.visitor_id)
            .where(SiteVisitorRole.site_id == site.id)
        )

        if active_only:
            query = query.where(SiteVisitorRole.is_active == True)

        result = await self.db.execute(query)
        return [(row[0], row[1]) for row in result.all()]

    async def get_visitor_sites(
        self,
        visitor: SiteVisitor,
    ) -> list[tuple[PublishedSite, SiteVisitorRole]]:
        """Get all sites a visitor has access to."""
        result = await self.db.execute(
            select(PublishedSite, SiteVisitorRole)
            .join(SiteVisitorRole, PublishedSite.id == SiteVisitorRole.site_id)
            .where(
                and_(
                    SiteVisitorRole.visitor_id == visitor.id,
                    SiteVisitorRole.is_active == True,
                )
            )
        )
        return [(row[0], row[1]) for row in result.all()]

    # Bulk operations

    async def invite_visitors(
        self,
        site: PublishedSite,
        emails: list[str],
        clearance_level: int = 0,
        expires_at: Optional[datetime] = None,
        assigned_by_id: Optional[str] = None,
    ) -> list[tuple[SiteVisitor, MagicLinkResult]]:
        """Invite multiple visitors to a site.

        Creates visitors as needed, assigns roles, generates magic links.
        """
        results = []

        for email in emails:
            visitor, _ = await self.get_or_create_visitor(email)
            await self.assign_role(
                visitor=visitor,
                site=site,
                clearance_level=clearance_level,
                expires_at=expires_at,
                assigned_by_id=assigned_by_id,
            )
            magic_link = await self.generate_magic_link(email, site)
            results.append((visitor, magic_link))

        return results

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions.

        Returns count of sessions cleaned up.
        """
        result = await self.db.execute(
            select(SiteVisitor).where(
                and_(
                    SiteVisitor.session_expires_at.isnot(None),
                    SiteVisitor.session_expires_at < datetime.utcnow(),
                )
            )
        )
        expired = result.scalars().all()

        count = 0
        for visitor in expired:
            visitor.session_token = None
            visitor.session_expires_at = None
            count += 1

        await self.db.flush()
        return count


# Convenience function for dependency injection
async def get_visitor_service(
    db: AsyncSession,
    base_url: str = "",
) -> VisitorService:
    """Get visitor service instance."""
    return VisitorService(db, base_url)
