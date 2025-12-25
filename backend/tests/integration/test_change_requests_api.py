"""Integration tests for Change Requests API (Sprint 4)."""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, Organization, Workspace, Space, Page


@pytest.fixture
async def setup_test_page(db_session: AsyncSession, patch_git_service):
    """Create a complete test hierarchy: org -> workspace -> space -> page.

    Uses patch_git_service to mock Git operations for integration tests.
    """
    from src.modules.access.security import hash_password

    # Use unique identifiers for each test run
    unique_id = uuid4().hex[:8]

    # Create user
    user = User(
        id=str(uuid4()),
        email=f"author-{unique_id}@example.com",
        full_name="Test Author",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(user)

    # Create another user for review
    reviewer = User(
        id=str(uuid4()),
        email=f"reviewer-{unique_id}@example.com",
        full_name="Test Reviewer",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(reviewer)

    # Create organization
    org = Organization(
        id=str(uuid4()),
        name="Test Org",
        slug=f"test-org-{unique_id}",
        owner_id=user.id,
        is_active=True,
    )
    db_session.add(org)

    # Create workspace
    workspace = Workspace(
        id=str(uuid4()),
        name="Test Workspace",
        slug=f"test-workspace-{unique_id}",
        organization_id=org.id,
        is_active=True,
    )
    db_session.add(workspace)

    # Create space
    space = Space(
        id=str(uuid4()),
        name="Test Space",
        slug=f"test-space-{unique_id}",
        workspace_id=workspace.id,
        diataxis_type="tutorial",
        is_active=True,
    )
    db_session.add(space)

    # Create page
    page = Page(
        id=str(uuid4()),
        title="Test Page",
        slug=f"test-page-{unique_id}",
        space_id=space.id,
        author_id=user.id,
        content={"type": "doc", "content": []},
        version="1.0",
        status="effective",
        git_commit_sha="abc123def456789012345678901234567890abcd",
        is_active=True,
    )
    db_session.add(page)

    await db_session.commit()

    return {
        "user": user,
        "reviewer": reviewer,
        "org": org,
        "workspace": workspace,
        "space": space,
        "page": page,
    }


@pytest.fixture
async def auth_headers(setup_test_page):
    """Get authorization headers for the test user."""
    from src.modules.access.security import create_access_token

    user = setup_test_page["user"]
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def reviewer_auth_headers(setup_test_page):
    """Get authorization headers for the reviewer user."""
    from src.modules.access.security import create_access_token

    reviewer = setup_test_page["reviewer"]
    token = create_access_token(reviewer.id)
    return {"Authorization": f"Bearer {token}"}


class TestDraftCRUD:
    """Tests for draft CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_draft_success(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should create a new draft successfully."""
        page = setup_test_page["page"]

        response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={
                "title": "Update installation guide",
                "description": "Add troubleshooting section",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Update installation guide"
        assert data["description"] == "Add troubleshooting section"
        assert data["status"] == "draft"
        assert data["number"] == 1
        assert "CR-0001" in data["branch_name"]

    @pytest.mark.asyncio
    async def test_create_draft_page_not_found(
        self, async_client: AsyncClient, auth_headers
    ):
        """Should return 404 for non-existent page."""
        fake_page_id = str(uuid4())

        response = await async_client.post(
            f"/api/v1/content/pages/{fake_page_id}/drafts",
            json={"title": "Test Draft"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_drafts(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should list all drafts for a page."""
        page = setup_test_page["page"]

        # Create two drafts
        await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Draft 1"},
            headers=auth_headers,
        )
        await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Draft 2"},
            headers=auth_headers,
        )

        response = await async_client.get(
            f"/api/v1/content/pages/{page.id}/drafts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_draft(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should get a specific draft by ID."""
        page = setup_test_page["page"]

        # Create draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Test Draft"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        # Get draft
        response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == draft_id

    @pytest.mark.asyncio
    async def test_update_draft(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should update draft metadata."""
        page = setup_test_page["page"]

        # Create draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Original Title"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        # Update draft
        response = await async_client.patch(
            f"/api/v1/content/drafts/{draft_id}",
            json={"title": "Updated Title", "description": "Added description"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Added description"

    @pytest.mark.asyncio
    async def test_cancel_draft(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should cancel a draft."""
        page = setup_test_page["page"]

        # Create draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Draft to Cancel"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        # Cancel draft
        response = await async_client.delete(
            f"/api/v1/content/drafts/{draft_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204


class TestDraftWorkflow:
    """Tests for draft workflow operations."""

    @pytest.mark.asyncio
    async def test_submit_for_review(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should submit draft for review."""
        page = setup_test_page["page"]

        # Create draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Draft for Review"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        # Submit for review
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "submitted"
        assert response.json()["submitted_at"] is not None

    @pytest.mark.asyncio
    async def test_approve_draft(
        self,
        async_client: AsyncClient,
        setup_test_page,
        auth_headers,
        reviewer_auth_headers,
    ):
        """Should approve a submitted draft."""
        page = setup_test_page["page"]

        # Create and submit draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Draft for Approval"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=auth_headers,
        )

        # Approve (as reviewer)
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={"comment": "Looks good!"},
            headers=reviewer_auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "approved"
        assert response.json()["review_comment"] == "Looks good!"

    @pytest.mark.asyncio
    async def test_author_cannot_approve_own_draft(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Author should not be able to approve their own draft."""
        page = setup_test_page["page"]

        # Create and submit draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "My Draft"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=auth_headers,
        )

        # Try to approve own draft
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={},
            headers=auth_headers,  # Same user as author
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_request_changes(
        self,
        async_client: AsyncClient,
        setup_test_page,
        auth_headers,
        reviewer_auth_headers,
    ):
        """Should request changes on a draft."""
        page = setup_test_page["page"]

        # Create and submit draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Draft Needing Changes"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=auth_headers,
        )

        # Request changes (as reviewer)
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/request-changes",
            json={"comment": "Please fix the typos"},
            headers=reviewer_auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "changes_requested"
        assert response.json()["review_comment"] == "Please fix the typos"

    @pytest.mark.asyncio
    async def test_request_changes_requires_comment(
        self,
        async_client: AsyncClient,
        setup_test_page,
        auth_headers,
        reviewer_auth_headers,
    ):
        """Request changes should require a comment."""
        page = setup_test_page["page"]

        # Create and submit draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Draft"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=auth_headers,
        )

        # Request changes without comment
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/request-changes",
            json={},
            headers=reviewer_auth_headers,
        )

        assert response.status_code == 400


class TestDraftComments:
    """Tests for draft comment operations."""

    @pytest.mark.asyncio
    async def test_add_comment(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should add a comment to a draft."""
        page = setup_test_page["page"]

        # Create draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Draft with Comments"},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        # Add comment
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/comments",
            json={"content": "This is a test comment"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "This is a test comment"
        assert data["change_request_id"] == draft_id

    @pytest.mark.asyncio
    async def test_add_line_comment(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should add a line-specific comment."""
        page = setup_test_page["page"]

        # Create draft with unique title to avoid branch name collision
        unique_title = f"Draft for Line Comment {uuid4().hex[:8]}"
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": unique_title},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        # Add line comment
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/comments",
            json={
                "content": "This line needs fixing",
                "file_path": "content.json",
                "line_number": 42,
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["file_path"] == "content.json"
        assert data["line_number"] == 42

    @pytest.mark.asyncio
    async def test_list_comments(
        self, async_client: AsyncClient, setup_test_page, auth_headers
    ):
        """Should list all comments on a draft."""
        page = setup_test_page["page"]

        # Create draft with unique title to avoid branch name collision
        unique_title = f"Draft for List Comments {uuid4().hex[:8]}"
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": unique_title},
            headers=auth_headers,
        )
        draft_id = create_response.json()["id"]

        # Add comments
        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/comments",
            json={"content": "Comment 1"},
            headers=auth_headers,
        )
        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/comments",
            json={"content": "Comment 2"},
            headers=auth_headers,
        )

        # List comments
        response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}/comments",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert len(response.json()) == 2
