"""Integration tests for Spaces API."""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, Organization, Workspace
from src.modules.access.security import hash_password, create_access_token


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for space tests."""
    user = User(
        id=str(uuid4()),
        email=f"spacetest-{uuid4().hex[:8]}@example.com",
        full_name="Space Test User",
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
    """Create a test organization for space tests."""
    response = await async_client.post(
        "/api/v1/organizations/",
        json={
            "name": "Space Test Org",
            "slug": f"space-test-org-{uuid4().hex[:8]}",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def test_workspace(async_client: AsyncClient, auth_headers, test_organization):
    """Create a test workspace for space tests."""
    response = await async_client.post(
        "/api/v1/workspaces/",
        json={
            "name": "Space Test Workspace",
            "slug": f"space-test-ws-{uuid4().hex[:8]}",
            "organization_id": test_organization["id"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


class TestSpaceCreate:
    """Tests for space creation."""

    @pytest.mark.asyncio
    async def test_create_space_success(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should create a space successfully."""
        response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Test Space",
                "slug": f"test-space-{uuid4().hex[:8]}",
                "workspace_id": test_workspace["id"],
                "description": "A test space",
                "diataxis_type": "tutorial",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Space"
        assert data["description"] == "A test space"
        assert data["workspace_id"] == test_workspace["id"]
        assert data["diataxis_type"] == "tutorial"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_space_all_diataxis_types(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should create spaces with all Diátaxis types."""
        diataxis_types = ["tutorial", "how_to", "reference", "explanation"]

        for dtype in diataxis_types:
            response = await async_client.post(
                "/api/v1/spaces/",
                json={
                    "name": f"{dtype.replace('_', ' ').title()} Space",
                    "slug": f"{dtype.replace('_', '-')}-space-{uuid4().hex[:8]}",
                    "workspace_id": test_workspace["id"],
                    "diataxis_type": dtype,
                },
                headers=auth_headers,
            )

            assert response.status_code == 201, f"Failed to create {dtype} space: {response.text}"
            assert response.json()["diataxis_type"] == dtype

    @pytest.mark.asyncio
    async def test_create_space_without_auth(
        self, async_client: AsyncClient, test_workspace
    ):
        """Should return 401 without authentication."""
        response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Test Space",
                "slug": "test-space",
                "workspace_id": test_workspace["id"],
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_space_invalid_workspace(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent workspace."""
        fake_ws_id = str(uuid4())
        response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Test Space",
                "slug": "test-space",
                "workspace_id": fake_ws_id,
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_space_missing_name(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should return 422 for missing name."""
        response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "slug": "test-space",
                "workspace_id": test_workspace["id"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_space_missing_slug(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should return 422 for missing slug."""
        response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Test Space",
                "workspace_id": test_workspace["id"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestSpaceList:
    """Tests for listing spaces."""

    @pytest.mark.asyncio
    async def test_list_spaces_by_workspace(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should list spaces for a workspace."""
        ws_id = test_workspace["id"]

        # Create spaces
        for i in range(3):
            await async_client.post(
                "/api/v1/spaces/",
                json={
                    "name": f"Space {i}",
                    "slug": f"space-{i}-{uuid4().hex[:8]}",
                    "workspace_id": ws_id,
                    "diataxis_type": "tutorial",
                },
                headers=auth_headers,
            )

        # List spaces
        response = await async_client.get(
            f"/api/v1/spaces/workspace/{ws_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        spaces = response.json()
        assert len(spaces) >= 3

    @pytest.mark.asyncio
    async def test_list_spaces_empty_workspace(
        self, async_client: AsyncClient, auth_headers, test_organization
    ):
        """Should return empty list for workspace with no spaces."""
        # Create a new workspace with no spaces
        ws_response = await async_client.post(
            "/api/v1/workspaces/",
            json={
                "name": "Empty Workspace",
                "slug": f"empty-ws-{uuid4().hex[:8]}",
                "organization_id": test_organization["id"],
            },
            headers=auth_headers,
        )
        ws_id = ws_response.json()["id"]

        response = await async_client.get(
            f"/api/v1/spaces/workspace/{ws_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_spaces_without_auth(
        self, async_client: AsyncClient, test_workspace
    ):
        """Should return 401 without authentication."""
        response = await async_client.get(
            f"/api/v1/spaces/workspace/{test_workspace['id']}",
        )
        assert response.status_code == 401


class TestSpaceGet:
    """Tests for getting a single space."""

    @pytest.mark.asyncio
    async def test_get_space_success(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should return space details."""
        # Create space
        create_response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Get Test Space",
                "slug": f"get-test-space-{uuid4().hex[:8]}",
                "workspace_id": test_workspace["id"],
                "description": "Test description",
                "diataxis_type": "how_to",
            },
            headers=auth_headers,
        )
        space_id = create_response.json()["id"]

        # Get space
        response = await async_client.get(
            f"/api/v1/spaces/{space_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == space_id
        assert data["name"] == "Get Test Space"
        assert data["description"] == "Test description"
        assert data["diataxis_type"] == "how_to"

    @pytest.mark.asyncio
    async def test_get_space_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent space."""
        fake_id = str(uuid4())
        response = await async_client.get(
            f"/api/v1/spaces/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestSpaceUpdate:
    """Tests for updating spaces."""

    @pytest.mark.asyncio
    async def test_update_space_success(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should update space successfully."""
        # Create space
        create_response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Original Space",
                "slug": f"update-test-space-{uuid4().hex[:8]}",
                "workspace_id": test_workspace["id"],
                "diataxis_type": "tutorial",
            },
            headers=auth_headers,
        )
        space_id = create_response.json()["id"]

        # Update space
        response = await async_client.patch(
            f"/api/v1/spaces/{space_id}",
            json={
                "name": "Updated Space",
                "description": "New description",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Space"
        assert data["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_space_change_type(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should update space Diátaxis type."""
        # Create space
        create_response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Type Test Space",
                "slug": f"type-test-space-{uuid4().hex[:8]}",
                "workspace_id": test_workspace["id"],
                "diataxis_type": "tutorial",
            },
            headers=auth_headers,
        )
        space_id = create_response.json()["id"]
        assert create_response.json()["diataxis_type"] == "tutorial"

        # Update type
        response = await async_client.patch(
            f"/api/v1/spaces/{space_id}",
            json={"diataxis_type": "reference"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["diataxis_type"] == "reference"

    @pytest.mark.asyncio
    async def test_update_space_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent space."""
        fake_id = str(uuid4())
        response = await async_client.patch(
            f"/api/v1/spaces/{fake_id}",
            json={"name": "New Name"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestSpaceWithPages:
    """Tests for spaces with pages (integration)."""

    @pytest.mark.asyncio
    async def test_space_can_have_pages(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should be able to create pages in a space."""
        # Create space
        space_response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Pages Test Space",
                "slug": f"pages-test-space-{uuid4().hex[:8]}",
                "workspace_id": test_workspace["id"],
                "diataxis_type": "tutorial",
            },
            headers=auth_headers,
        )
        space_id = space_response.json()["id"]

        # Create pages
        for i in range(3):
            page_response = await async_client.post(
                "/api/v1/content/pages",
                json={
                    "title": f"Test Page {i}",
                    "slug": f"test-page-{i}-{uuid4().hex[:8]}",
                    "space_id": space_id,
                },
                headers=auth_headers,
            )
            assert page_response.status_code == 201, f"Failed to create page: {page_response.text}"

        # List pages in space
        pages_response = await async_client.get(
            f"/api/v1/content/space/{space_id}/pages",
            headers=auth_headers,
        )

        assert pages_response.status_code == 200
        pages = pages_response.json()
        assert len(pages) >= 3

    @pytest.mark.asyncio
    async def test_list_pages_empty_space(
        self, async_client: AsyncClient, auth_headers, test_workspace
    ):
        """Should return empty list for space with no pages."""
        # Create space
        space_response = await async_client.post(
            "/api/v1/spaces/",
            json={
                "name": "Empty Pages Space",
                "slug": f"empty-pages-space-{uuid4().hex[:8]}",
                "workspace_id": test_workspace["id"],
                "diataxis_type": "reference",
            },
            headers=auth_headers,
        )
        space_id = space_response.json()["id"]

        # List pages
        pages_response = await async_client.get(
            f"/api/v1/content/space/{space_id}/pages",
            headers=auth_headers,
        )

        assert pages_response.status_code == 200
        assert pages_response.json() == []
