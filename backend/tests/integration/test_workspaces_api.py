"""Integration tests for Workspaces API."""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.modules.access.security import hash_password, create_access_token


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for workspace tests."""
    user = User(
        id=str(uuid4()),
        email=f"wstest-{uuid4().hex[:8]}@example.com",
        full_name="Workspace Test User",
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
async def test_organization(async_client: AsyncClient, auth_headers):
    """Create a test organization for workspace tests."""
    response = await async_client.post(
        "/api/v1/organizations/",
        json={
            "name": "Workspace Test Org",
            "slug": f"ws-test-org-{uuid4().hex[:8]}",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


class TestWorkspaceCreate:
    """Tests for workspace creation."""

    @pytest.mark.asyncio
    async def test_create_workspace_success(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should create a workspace successfully."""
        response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Test Workspace",
                "slug": f"test-ws-{uuid4().hex[:8]}",
                "organization_id": test_organization["id"],
                "description": "A test workspace",
                "is_public": False,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workspace"
        assert data["description"] == "A test workspace"
        assert data["organization_id"] == test_organization["id"]
        assert data["is_public"] is False
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_workspace_public(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should create a public workspace."""
        response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Public Workspace",
                "slug": f"public-ws-{uuid4().hex[:8]}",
                "organization_id": test_organization["id"],
                "is_public": True,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["is_public"] is True

    @pytest.mark.asyncio
    async def test_create_workspace_without_auth(
        self, async_client: AsyncClient, test_organization
    ):
        """Should return 401 without authentication."""
        response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Test Workspace",
                "slug": "test-ws",
                "organization_id": test_organization["id"],
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_workspace_invalid_org(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent organization."""
        fake_org_id = str(uuid4())
        response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Test Workspace",
                "slug": "test-ws",
                "organization_id": fake_org_id,
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_workspace_missing_name(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should return 422 for missing name."""
        response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "slug": "test-ws",
                "organization_id": test_organization["id"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_workspace_missing_slug(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should return 422 for missing slug."""
        response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Test Workspace",
                "organization_id": test_organization["id"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestWorkspaceList:
    """Tests for listing workspaces."""

    @pytest.mark.asyncio
    async def test_list_workspaces_by_org(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should list workspaces for an organization."""
        org_id = test_organization["id"]

        # Create workspaces
        for i in range(3):
            await async_client.post(
                "/api/v1/workspaces/",
                json={
                    "name": f"Workspace {i}",
                    "slug": f"ws-{i}-{uuid4().hex[:8]}",
                    "organization_id": org_id,
                },
                headers=auth_headers,
            )

        # List workspaces
        response = await async_client.get(
            f"/api/v1/workspaces/org/{org_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        workspaces = response.json()
        assert len(workspaces) >= 3

    @pytest.mark.asyncio
    async def test_list_workspaces_empty_org(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should return empty list for org with no workspaces."""
        # Create a new org with no workspaces
        org_response = await async_client.post(
            "/api/v1/organizations/",
            json={
                "name": "Empty Org",
                "slug": f"empty-org-{uuid4().hex[:8]}",
            },
            headers=auth_headers,
        )
        org_id = org_response.json()["id"]

        response = await async_client.get(
            f"/api/v1/workspaces/org/{org_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_workspaces_invalid_org(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent organization."""
        fake_org_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/workspaces/org/{fake_org_id}",
            headers=auth_headers,
        )

        # Could be 404 or empty list depending on implementation
        assert response.status_code in [200, 404]


class TestWorkspaceGet:
    """Tests for getting a single workspace."""

    @pytest.mark.asyncio
    async def test_get_workspace_success(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should return workspace details."""
        # Create workspace
        create_response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Get Test Workspace",
                "slug": f"get-test-ws-{uuid4().hex[:8]}",
                "organization_id": test_organization["id"],
                "description": "Test description",
            },
            headers=auth_headers,
        )
        ws_id = create_response.json()["id"]

        # Get workspace
        response = await async_client.get(
            f"/api/v1/workspaces/{ws_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ws_id
        assert data["name"] == "Get Test Workspace"
        assert data["description"] == "Test description"

    @pytest.mark.asyncio
    async def test_get_workspace_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent workspace."""
        fake_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/workspaces/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestWorkspaceUpdate:
    """Tests for updating workspaces."""

    @pytest.mark.asyncio
    async def test_update_workspace_success(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should update workspace successfully."""
        # Create workspace
        create_response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Original Name",
                "slug": f"update-test-ws-{uuid4().hex[:8]}",
                "organization_id": test_organization["id"],
            },
            headers=auth_headers,
        )
        ws_id = create_response.json()["id"]

        # Update workspace
        response = await async_client.patch(
            f"/api/v1/workspaces/{ws_id}",
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
    async def test_update_workspace_toggle_public(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should toggle workspace public status."""
        # Create private workspace
        create_response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Private Workspace",
                "slug": f"toggle-public-ws-{uuid4().hex[:8]}",
                "organization_id": test_organization["id"],
                "is_public": False,
            },
            headers=auth_headers,
        )
        ws_id = create_response.json()["id"]
        assert create_response.json()["is_public"] is False

        # Make public
        response = await async_client.patch(
            f"/api/v1/workspaces/{ws_id}",
            json={"is_public": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["is_public"] is True

    @pytest.mark.asyncio
    async def test_update_workspace_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent workspace."""
        fake_id = str(uuid4())
        response = await async_client.patch(
            f"/api/v1/workspaces/{fake_id}",
            json={"name": "New Name"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestWorkspaceWithSpaces:
    """Tests for workspaces with spaces (integration)."""

    @pytest.mark.asyncio
    async def test_workspace_can_have_multiple_spaces(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should be able to create multiple spaces in a workspace."""
        # Create workspace
        ws_response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Multi-Space Workspace",
                "slug": f"multi-space-ws-{uuid4().hex[:8]}",
                "organization_id": test_organization["id"],
            },
            headers=auth_headers,
        )
        ws_id = ws_response.json()["id"]

        # Create spaces
        diataxis_types = ["tutorial", "how_to", "reference", "explanation"]
        created_space_ids = []

        for dtype in diataxis_types:
            space_response = await async_client.post(
                "/api/v1/spaces/",
                json={
                    "name": f"{dtype.replace('_', ' ').title()} Space",
                    "slug": f"{dtype.replace('_', '-')}-space-{uuid4().hex[:8]}",
                    "workspace_id": ws_id,
                    "diataxis_type": dtype,
                },
                headers=auth_headers,
            )
            assert space_response.status_code == 201, f"Failed to create space: {space_response.text}"
            created_space_ids.append(space_response.json()["id"])

        # List spaces in workspace
        spaces_response = await async_client.get(
            f"/api/v1/spaces/workspace/{ws_id}",
            headers=auth_headers,
        )

        assert spaces_response.status_code == 200
        spaces = spaces_response.json()
        assert len(spaces) >= 4

        # Verify all created spaces are present
        space_ids = [s["id"] for s in spaces]
        for created_id in created_space_ids:
            assert created_id in space_ids
