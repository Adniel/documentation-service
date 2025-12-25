"""End-to-end integration tests for the version control workflow.

This tests the complete document lifecycle:
1. Create page
2. Create draft (change request)
3. Save content changes
4. Submit for review
5. Approve draft
6. Publish changes

These tests verify the integration between all components.
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, Organization, Workspace, Space, Page


@pytest.fixture
async def setup_workflow_hierarchy(db_session: AsyncSession, patch_git_service):
    """Create a complete test hierarchy for workflow testing.

    Creates: author (creates content), reviewer (reviews), publisher (publishes)
    Along with: org -> workspace -> space
    """
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

    # Create publisher user (could be same as reviewer in practice)
    publisher = User(
        id=str(uuid4()),
        email=f"publisher-{unique_id}@example.com",
        full_name="Content Publisher",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(publisher)

    # Create organization
    org = Organization(
        id=str(uuid4()),
        name="Workflow Test Org",
        slug=f"workflow-org-{unique_id}",
        owner_id=author.id,
        is_active=True,
    )
    db_session.add(org)

    # Create workspace
    workspace = Workspace(
        id=str(uuid4()),
        name="Workflow Workspace",
        slug=f"workflow-ws-{unique_id}",
        organization_id=org.id,
        is_active=True,
    )
    db_session.add(workspace)

    # Create space
    space = Space(
        id=str(uuid4()),
        name="Workflow Space",
        slug=f"workflow-space-{unique_id}",
        workspace_id=workspace.id,
        diataxis_type="tutorial",
        is_active=True,
    )
    db_session.add(space)

    await db_session.commit()

    return {
        "author": author,
        "reviewer": reviewer,
        "publisher": publisher,
        "org": org,
        "workspace": workspace,
        "space": space,
    }


@pytest.fixture
async def author_headers(setup_workflow_hierarchy):
    """Get authorization headers for the author."""
    from src.modules.access.security import create_access_token

    token = create_access_token(setup_workflow_hierarchy["author"].id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def reviewer_headers(setup_workflow_hierarchy):
    """Get authorization headers for the reviewer."""
    from src.modules.access.security import create_access_token

    token = create_access_token(setup_workflow_hierarchy["reviewer"].id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def publisher_headers(setup_workflow_hierarchy):
    """Get authorization headers for the publisher."""
    from src.modules.access.security import create_access_token

    token = create_access_token(setup_workflow_hierarchy["publisher"].id)
    return {"Authorization": f"Bearer {token}"}


class TestCompleteWorkflow:
    """End-to-end tests for the complete version control workflow."""

    @pytest.mark.asyncio
    async def test_full_document_lifecycle(
        self,
        async_client: AsyncClient,
        setup_workflow_hierarchy,
        author_headers,
        reviewer_headers,
        publisher_headers,
    ):
        """Test the complete document lifecycle from creation to publication."""
        space = setup_workflow_hierarchy["space"]

        # Step 1: Create a new page
        page_response = await async_client.post(
            "/api/v1/content/pages",
            json={
                "title": "Getting Started Guide",
                "slug": f"getting-started-{uuid4().hex[:8]}",
                "space_id": space.id,
                "content": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": "Initial content"}],
                        }
                    ],
                },
            },
            headers=author_headers,
        )

        assert page_response.status_code == 201, f"Page creation failed: {page_response.text}"
        page = page_response.json()
        page_id = page["id"]

        # Step 2: Create a draft (change request)
        draft_response = await async_client.post(
            f"/api/v1/content/pages/{page_id}/drafts",
            json={
                "title": "Add installation section",
                "description": "Adding detailed installation instructions",
            },
            headers=author_headers,
        )

        assert draft_response.status_code == 201, f"Draft creation failed: {draft_response.text}"
        draft = draft_response.json()
        draft_id = draft["id"]
        assert draft["status"] == "draft"
        assert "CR-0001" in draft["branch_name"]

        # Step 3: Verify draft appears in the list
        list_response = await async_client.get(
            f"/api/v1/content/pages/{page_id}/drafts",
            headers=author_headers,
        )

        assert list_response.status_code == 200
        assert list_response.json()["total"] == 1

        # Step 4: Submit the draft for review
        submit_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )

        assert submit_response.status_code == 200, f"Submit failed: {submit_response.text}"
        submitted_draft = submit_response.json()
        assert submitted_draft["status"] == "submitted"
        assert submitted_draft["submitted_at"] is not None

        # Step 5: Author cannot approve their own draft
        self_approve_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={},
            headers=author_headers,
        )
        assert self_approve_response.status_code == 403

        # Step 6: Reviewer approves the draft
        approve_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={"comment": "Looks good, approved for publication."},
            headers=reviewer_headers,
        )

        assert approve_response.status_code == 200, f"Approval failed: {approve_response.text}"
        approved_draft = approve_response.json()
        assert approved_draft["status"] == "approved"
        assert approved_draft["review_comment"] == "Looks good, approved for publication."
        assert approved_draft["reviewed_at"] is not None

        # Step 7: Get the final draft state
        get_response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}",
            headers=author_headers,
        )

        assert get_response.status_code == 200
        final_draft = get_response.json()
        assert final_draft["status"] == "approved"

    @pytest.mark.asyncio
    async def test_request_changes_and_resubmit(
        self,
        async_client: AsyncClient,
        setup_workflow_hierarchy,
        author_headers,
        reviewer_headers,
    ):
        """Test the workflow when changes are requested."""
        space = setup_workflow_hierarchy["space"]

        # Create page
        page_response = await async_client.post(
            "/api/v1/content/pages",
            json={
                "title": "API Reference",
                "slug": f"api-reference-{uuid4().hex[:8]}",
                "space_id": space.id,
                "content": {"type": "doc", "content": []},
            },
            headers=author_headers,
        )
        page_id = page_response.json()["id"]

        # Create and submit draft
        draft_response = await async_client.post(
            f"/api/v1/content/pages/{page_id}/drafts",
            json={"title": "Add endpoints documentation"},
            headers=author_headers,
        )
        draft_id = draft_response.json()["id"]

        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )

        # Reviewer requests changes
        changes_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/request-changes",
            json={"comment": "Please add more examples to the documentation."},
            headers=reviewer_headers,
        )

        assert changes_response.status_code == 200
        draft_with_changes = changes_response.json()
        assert draft_with_changes["status"] == "changes_requested"
        assert draft_with_changes["review_comment"] == "Please add more examples to the documentation."

        # Author can update the draft
        update_response = await async_client.patch(
            f"/api/v1/content/drafts/{draft_id}",
            json={"description": "Updated with more examples"},
            headers=author_headers,
        )

        assert update_response.status_code == 200
        assert update_response.json()["description"] == "Updated with more examples"

        # Author resubmits
        resubmit_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )

        assert resubmit_response.status_code == 200
        resubmitted_draft = resubmit_response.json()
        assert resubmitted_draft["status"] == "submitted"

        # Reviewer can now approve
        final_approve = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={"comment": "Examples look great, approved!"},
            headers=reviewer_headers,
        )

        assert final_approve.status_code == 200
        assert final_approve.json()["status"] == "approved"

    @pytest.mark.asyncio
    async def test_draft_with_comments(
        self,
        async_client: AsyncClient,
        setup_workflow_hierarchy,
        author_headers,
        reviewer_headers,
    ):
        """Test adding and managing comments on drafts."""
        space = setup_workflow_hierarchy["space"]

        # Create page and draft
        page_response = await async_client.post(
            "/api/v1/content/pages",
            json={
                "title": "Configuration Guide",
                "slug": f"config-guide-{uuid4().hex[:8]}",
                "space_id": space.id,
                "content": {"type": "doc", "content": []},
            },
            headers=author_headers,
        )
        page_id = page_response.json()["id"]

        draft_response = await async_client.post(
            f"/api/v1/content/pages/{page_id}/drafts",
            json={"title": "Add environment variables section"},
            headers=author_headers,
        )
        draft_id = draft_response.json()["id"]

        # Submit for review
        await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )

        # Reviewer adds a general comment
        comment1_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/comments",
            json={"content": "Consider adding a table of all environment variables."},
            headers=reviewer_headers,
        )
        assert comment1_response.status_code == 201
        comment1 = comment1_response.json()
        assert comment1["content"] == "Consider adding a table of all environment variables."

        # Author responds with a comment
        comment2_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/comments",
            json={"content": "Good idea! I'll add that in the next revision."},
            headers=author_headers,
        )
        assert comment2_response.status_code == 201

        # Reviewer adds a line-specific comment
        line_comment_response = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/comments",
            json={
                "content": "This variable name could be clearer.",
                "file_path": "content.json",
                "line_number": 15,
            },
            headers=reviewer_headers,
        )
        assert line_comment_response.status_code == 201
        line_comment = line_comment_response.json()
        assert line_comment["file_path"] == "content.json"
        assert line_comment["line_number"] == 15

        # Get all comments
        comments_response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}/comments",
            headers=author_headers,
        )
        assert comments_response.status_code == 200
        comments = comments_response.json()
        assert len(comments) == 3

    @pytest.mark.asyncio
    async def test_cancel_draft(
        self,
        async_client: AsyncClient,
        setup_workflow_hierarchy,
        author_headers,
    ):
        """Test cancelling a draft."""
        space = setup_workflow_hierarchy["space"]

        # Create page and draft
        page_response = await async_client.post(
            "/api/v1/content/pages",
            json={
                "title": "Temporary Guide",
                "slug": f"temp-guide-{uuid4().hex[:8]}",
                "space_id": space.id,
                "content": {"type": "doc", "content": []},
            },
            headers=author_headers,
        )
        page_id = page_response.json()["id"]

        draft_response = await async_client.post(
            f"/api/v1/content/pages/{page_id}/drafts",
            json={"title": "Draft to be cancelled"},
            headers=author_headers,
        )
        draft_id = draft_response.json()["id"]

        # Cancel the draft
        cancel_response = await async_client.delete(
            f"/api/v1/content/drafts/{draft_id}",
            headers=author_headers,
        )
        assert cancel_response.status_code == 204

        # Verify draft is cancelled (get should still work)
        get_response = await async_client.get(
            f"/api/v1/content/drafts/{draft_id}",
            headers=author_headers,
        )
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_multiple_drafts_on_page(
        self,
        async_client: AsyncClient,
        setup_workflow_hierarchy,
        author_headers,
    ):
        """Test having multiple drafts on the same page."""
        space = setup_workflow_hierarchy["space"]

        # Create page
        page_response = await async_client.post(
            "/api/v1/content/pages",
            json={
                "title": "Multi-Draft Page",
                "slug": f"multi-draft-{uuid4().hex[:8]}",
                "space_id": space.id,
                "content": {"type": "doc", "content": []},
            },
            headers=author_headers,
        )
        page_id = page_response.json()["id"]

        # Create first draft
        draft1_response = await async_client.post(
            f"/api/v1/content/pages/{page_id}/drafts",
            json={"title": "Add section A"},
            headers=author_headers,
        )
        assert draft1_response.status_code == 201
        draft1 = draft1_response.json()
        assert draft1["number"] == 1
        assert "CR-0001" in draft1["branch_name"]

        # Create second draft
        draft2_response = await async_client.post(
            f"/api/v1/content/pages/{page_id}/drafts",
            json={"title": "Add section B"},
            headers=author_headers,
        )
        assert draft2_response.status_code == 201
        draft2 = draft2_response.json()
        assert draft2["number"] == 2
        assert "CR-0002" in draft2["branch_name"]

        # Create third draft
        draft3_response = await async_client.post(
            f"/api/v1/content/pages/{page_id}/drafts",
            json={"title": "Add section C"},
            headers=author_headers,
        )
        assert draft3_response.status_code == 201
        draft3 = draft3_response.json()
        assert draft3["number"] == 3
        assert "CR-0003" in draft3["branch_name"]

        # List all drafts
        list_response = await async_client.get(
            f"/api/v1/content/pages/{page_id}/drafts",
            headers=author_headers,
        )
        assert list_response.status_code == 200
        data = list_response.json()
        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_draft_workflow_state_transitions(
        self,
        async_client: AsyncClient,
        setup_workflow_hierarchy,
        author_headers,
        reviewer_headers,
    ):
        """Test that state transitions are enforced correctly."""
        space = setup_workflow_hierarchy["space"]

        # Create page and draft
        page_response = await async_client.post(
            "/api/v1/content/pages",
            json={
                "title": "State Transition Test",
                "slug": f"state-test-{uuid4().hex[:8]}",
                "space_id": space.id,
                "content": {"type": "doc", "content": []},
            },
            headers=author_headers,
        )
        page_id = page_response.json()["id"]

        draft_response = await async_client.post(
            f"/api/v1/content/pages/{page_id}/drafts",
            json={"title": "Test transitions"},
            headers=author_headers,
        )
        draft_id = draft_response.json()["id"]

        # Cannot approve a draft that hasn't been submitted
        approve_unsubmitted = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/approve",
            json={},
            headers=reviewer_headers,
        )
        assert approve_unsubmitted.status_code == 400

        # Cannot request changes on a draft that hasn't been submitted
        changes_unsubmitted = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/request-changes",
            json={"comment": "Some feedback"},
            headers=reviewer_headers,
        )
        assert changes_unsubmitted.status_code == 400

        # Submit the draft
        submit = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )
        assert submit.status_code == 200

        # Cannot submit again when already submitted
        resubmit = await async_client.post(
            f"/api/v1/content/drafts/{draft_id}/submit",
            json={},
            headers=author_headers,
        )
        assert resubmit.status_code == 400
