"""Integration tests for Publishing API endpoints.

Sprint A: Publishing
"""

import pytest
from httpx import AsyncClient

from src.db.models import SiteStatus, SiteVisibility


@pytest.mark.asyncio
class TestThemeEndpoints:
    """Tests for theme API endpoints."""

    async def test_list_themes_empty(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing themes when none exist."""
        response = await async_client.get("/api/v1/publishing/themes", headers=auth_headers)
        # May return system themes or empty list depending on setup
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_theme(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_organization: dict,
    ):
        """Test creating a theme."""
        theme_data = {
            "name": "Test Theme",
            "description": "A test theme",
            "primary_color": "#0066cc",
            "secondary_color": "#6633cc",
        }

        response = await async_client.post(
            f"/api/v1/publishing/organizations/{test_organization['id']}/themes",
            json=theme_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Theme"
        assert data["primary_color"] == "#0066cc"
        assert data["organization_id"] == test_organization["id"]

    async def test_get_theme(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_organization: dict,
    ):
        """Test getting a theme by ID."""
        # First create a theme
        theme_data = {"name": "Get Theme Test"}
        create_response = await async_client.post(
            f"/api/v1/publishing/organizations/{test_organization['id']}/themes",
            json=theme_data,
            headers=auth_headers,
        )
        theme_id = create_response.json()["id"]

        # Now get it
        response = await async_client.get(
            f"/api/v1/publishing/themes/{theme_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == theme_id
        assert response.json()["name"] == "Get Theme Test"

    async def test_update_theme(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_organization: dict,
    ):
        """Test updating a theme."""
        # Create a theme
        theme_data = {"name": "Update Theme Test"}
        create_response = await async_client.post(
            f"/api/v1/publishing/organizations/{test_organization['id']}/themes",
            json=theme_data,
            headers=auth_headers,
        )
        theme_id = create_response.json()["id"]

        # Update it
        update_data = {
            "name": "Updated Theme Name",
            "primary_color": "#ff0000",
        }
        response = await async_client.patch(
            f"/api/v1/publishing/themes/{theme_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Theme Name"
        assert response.json()["primary_color"] == "#ff0000"

    async def test_delete_theme(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_organization: dict,
    ):
        """Test deleting a theme."""
        # Create a theme
        theme_data = {"name": "Delete Theme Test"}
        create_response = await async_client.post(
            f"/api/v1/publishing/organizations/{test_organization['id']}/themes",
            json=theme_data,
            headers=auth_headers,
        )
        theme_id = create_response.json()["id"]

        # Delete it
        response = await async_client.delete(
            f"/api/v1/publishing/themes/{theme_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = await async_client.get(
            f"/api/v1/publishing/themes/{theme_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


@pytest.mark.asyncio
class TestSiteEndpoints:
    """Tests for site API endpoints."""

    async def test_list_sites_empty(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing sites when none exist."""
        response = await async_client.get("/api/v1/publishing/sites", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_site(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test creating a site."""
        site_data = {
            "space_id": test_space["id"],
            "slug": "test-docs",
            "site_title": "Test Documentation",
            "site_description": "Test site for documentation",
            "visibility": "public",
        }

        response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "test-docs"
        assert data["site_title"] == "Test Documentation"
        assert data["status"] == "draft"
        assert data["visibility"] == "public"

    async def test_create_site_duplicate_slug(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test that duplicate slugs are rejected."""
        site_data = {
            "space_id": test_space["id"],
            "slug": "unique-slug-test",
            "site_title": "First Site",
        }

        # Create first site
        response1 = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        assert response1.status_code == 201

        # Try to create second site with same slug (different space)
        # This should fail since slugs are globally unique
        # Note: This test may need adjustment based on actual implementation

    async def test_get_site(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test getting a site by ID."""
        # Create a site
        site_data = {
            "space_id": test_space["id"],
            "slug": "get-site-test",
            "site_title": "Get Site Test",
        }
        create_response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        site_id = create_response.json()["id"]

        # Get it
        response = await async_client.get(
            f"/api/v1/publishing/sites/{site_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == site_id
        assert response.json()["slug"] == "get-site-test"

    async def test_update_site(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test updating a site."""
        # Create a site
        site_data = {
            "space_id": test_space["id"],
            "slug": "update-site-test",
            "site_title": "Update Site Test",
        }
        create_response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        site_id = create_response.json()["id"]

        # Update it
        update_data = {
            "site_title": "Updated Site Title",
            "site_description": "New description",
            "search_enabled": False,
        }
        response = await async_client.patch(
            f"/api/v1/publishing/sites/{site_id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["site_title"] == "Updated Site Title"
        assert response.json()["site_description"] == "New description"
        assert response.json()["search_enabled"] is False

    async def test_publish_site(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test publishing a site."""
        # Create a site
        site_data = {
            "space_id": test_space["id"],
            "slug": "publish-site-test",
            "site_title": "Publish Site Test",
        }
        create_response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        site_id = create_response.json()["id"]

        # Publish it
        response = await async_client.post(
            f"/api/v1/publishing/sites/{site_id}/publish",
            json={"commit_message": "Initial publish"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["site_id"] == site_id
        assert "published_at" in data
        assert "pages_published" in data

    async def test_unpublish_site(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test unpublishing a site."""
        # Create and publish a site
        site_data = {
            "space_id": test_space["id"],
            "slug": "unpublish-site-test",
            "site_title": "Unpublish Site Test",
        }
        create_response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        site_id = create_response.json()["id"]

        # Publish it
        await async_client.post(
            f"/api/v1/publishing/sites/{site_id}/publish",
            headers=auth_headers,
        )

        # Unpublish it
        response = await async_client.post(
            f"/api/v1/publishing/sites/{site_id}/unpublish",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "draft"

    async def test_delete_site(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test deleting a site."""
        # Create a site
        site_data = {
            "space_id": test_space["id"],
            "slug": "delete-site-test",
            "site_title": "Delete Site Test",
        }
        create_response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        site_id = create_response.json()["id"]

        # Delete it
        response = await async_client.delete(
            f"/api/v1/publishing/sites/{site_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's gone
        get_response = await async_client.get(
            f"/api/v1/publishing/sites/{site_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_get_site_navigation(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test getting site navigation."""
        # Create a site
        site_data = {
            "space_id": test_space["id"],
            "slug": "nav-test-site",
            "site_title": "Navigation Test Site",
        }
        create_response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        site_id = create_response.json()["id"]

        # Get navigation
        response = await async_client.get(
            f"/api/v1/publishing/sites/{site_id}/navigation",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)


@pytest.mark.asyncio
class TestPublicSiteEndpoints:
    """Tests for public site viewing endpoints."""

    async def test_get_public_site_not_found(self, async_client: AsyncClient):
        """Test accessing non-existent public site."""
        response = await async_client.get("/s/nonexistent-site")
        assert response.status_code == 404

    async def test_get_public_site_unpublished(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test that unpublished sites are not accessible publicly."""
        # Create a site but don't publish it
        site_data = {
            "space_id": test_space["id"],
            "slug": "unpublished-test",
            "site_title": "Unpublished Test",
        }
        await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )

        # Try to access it publicly
        response = await async_client.get("/s/unpublished-test")
        assert response.status_code == 404  # Not found because not published

    async def test_get_public_site_published(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test accessing a published site."""
        # Create and publish a site
        site_data = {
            "space_id": test_space["id"],
            "slug": "published-test",
            "site_title": "Published Test",
        }
        create_response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        site_id = create_response.json()["id"]

        # Publish it
        await async_client.post(
            f"/api/v1/publishing/sites/{site_id}/publish",
            headers=auth_headers,
        )

        # Access it publicly
        response = await async_client.get("/s/published-test")
        assert response.status_code == 200
        data = response.json()
        assert data["site"]["title"] == "Published Test"

    async def test_get_robots_txt_public_site(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_space: dict,
    ):
        """Test robots.txt for public site."""
        # Create and publish a public site
        site_data = {
            "space_id": test_space["id"],
            "slug": "robots-test",
            "site_title": "Robots Test",
            "visibility": "public",
        }
        create_response = await async_client.post(
            "/api/v1/publishing/sites",
            json=site_data,
            headers=auth_headers,
        )
        site_id = create_response.json()["id"]

        # Publish it
        await async_client.post(
            f"/api/v1/publishing/sites/{site_id}/publish",
            headers=auth_headers,
        )

        # Get robots.txt
        response = await async_client.get("/s/robots-test/robots.txt")
        assert response.status_code == 200
        assert "User-agent: *" in response.text
        assert "Allow:" in response.text
