"""Integration tests for visitor management API.

Sprint D: Integrated Access Control
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from httpx import AsyncClient

from src.db.models.published_site import PublishedSite, SiteStatus, SiteVisibility
from src.db.models.site_visitor import SiteVisitor
from src.db.models.site_visitor_role import SiteVisitorRole


class TestVisitorManagementAPI:
    """Test visitor management endpoints."""

    @pytest.fixture
    async def published_site(self, db_session, test_organization, test_space):
        """Create a published site for testing."""
        site = PublishedSite(
            id=str(uuid4()),
            organization_id=test_organization.id,
            space_id=test_space.id,
            slug=f"test-site-{uuid4().hex[:8]}",
            site_title="Test Site",
            visibility=SiteVisibility.AUTHENTICATED.value,
            status=SiteStatus.PUBLISHED.value,
            show_restricted_as_placeholder=True,
        )
        db_session.add(site)
        await db_session.commit()
        await db_session.refresh(site)
        return site

    @pytest.fixture
    async def test_visitor(self, db_session):
        """Create a test visitor."""
        visitor = SiteVisitor(
            id=str(uuid4()),
            email="testvisitor@example.com",
            display_name="Test Visitor",
            created_at=datetime.utcnow(),
        )
        db_session.add(visitor)
        await db_session.commit()
        await db_session.refresh(visitor)
        return visitor

    @pytest.mark.asyncio
    async def test_list_site_visitors_empty(
        self, async_client: AsyncClient, auth_headers, published_site
    ):
        """List visitors returns empty list for new site."""
        response = await async_client.get(
            f"/api/v1/visitors/sites/{published_site.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_invite_visitor(
        self, async_client: AsyncClient, auth_headers, published_site
    ):
        """Invite a new visitor to a site."""
        response = await async_client.post(
            f"/api/v1/visitors/sites/{published_site.id}/invite",
            headers=auth_headers,
            json={
                "email": "newvisitor@example.com",
                "display_name": "New Visitor",
                "clearance_level": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["visitor"]["email"] == "newvisitor@example.com"
        assert data["visitor"]["display_name"] == "New Visitor"
        assert "magic_link_url" in data
        assert "expires_at" in data

    @pytest.mark.asyncio
    async def test_invite_visitor_with_expiry(
        self, async_client: AsyncClient, auth_headers, published_site
    ):
        """Invite visitor with expiration date."""
        expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()
        response = await async_client.post(
            f"/api/v1/visitors/sites/{published_site.id}/invite",
            headers=auth_headers,
            json={
                "email": "tempvisitor@example.com",
                "clearance_level": 0,
                "expires_at": expiry,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["visitor"]["email"] == "tempvisitor@example.com"

    @pytest.mark.asyncio
    async def test_bulk_invite_visitors(
        self, async_client: AsyncClient, auth_headers, published_site
    ):
        """Bulk invite multiple visitors."""
        response = await async_client.post(
            f"/api/v1/visitors/sites/{published_site.id}/invite/bulk",
            headers=auth_headers,
            json={
                "emails": [
                    "bulk1@example.com",
                    "bulk2@example.com",
                    "bulk3@example.com",
                ],
                "clearance_level": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        emails = [r["visitor"]["email"] for r in data]
        assert "bulk1@example.com" in emails
        assert "bulk2@example.com" in emails
        assert "bulk3@example.com" in emails

    @pytest.mark.asyncio
    async def test_list_site_visitors_after_invite(
        self,
        async_client: AsyncClient,
        auth_headers,
        published_site,
        db_session,
        test_visitor,
    ):
        """List visitors shows invited visitors."""
        # Create role for visitor
        role = SiteVisitorRole(
            id=str(uuid4()),
            visitor_id=test_visitor.id,
            site_id=published_site.id,
            clearance_level=1,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db_session.add(role)
        await db_session.commit()

        response = await async_client.get(
            f"/api/v1/visitors/sites/{published_site.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["visitor"]["email"] == test_visitor.email
        assert data[0]["role"]["clearance_level"] == 1

    @pytest.mark.asyncio
    async def test_update_visitor_role(
        self,
        async_client: AsyncClient,
        auth_headers,
        published_site,
        db_session,
        test_visitor,
    ):
        """Update visitor's role and clearance level."""
        # Create initial role
        role = SiteVisitorRole(
            id=str(uuid4()),
            visitor_id=test_visitor.id,
            site_id=published_site.id,
            clearance_level=0,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db_session.add(role)
        await db_session.commit()

        response = await async_client.put(
            f"/api/v1/visitors/sites/{published_site.id}/visitors/{test_visitor.id}/role",
            headers=auth_headers,
            json={
                "clearance_level": 2,
                "allowed_page_ids": [],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["clearance_level"] == 2

    @pytest.mark.asyncio
    async def test_revoke_visitor_access(
        self,
        async_client: AsyncClient,
        auth_headers,
        published_site,
        db_session,
        test_visitor,
    ):
        """Revoke visitor's access to site."""
        # Create role
        role = SiteVisitorRole(
            id=str(uuid4()),
            visitor_id=test_visitor.id,
            site_id=published_site.id,
            clearance_level=1,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db_session.add(role)
        await db_session.commit()

        response = await async_client.delete(
            f"/api/v1/visitors/sites/{published_site.id}/visitors/{test_visitor.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "revoked"

    @pytest.mark.asyncio
    async def test_revoke_nonexistent_visitor(
        self, async_client: AsyncClient, auth_headers, published_site
    ):
        """Revoke access for non-existent visitor returns 404."""
        response = await async_client.delete(
            f"/api/v1/visitors/sites/{published_site.id}/visitors/{uuid4()}",
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_resend_invite(
        self,
        async_client: AsyncClient,
        auth_headers,
        published_site,
        db_session,
        test_visitor,
    ):
        """Resend invitation to existing visitor."""
        # Create role
        role = SiteVisitorRole(
            id=str(uuid4()),
            visitor_id=test_visitor.id,
            site_id=published_site.id,
            clearance_level=1,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db_session.add(role)
        await db_session.commit()

        response = await async_client.post(
            f"/api/v1/visitors/sites/{published_site.id}/visitors/{test_visitor.id}/resend-invite",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "magic_link_url" in data
        assert data["visitor"]["id"] == test_visitor.id


class TestVisitorAuthenticationAPI:
    """Test visitor authentication endpoints."""

    @pytest.fixture
    async def visitor_with_magic_link(self, db_session):
        """Create visitor with valid magic link."""
        import secrets

        token = secrets.token_urlsafe(32)
        visitor = SiteVisitor(
            id=str(uuid4()),
            email="authtest@example.com",
            display_name="Auth Test",
            magic_link_token=token,
            magic_link_expires_at=datetime.utcnow() + timedelta(minutes=30),
            created_at=datetime.utcnow(),
        )
        db_session.add(visitor)
        await db_session.commit()
        await db_session.refresh(visitor)
        return visitor, token

    @pytest.mark.asyncio
    async def test_verify_magic_link_valid(
        self, async_client: AsyncClient, visitor_with_magic_link
    ):
        """Verify valid magic link creates session."""
        visitor, token = visitor_with_magic_link

        response = await async_client.post(
            "/api/v1/visitors/auth/verify",
            params={"token": token},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["visitor_id"] == visitor.id
        assert "session_token" in data
        assert "expires_at" in data

    @pytest.mark.asyncio
    async def test_verify_magic_link_invalid(self, async_client: AsyncClient):
        """Verify invalid magic link returns 401."""
        response = await async_client.post(
            "/api/v1/visitors/auth/verify",
            params={"token": "invalid_token_here"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_magic_link_expired(self, async_client: AsyncClient, db_session):
        """Verify expired magic link returns 401."""
        import secrets

        token = secrets.token_urlsafe(32)
        visitor = SiteVisitor(
            id=str(uuid4()),
            email="expired@example.com",
            display_name="Expired Test",
            magic_link_token=token,
            magic_link_expires_at=datetime.utcnow() - timedelta(minutes=5),  # Expired
            created_at=datetime.utcnow(),
        )
        db_session.add(visitor)
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/visitors/auth/verify",
            params={"token": token},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_visitor(
        self, async_client: AsyncClient, db_session
    ):
        """Get current visitor from session token."""
        import secrets

        session_token = secrets.token_urlsafe(32)
        visitor = SiteVisitor(
            id=str(uuid4()),
            email="session@example.com",
            display_name="Session Test",
            session_token=session_token,
            session_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
        )
        db_session.add(visitor)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/visitors/auth/me",
            params={"session_token": session_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "session@example.com"

    @pytest.mark.asyncio
    async def test_visitor_logout(self, async_client: AsyncClient, db_session):
        """Logout ends visitor session."""
        import secrets

        session_token = secrets.token_urlsafe(32)
        visitor = SiteVisitor(
            id=str(uuid4()),
            email="logout@example.com",
            display_name="Logout Test",
            session_token=session_token,
            session_expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow(),
        )
        db_session.add(visitor)
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/visitors/auth/logout",
            params={"session_token": session_token},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "logged_out"

        # Session should now be invalid
        response = await async_client.get(
            "/api/v1/visitors/auth/me",
            params={"session_token": session_token},
        )
        assert response.status_code == 401
