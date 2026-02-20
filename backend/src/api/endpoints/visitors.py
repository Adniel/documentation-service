"""Visitor management API endpoints.

Sprint D: Integrated Access Control

Endpoints for managing external visitors to published sites:
- Invite visitors by email
- Manage visitor roles and clearance levels
- Magic link authentication
- Visitor session management
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.db.models import User
from src.db.models.published_site import PublishedSite
from src.modules.publishing import (
    PublishingService,
    VisitorService,
    get_visitor_service,
)

router = APIRouter(prefix="/visitors", tags=["visitors"])


# Request/Response models

class VisitorInvite(BaseModel):
    """Request to invite a visitor to a site."""

    email: EmailStr
    display_name: Optional[str] = None
    clearance_level: int = Field(default=0, ge=0, le=3)
    allowed_page_ids: list[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None


class BulkVisitorInvite(BaseModel):
    """Request to invite multiple visitors."""

    emails: list[EmailStr]
    clearance_level: int = Field(default=0, ge=0, le=3)
    expires_at: Optional[datetime] = None


class VisitorRoleUpdate(BaseModel):
    """Request to update visitor role."""

    clearance_level: int = Field(ge=0, le=3)
    allowed_page_ids: list[str] = Field(default_factory=list)
    expires_at: Optional[datetime] = None


class VisitorResponse(BaseModel):
    """Visitor information response."""

    id: str
    email: str
    display_name: str
    is_internal: bool
    last_login_at: Optional[datetime]
    created_at: datetime


class VisitorRoleResponse(BaseModel):
    """Visitor role information."""

    visitor_id: str
    site_id: str
    clearance_level: int
    allowed_page_ids: list[str]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime


class VisitorWithRoleResponse(BaseModel):
    """Visitor with their site role."""

    visitor: VisitorResponse
    role: VisitorRoleResponse


class InviteResultResponse(BaseModel):
    """Result of visitor invitation."""

    visitor: VisitorResponse
    magic_link_url: str
    expires_at: datetime


# Helper functions

async def get_site_with_access_check(
    site_id: str,
    db: AsyncSession,
    current_user: User,
) -> PublishedSite:
    """Get site and verify user has admin access."""
    publishing_service = PublishingService(db)
    site = await publishing_service.get_site(site_id)

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )

    # Check if user has admin access to this site
    # For now, require owner or admin role
    # This can be enhanced with more granular permission checks
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return site


# Endpoints

@router.get("/sites/{site_id}")
async def list_site_visitors(
    site_id: str,
    active_only: bool = Query(True, description="Only return active visitors"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VisitorWithRoleResponse]:
    """List all visitors for a site."""
    site = await get_site_with_access_check(site_id, db, current_user)
    visitor_service = await get_visitor_service(db)

    visitors_with_roles = await visitor_service.get_site_visitors(site, active_only)

    return [
        VisitorWithRoleResponse(
            visitor=VisitorResponse(
                id=visitor.id,
                email=visitor.email,
                display_name=visitor.display_name,
                is_internal=visitor.internal_user_id is not None,
                last_login_at=visitor.last_login_at,
                created_at=visitor.created_at,
            ),
            role=VisitorRoleResponse(
                visitor_id=role.visitor_id,
                site_id=role.site_id,
                clearance_level=role.clearance_level,
                allowed_page_ids=role.allowed_page_ids or [],
                expires_at=role.expires_at,
                is_active=role.is_active,
                created_at=role.created_at,
            ),
        )
        for visitor, role in visitors_with_roles
    ]


@router.post("/sites/{site_id}/invite")
async def invite_visitor(
    site_id: str,
    invite: VisitorInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InviteResultResponse:
    """Invite a single visitor to a site."""
    site = await get_site_with_access_check(site_id, db, current_user)

    # Get base URL from site or config
    from src.config import settings
    base_url = getattr(settings, "PUBLIC_SITE_URL", "")

    visitor_service = VisitorService(db, base_url)

    # Create or get visitor
    visitor, _ = await visitor_service.get_or_create_visitor(
        email=invite.email,
        display_name=invite.display_name,
    )

    # Assign role
    await visitor_service.assign_role(
        visitor=visitor,
        site=site,
        clearance_level=invite.clearance_level,
        allowed_page_ids=invite.allowed_page_ids,
        expires_at=invite.expires_at,
        assigned_by_id=current_user.id,
    )

    # Generate magic link
    magic_link = await visitor_service.generate_magic_link(
        email=invite.email,
        site=site,
    )

    await db.commit()

    return InviteResultResponse(
        visitor=VisitorResponse(
            id=visitor.id,
            email=visitor.email,
            display_name=visitor.display_name,
            is_internal=visitor.internal_user_id is not None,
            last_login_at=visitor.last_login_at,
            created_at=visitor.created_at,
        ),
        magic_link_url=magic_link.login_url,
        expires_at=magic_link.expires_at,
    )


@router.post("/sites/{site_id}/invite/bulk")
async def bulk_invite_visitors(
    site_id: str,
    invite: BulkVisitorInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InviteResultResponse]:
    """Invite multiple visitors to a site."""
    site = await get_site_with_access_check(site_id, db, current_user)

    from src.config import settings
    base_url = getattr(settings, "PUBLIC_SITE_URL", "")

    visitor_service = VisitorService(db, base_url)

    results = await visitor_service.invite_visitors(
        site=site,
        emails=invite.emails,
        clearance_level=invite.clearance_level,
        expires_at=invite.expires_at,
        assigned_by_id=current_user.id,
    )

    await db.commit()

    return [
        InviteResultResponse(
            visitor=VisitorResponse(
                id=visitor.id,
                email=visitor.email,
                display_name=visitor.display_name,
                is_internal=visitor.internal_user_id is not None,
                last_login_at=visitor.last_login_at,
                created_at=visitor.created_at,
            ),
            magic_link_url=magic_link.login_url,
            expires_at=magic_link.expires_at,
        )
        for visitor, magic_link in results
    ]


@router.put("/sites/{site_id}/visitors/{visitor_id}/role")
async def update_visitor_role(
    site_id: str,
    visitor_id: str,
    role_update: VisitorRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VisitorRoleResponse:
    """Update a visitor's role on a site."""
    site = await get_site_with_access_check(site_id, db, current_user)
    visitor_service = await get_visitor_service(db)

    visitor = await visitor_service.get_visitor_by_id(visitor_id)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitor not found",
        )

    role = await visitor_service.assign_role(
        visitor=visitor,
        site=site,
        clearance_level=role_update.clearance_level,
        allowed_page_ids=role_update.allowed_page_ids,
        expires_at=role_update.expires_at,
        assigned_by_id=current_user.id,
    )

    await db.commit()

    return VisitorRoleResponse(
        visitor_id=role.visitor_id,
        site_id=role.site_id,
        clearance_level=role.clearance_level,
        allowed_page_ids=role.allowed_page_ids or [],
        expires_at=role.expires_at,
        is_active=role.is_active,
        created_at=role.created_at,
    )


