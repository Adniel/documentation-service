"""Integration tests for merge conflict detection.

Tests the conflict detection API endpoint and the underlying
service logic for identifying merge conflicts before publish.
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, Organization, Workspace, Space, Page


@pytest.fixture
async def setup_conflict_test_hierarchy(db_session: AsyncSession, patch_git_service):
    """Create test hierarchy for conflict testing."""
    from src.modules.access.security import hash_password

    unique_id = uuid4().hex[:8]

    # Create author user
    author = User(
        id=str(uuid4()),
        email=f"author-{unique_id}@example.com",
        full_name="Content Author",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(author)

    # Create reviewer user
    reviewer = User(
        id=str(uuid4()),
        email=f"reviewer-{unique_id}@example.com",
        full_name="Content Reviewer",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(reviewer)

    # Create organization
    org = Organization(
        id=str(uuid4()),
        name="Conflict Test Org",
        slug=f"conflict-org-{unique_id}",
        owner_id=author.id,
        is_active=True,
    )
    db_session.add(org)

    # Create workspace
    workspace = Workspace(
        id=str(uuid4()),
        name="Conflict Workspace",
        slug=f"conflict-ws-{unique_id}",
        organization_id=org.id,
        is_active=True,
    )
    db_session.add(workspace)

    # Create space
    space = Space(
        id=str(uuid4()),
        name="Conflict Space",
        slug=f"conflict-space-{unique_id}",
        workspace_id=workspace.id,
        diataxis_type="tutorial",
        is_active=True,
    )
    db_session.add(space)

    # Create page with initial content
    page = Page(
        id=str(uuid4()),
        title="Conflict Test Page",
        slug=f"conflict-page-{unique_id}",
        space_id=space.id,
        author_id=author.id,
        content={"type": "doc", "content": []},
        version="1.0",
        status="effective",
        git_commit_sha="initial123abc456def789012345678901234567890",
        is_active=True,
    )
    db_session.add(page)

    await db_session.commit()

    return {
        "author": author,
        "reviewer": reviewer,
        "org": org,
        "workspace": workspace,
        "space": space,
        "page": page,
        "git_mock": patch_git_service,
    }


@pytest.fixture
async def author_headers(setup_conflict_test_hierarchy):
    """Get authorization headers for the author."""
    from src.modules.access.security import create_access_token

    user = setup_conflict_test_hierarchy["author"]
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def reviewer_headers(setup_conflict_test_hierarchy):
    """Get authorization headers for the reviewer."""
    from src.modules.access.security import create_access_token

    user = setup_conflict_test_hierarchy["reviewer"]
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


class TestConflictDetection:
    """Tests for merge conflict detection."""

    @pytest.mark.asyncio
    async def test_check_conflicts_no_conflict(
        self,
        async_client: AsyncClient,
        setup_conflict_test_hierarchy,
        author_headers,
    ):
        """Should return no conflicts for clean draft."""
        page = setup_conflict_test_hierarchy["page"]

        # Create a draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Clean Draft"},
            headers=author_headers,
        )
        assert create_response.status_code == 201
        draft_id = create_response.json()["id"]

        # Check for conflicts
        response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}/conflicts",
            headers=author_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_conflicts"] is False
        assert data["conflict_files"] == []

    @pytest.mark.asyncio
    async def test_check_conflicts_with_conflict(
        self,
        async_client: AsyncClient,
        setup_conflict_test_hierarchy,
        author_headers,
    ):
        """Should detect conflicts when present."""
        page = setup_conflict_test_hierarchy["page"]
        git_mock = setup_conflict_test_hierarchy["git_mock"]

        # Create a draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": "Conflicting Draft"},
            headers=author_headers,
        )
        assert create_response.status_code == 201
        draft_data = create_response.json()
        draft_id = draft_data["id"]
        branch_name = draft_data["branch_name"]

        # Simulate a conflict on this branch
        git_mock._simulate_conflict(branch_name)

        # Check for conflicts
        response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}/conflicts",
            headers=author_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_conflicts"] is True
        assert "content.json" in data["conflict_files"]

    @pytest.mark.asyncio
    async def test_publish_fails_with_conflict(
        self,
        async_client: AsyncClient,
        setup_conflict_test_hierarchy,
        author_headers,
        reviewer_headers,
    ):
        """Should fail to publish when conflicts exist."""
        page = setup_conflict_test_hierarchy["page"]
        git_mock = setup_conflict_test_hierarchy["git_mock"]

        # Create and approve a draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": f"Draft to Fail {uuid4().hex[:8]}"},
            headers=author_headers,
        )
        assert create_response.status_code == 201
        draft_data = create_response.json()
        draft_id = draft_data["id"]
        branch_name = draft_data["branch_name"]

        # Submit for review
        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )

        # Approve
        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={"comment": "Approved"},
            headers=reviewer_headers,
        )

        # Simulate a conflict on this branch
        git_mock._simulate_conflict(branch_name)

        # Try to publish - should fail
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/publish",
            headers=author_headers,
        )

        assert response.status_code == 409
        assert "conflict" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_publish_succeeds_without_conflict(
        self,
        async_client: AsyncClient,
        setup_conflict_test_hierarchy,
        author_headers,
        reviewer_headers,
    ):
        """Should successfully publish when no conflicts."""
        page = setup_conflict_test_hierarchy["page"]

        # Create a draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": f"Draft to Publish {uuid4().hex[:8]}"},
            headers=author_headers,
        )
        assert create_response.status_code == 201
        draft_id = create_response.json()["id"]

        # Submit for review
        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )

        # Approve
        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={"comment": "Looks good"},
            headers=reviewer_headers,
        )

        # Publish - should succeed
        response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/publish",
            headers=author_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert data["merge_commit_sha"] is not None

    @pytest.mark.asyncio
    async def test_check_conflicts_draft_not_found(
        self,
        async_client: AsyncClient,
        setup_conflict_test_hierarchy,
        author_headers,
    ):
        """Should return 404 for non-existent draft."""
        fake_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/content/drafts/{fake_id}/conflicts",
            headers=author_headers,
        )

        assert response.status_code == 404


class TestConflictResolutionWorkflow:
    """Tests for conflict resolution workflows."""

    @pytest.mark.asyncio
    async def test_conflict_detected_before_publish(
        self,
        async_client: AsyncClient,
        setup_conflict_test_hierarchy,
        author_headers,
        reviewer_headers,
    ):
        """Demonstrate checking for conflicts before attempting publish."""
        page = setup_conflict_test_hierarchy["page"]
        git_mock = setup_conflict_test_hierarchy["git_mock"]

        # Create and approve draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": f"Check Before Publish {uuid4().hex[:8]}"},
            headers=author_headers,
        )
        draft_data = create_response.json()
        draft_id = draft_data["id"]
        branch_name = draft_data["branch_name"]

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={"comment": "OK"},
            headers=reviewer_headers,
        )

        # Simulate conflict happening after approval
        git_mock._simulate_conflict(branch_name)

        # Check for conflicts first (best practice)
        conflict_response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}/conflicts",
            headers=author_headers,
        )

        assert conflict_response.status_code == 200
        conflict_data = conflict_response.json()
        assert conflict_data["has_conflicts"] is True

        # UI would show conflict warning to user here
        # User would need to resolve conflicts before publishing

    @pytest.mark.asyncio
    async def test_conflict_cleared_allows_publish(
        self,
        async_client: AsyncClient,
        setup_conflict_test_hierarchy,
        author_headers,
        reviewer_headers,
    ):
        """Should allow publish after conflict is resolved."""
        page = setup_conflict_test_hierarchy["page"]
        git_mock = setup_conflict_test_hierarchy["git_mock"]

        # Create and approve draft
        create_response = await async_client.post(
            f"/api/v1/content/pages/{page.id}/drafts",
            json={"title": f"Resolve and Publish {uuid4().hex[:8]}"},
            headers=author_headers,
        )
        draft_data = create_response.json()
        draft_id = draft_data["id"]
        branch_name = draft_data["branch_name"]

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={"comment": "OK"},
            headers=reviewer_headers,
        )

        # Simulate conflict
        git_mock._simulate_conflict(branch_name)

        # Verify conflict exists
        conflict_response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}/conflicts",
            headers=author_headers,
        )
        assert conflict_response.json()["has_conflicts"] is True

        # Simulate conflict resolution
        git_mock._clear_conflict(branch_name)

        # Verify conflict is cleared
        conflict_response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}/conflicts",
            headers=author_headers,
        )
        assert conflict_response.json()["has_conflicts"] is False

        # Now publish should succeed
        publish_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/publish",
            headers=author_headers,
        )
        assert publish_response.status_code == 200
        assert publish_response.json()["status"] == "published"
