"""Integration tests for Organizations API."""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.modules.access.security import hash_password, create_access_token


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for organization tests."""
    user = User(
        id=str(uuid4()),
        email=f"orgtest-{uuid4().hex[:8]}@example.com",
        full_name="Org Test User",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user: User):
    """Get authorization headers for the test user."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def second_user(db_session: AsyncSession):
    """Create a second test user."""
    user = User(
        id=str(uuid4()),
        email=f"orgtest2-{uuid4().hex[:8]}@example.com",
        full_name="Second Test User",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def second_user_headers(second_user: User):
    """Get authorization headers for the second user."""
    token = create_access_token(second_user.id)
    return {"Authorization": f"Bearer {token}"}


class TestOrganizationCreate:
    """Tests for organization creation."""

    @pytest.mark.asyncio
    async def test_create_organization_success(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should create an organization successfully."""
        response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "name": "Test Organization",
                "slug": f"test-org-{uuid4().hex[:8]}",
                "description": "A test organization",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Organization"
        assert data["description"] == "A test organization"
        assert "id" in data
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_organization_without_auth(self, async_client: AsyncClient):
        """Should return 401 without authentication."""
        response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "name": "Test Org",
                "slug": "test-org",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_organization_duplicate_slug(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 400 for duplicate slug."""
        slug = f"duplicate-slug-{uuid4().hex[:8]}"

        # Create first org
        await async_client.post(
            "/api/v1/organizations/",
            json={"name": "First Org", "slug": slug},
            headers=auth_headers,
        )

        # Try to create second with same slug
        response = await async_client.post(
            "/api/v1/organizations/",
            json={"name": "Second Org", "slug": slug},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_organization_missing_name(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 422 for missing name."""
        response = await async_client.post(
            "/api/v1/organizations/",
            json={"slug": "test-org"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_organization_missing_slug(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 422 for missing slug."""
        response = await async_client.post(
            "/api/v1/organizations/",
            json={"name": "Test Org"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestOrganizationList:
    """Tests for listing organizations."""

    @pytest.mark.asyncio
    async def test_list_organizations_empty(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return empty list when user has no organizations."""
        response = await async_client.get(
            "/api/v1/organizations/",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_organizations_returns_owned(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return organizations the user is a member of."""
        # Create an organization
        create_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "name": "My Organization",
                "slug": f"my-org-{uuid4().hex[:8]}",
            },
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        org_id = create_response.json()["id"]

        # List should include the created org
        response = await async_client.get(
            "/api/v1/organizations/",
            headers=auth_headers,
        )

        assert response.status_code == 200
        orgs = response.json()
        assert len(orgs) >= 1
        org_ids = [org["id"] for org in orgs]
        assert org_id in org_ids

    @pytest.mark.asyncio
    async def test_list_organizations_excludes_others(
        self,
        async_client: AsyncClient,
        auth_headers,
        second_user_headers,
    ):
        """Should not return organizations owned by other users."""
        # First user creates an org
        slug = f"first-user-org-{uuid4().hex[:8]}"
        await async_client.post(
            "/api/v1/organizations/",
            json={"name": "First User Org", "slug": slug},
            headers=auth_headers,
        )

        # Second user should not see it
        response = await async_client.get(
            "/api/v1/organizations/",
            headers=second_user_headers,
        )

        assert response.status_code == 200
        orgs = response.json()
        org_slugs = [org["slug"] for org in orgs]
        assert slug not in org_slugs

    @pytest.mark.asyncio
    async def test_list_organizations_without_auth(self, async_client: AsyncClient):
        """Should return 401 without authentication."""
        response = await async_client.get("/api/v1/organizations/")
        assert response.status_code == 401


class TestOrganizationGet:
    """Tests for getting a single organization."""

    @pytest.mark.asyncio
    async def test_get_organization_success(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return organization details."""
        # Create org
        create_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "name": "Get Test Org",
                "slug": f"get-test-org-{uuid4().hex[:8]}",
                "description": "Test description",
            },
            headers=auth_headers,
        )
        org_id = create_response.json()["id"]

        # Get org
        response = await async_client.get(
            f"/api/v1/organizations/{org_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == org_id
        assert data["name"] == "Get Test Org"
        assert data["description"] == "Test description"

    @pytest.mark.asyncio
    async def test_get_organization_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent organization."""
        fake_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/organizations/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestOrganizationUpdate:
    """Tests for updating organizations."""

    @pytest.mark.asyncio
    async def test_update_organization_success(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should update organization successfully."""
        # Create org
        create_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "name": "Original Name",
                "slug": f"update-test-{uuid4().hex[:8]}",
            },
            headers=auth_headers,
        )
        org_id = create_response.json()["id"]

        # Update org
        response = await async_client.patch(
            f"/api/v1/organizations/{org_id}",
            json={
                "name": "Updated Name",
                "description": "New description",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_organization_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent organization."""
        fake_id = str(uuid4())
        response = await async_client.patch(
            f"/api/v1/organizations/{fake_id}",
            json={"name": "New Name"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestOrganizationMembership:
    """Tests for organization membership (owner is automatically a member)."""

    @pytest.mark.asyncio
    async def test_creator_is_member(
        self, async_client: AsyncClient, auth_headers
    ):
        """Creator should automatically be a member of the organization."""
        # Create org
        create_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "name": "Membership Test Org",
                "slug": f"membership-test-{uuid4().hex[:8]}",
            },
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        org_id = create_response.json()["id"]

        # List orgs should include this one (only members can see)
        list_response = await async_client.get(
            "/api/v1/organizations/",
            headers=auth_headers,
        )

        assert list_response.status_code == 200
        orgs = list_response.json()
        org_ids = [org["id"] for org in orgs]
        assert org_id in org_ids, "Creator should be able to see their own organization"

    @pytest.mark.asyncio
    async def test_multiple_orgs_all_visible(
        self, async_client: AsyncClient, auth_headers
    ):
        """User should see all organizations they create."""
        created_ids = []

        # Create 3 organizations
        for i in range(3):
            response = await async_client.post(
                "/api/v1/organizations/",
                json={
                    "name": f"Multi Org {i}",
                    "slug": f"multi-org-{i}-{uuid4().hex[:8]}",
                },
                headers=auth_headers,
            )
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # List should include all 3
        list_response = await async_client.get(
            "/api/v1/organizations/",
            headers=auth_headers,
        )

        assert list_response.status_code == 200
        orgs = list_response.json()
        org_ids = [org["id"] for org in orgs]

        for created_id in created_ids:
            assert created_id in org_ids