@router.delete("/sites/{site_id}/visitors/{visitor_id}")
async def revoke_visitor_access(
    site_id: str,
    visitor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Revoke a visitor's access to a site."""
    site = await get_site_with_access_check(site_id, db, current_user)
    visitor_service = await get_visitor_service(db)

    visitor = await visitor_service.get_visitor_by_id(visitor_id)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitor not found",
        )

    revoked = await visitor_service.revoke_role(visitor, site)

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitor role not found",
        )

    await db.commit()

    return {"status": "revoked", "visitor_id": visitor_id, "site_id": site_id}


@router.post("/sites/{site_id}/visitors/{visitor_id}/resend-invite")
async def resend_visitor_invite(
    site_id: str,
    visitor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InviteResultResponse:
    """Resend invitation to a visitor."""
    site = await get_site_with_access_check(site_id, db, current_user)

    from src.config import settings
    base_url = getattr(settings, "PUBLIC_SITE_URL", "")

    visitor_service = VisitorService(db, base_url)

    visitor = await visitor_service.get_visitor_by_id(visitor_id)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visitor not found",
        )

    # Generate new magic link
    magic_link = await visitor_service.generate_magic_link(
        email=visitor.email,
        site=site,
    )

    await db.commit()

    return InviteResultResponse(
        visitor=VisitorResponse(
            id=visitor.id,
            email=visitor.email,
            display_name=visitor.display_name,
            is_internal=visitor.internal_user_id is not None,
            last_login_at=visitor.last_login_at,
            created_at=visitor.created_at,
        ),
        magic_link_url=magic_link.login_url,
        expires_at=magic_link.expires_at,
    )


# Authentication endpoints for visitor login

@router.post("/auth/verify")
async def verify_magic_link(
    token: str = Query(..., description="Magic link token"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Verify magic link and create session.

    Returns session token for subsequent requests.
    """
    visitor_service = await get_visitor_service(db)

    visitor = await visitor_service.verify_magic_link(token)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired magic link",
        )

    await db.commit()

    return {
        "visitor_id": visitor.id,
        "session_token": visitor.session_token,
        "expires_at": visitor.session_expires_at.isoformat(),
        "email": visitor.email,
        "display_name": visitor.display_name,
    }


@router.post("/auth/logout")
async def visitor_logout(
    session_token: str = Query(..., description="Session token"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """End visitor session."""
    visitor_service = await get_visitor_service(db)

    visitor = await visitor_service.get_visitor_by_token(session_token)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )

    await visitor_service.end_session(visitor)
    await db.commit()

    return {"status": "logged_out"}


@router.get("/auth/me")
async def get_current_visitor(
    session_token: str = Query(..., description="Session token"),
    db: AsyncSession = Depends(get_db),
) -> VisitorResponse:
    """Get current visitor information from session token."""
    visitor_service = await get_visitor_service(db)

    visitor = await visitor_service.get_visitor_by_token(session_token)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    return VisitorResponse(
        id=visitor.id,
        email=visitor.email,
        display_name=visitor.display_name,
        is_internal=visitor.internal_user_id is not None,
        last_login_at=visitor.last_login_at,
        created_at=visitor.created_at,
    )
