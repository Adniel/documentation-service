"""Integration tests for Document Control API (Sprint 6).

Tests document control endpoints for ISO 9001/13485 compliance.

Compliance: ISO 9001 §7.5.2, ISO 13485 §4.2.4-5, ISO 15489
"""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, Organization, Workspace, Space, Page
from src.db.models.page import PageStatus
from src.db.models.approval import ApprovalMatrix


@pytest.fixture
async def setup_document_control(db_session: AsyncSession, patch_git_service):
    """Create test hierarchy for document control tests.

    Creates: org -> workspace -> space -> controlled page
    """
    from src.modules.access.security import hash_password

    unique_id = uuid4().hex[:8]

    # Create admin user
    admin = User(
        id=str(uuid4()),
        email=f"admin-{unique_id}@example.com",
        full_name="Test Admin",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
        is_superuser=True,
    )
    db_session.add(admin)

    # Create regular user
    user = User(
        id=str(uuid4()),
        email=f"user-{unique_id}@example.com",
        full_name="Test User",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(user)

    # Create approver user
    approver = User(
        id=str(uuid4()),
        email=f"approver-{unique_id}@example.com",
        full_name="Test Approver",
        hashed_password=hash_password("password123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(approver)

    # Create organization
    org = Organization(
        id=str(uuid4()),
        name="Test Org",
        slug=f"test-org-{unique_id}",
        owner_id=admin.id,
        is_active=True,
    )
    db_session.add(org)

    # Link users to organization
    admin.organization_id = org.id
    user.organization_id = org.id
    approver.organization_id = org.id

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
        diataxis_type="how-to",
        is_active=True,
    )
    db_session.add(space)

    # Create a draft page (for document number tests)
    draft_page = Page(
        id=str(uuid4()),
        title="Draft Document",
        slug=f"draft-doc-{unique_id}",
        space_id=space.id,
        author_id=user.id,
        content={"type": "doc", "content": []},
        version="1.0",
        status=PageStatus.DRAFT.value,
        git_commit_sha="abc123def456789012345678901234567890abcd",
        is_active=True,
    )
    db_session.add(draft_page)

    # Create an effective page (for revision tests)
    effective_page = Page(
        id=str(uuid4()),
        title="Effective Document",
        slug=f"effective-doc-{unique_id}",
        space_id=space.id,
        author_id=user.id,
        owner_id=user.id,
        content={"type": "doc", "content": []},
        version="1.0",
        revision="A",
        major_version=1,
        minor_version=0,
        status=PageStatus.EFFECTIVE.value,
        document_number=f"SOP-{unique_id}",
        document_type="sop",
        is_controlled=True,
        effective_date=datetime.now(timezone.utc) - timedelta(days=30),
        review_cycle_months=12,
        next_review_date=datetime.now(timezone.utc) + timedelta(days=335),
        git_commit_sha="def456abc789012345678901234567890abcd1234",
        is_active=True,
    )
    db_session.add(effective_page)

    # Create an approved page (for status transition tests)
    approved_page = Page(
        id=str(uuid4()),
        title="Approved Document",
        slug=f"approved-doc-{unique_id}",
        space_id=space.id,
        author_id=user.id,
        owner_id=user.id,
        content={"type": "doc", "content": []},
        version="1.0",
        revision="A",
        major_version=1,
        minor_version=0,
        status=PageStatus.APPROVED.value,
        document_number=f"WI-{unique_id}",
        document_type="wi",
        is_controlled=True,
        approved_date=datetime.now(timezone.utc),
        approved_by_id=approver.id,
        git_commit_sha="ghi789jkl012345678901234567890abcd5678",
        is_active=True,
    )
    db_session.add(approved_page)

    await db_session.commit()

    return {
        "admin": admin,
        "user": user,
        "approver": approver,
        "org": org,
        "workspace": workspace,
        "space": space,
        "draft_page": draft_page,
        "effective_page": effective_page,
        "approved_page": approved_page,
    }


@pytest.fixture
async def admin_headers(setup_document_control):
    """Get authorization headers for the admin user."""
    from src.modules.access.security import create_access_token

    admin = setup_document_control["admin"]
    token = create_access_token(admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def user_headers(setup_document_control):
    """Get authorization headers for the regular user."""
    from src.modules.access.security import create_access_token

    user = setup_document_control["user"]
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def approver_headers(setup_document_control):
    """Get authorization headers for the approver user."""
    from src.modules.access.security import create_access_token

    approver = setup_document_control["approver"]
    token = create_access_token(approver.id)
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Document Number Tests
# ============================================================================


class TestDocumentNumberGeneration:
    """Tests for document number generation endpoints."""

    @pytest.mark.asyncio
    async def test_generate_document_number_success(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should generate a unique document number for a page."""
        page = setup_document_control["draft_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/number",
            json={"document_type": "sop"},
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "document_number" in data
        assert "SOP" in data["document_number"]
        assert data["document_type"] == "sop"

    @pytest.mark.asyncio
    async def test_generate_document_number_with_custom_prefix(
        self, async_client: AsyncClient, setup_document_control, user_headers, db_session
    ):
        """Should support custom prefix for document numbers."""
        # Create a new page for this test
        unique_id = uuid4().hex[:8]
        page = Page(
            id=str(uuid4()),
            title="Custom Prefix Doc",
            slug=f"custom-prefix-{unique_id}",
            space_id=setup_document_control["space"].id,
            author_id=setup_document_control["user"].id,
            content={"type": "doc", "content": []},
            version="1.0",
            status=PageStatus.DRAFT.value,
            git_commit_sha="xyz123abc456789012345678901234567890abcd",
            is_active=True,
        )
        db_session.add(page)
        await db_session.commit()

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/number",
            json={"document_type": "sop", "custom_prefix": "QA-SOP"},
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "QA-SOP" in data["document_number"]

    @pytest.mark.asyncio
    async def test_cannot_assign_number_twice(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should not allow assigning document number to already numbered page."""
        page = setup_document_control["effective_page"]  # Already has document_number

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/number",
            json={"document_type": "sop"},
            headers=user_headers,
        )

        assert response.status_code == 400
        assert "already has a number" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_generate_number_page_not_found(
        self, async_client: AsyncClient, user_headers
    ):
        """Should return 404 for non-existent page."""
        fake_id = str(uuid4())

        response = await async_client.post(
            f"/api/v1/document-control/pages/{fake_id}/number",
            json={"document_type": "sop"},
            headers=user_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_number_sequences(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should list document number sequences."""
        # First generate a number to create a sequence
        page = setup_document_control["draft_page"]
        await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/number",
            json={"document_type": "form"},
            headers=user_headers,
        )

        response = await async_client.get(
            "/api/v1/document-control/sequences",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "sequences" in data
        # Should have at least the sequence we just created
        assert len(data["sequences"]) >= 1


# ============================================================================
# Revision Tests
# ============================================================================


class TestRevisionCreation:
    """Tests for revision creation endpoints."""

    @pytest.mark.asyncio
    async def test_create_major_revision(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should create a major revision with change request."""
        page = setup_document_control["effective_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/revise",
            json={
                "is_major": True,
                "change_reason": "Major regulatory update required for compliance",
                "title": "Regulatory Update",
            },
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "change_request_id" in data
        assert data["is_major"] is True
        assert data["pending_revision"] == "B"  # A -> B

    @pytest.mark.asyncio
    async def test_create_minor_revision(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should create a minor revision with change request."""
        page = setup_document_control["effective_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/revise",
            json={
                "is_major": False,
                "change_reason": "Minor clarification to section 3.2",
                "title": "Clarification Update",
            },
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "change_request_id" in data
        assert data["is_major"] is False
        assert data["pending_version"] == "1.1"  # 1.0 -> 1.1

    @pytest.mark.asyncio
    async def test_cannot_revise_non_effective_document(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should not allow revision of non-effective documents."""
        page = setup_document_control["draft_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/revise",
            json={
                "is_major": True,
                "change_reason": "This should fail because document is draft",
            },
            headers=user_headers,
        )

        assert response.status_code == 400
        assert "effective" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_revision_requires_reason(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should require change reason for revisions."""
        page = setup_document_control["effective_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/revise",
            json={
                "is_major": True,
                "change_reason": "short",  # Too short (min 10 chars)
            },
            headers=user_headers,
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_revision_history(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should return revision history for a document."""
        page = setup_document_control["effective_page"]

        response = await async_client.get(
            f"/api/v1/document-control/pages/{page.id}/revisions",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page_id"] == page.id
        assert data["current_revision"] == "A"
        assert "revisions" in data


# ============================================================================
# Status Transition Tests
# ============================================================================


class TestStatusTransitions:
    """Tests for document status transition endpoints."""

    @pytest.mark.asyncio
    async def test_transition_approved_to_effective(
        self, async_client: AsyncClient, setup_document_control, approver_headers
    ):
        """Should transition approved document to effective."""
        page = setup_document_control["approved_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/status",
            json={
                "to_status": "effective",
                "effective_date": datetime.now(timezone.utc).isoformat(),
            },
            headers=approver_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["previous_status"] == "approved"
        assert data["new_status"] == "effective"

    @pytest.mark.asyncio
    async def test_transition_effective_to_obsolete(
        self, async_client: AsyncClient, setup_document_control, approver_headers
    ):
        """Should transition effective document to obsolete."""
        page = setup_document_control["effective_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/status",
            json={
                "to_status": "obsolete",
                "reason": "Superseded by new version",
            },
            headers=approver_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["previous_status"] == "effective"
        assert data["new_status"] == "obsolete"

    @pytest.mark.asyncio
    async def test_invalid_transition_blocked(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should block invalid status transitions."""
        page = setup_document_control["draft_page"]

        # Try to go directly from draft to effective (should fail)
        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/status",
            json={"to_status": "effective"},
            headers=user_headers,
        )

        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalid_status_value(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should reject invalid status values."""
        page = setup_document_control["draft_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/status",
            json={"to_status": "invalid_status"},
            headers=user_headers,
        )

        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_list_statuses(
        self, async_client: AsyncClient, user_headers
    ):
        """Should list all available statuses."""
        response = await async_client.get(
            "/api/v1/document-control/statuses",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "statuses" in data
        status_names = [s["name"] for s in data["statuses"]]
        assert "draft" in status_names
        assert "in_review" in status_names
        assert "approved" in status_names
        assert "effective" in status_names
        assert "obsolete" in status_names


# ============================================================================
# Metadata Tests
# ============================================================================


class TestMetadataManagement:
    """Tests for document metadata endpoints."""

    @pytest.mark.asyncio
    async def test_get_metadata(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should return document metadata."""
        page = setup_document_control["effective_page"]

        response = await async_client.get(
            f"/api/v1/document-control/pages/{page.id}/metadata",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page_id"] == page.id
        assert "metadata" in data
        assert data["metadata"]["document_number"] is not None
        assert "SOP-" in data["metadata"]["document_number"]
        assert data["metadata"]["status"] == "effective"

    @pytest.mark.asyncio
    async def test_update_review_schedule(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should update document review schedule."""
        page = setup_document_control["effective_page"]

        response = await async_client.patch(
            f"/api/v1/document-control/pages/{page.id}/metadata",
            json={"review_cycle_months": 6},
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["review_cycle_months"] == 6

    @pytest.mark.asyncio
    async def test_update_training_requirement(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should update training requirements."""
        page = setup_document_control["effective_page"]

        response = await async_client.patch(
            f"/api/v1/document-control/pages/{page.id}/metadata",
            json={
                "requires_training": True,
                "training_validity_months": 24,
            },
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["requires_training"] is True
        assert data["metadata"]["training_validity_months"] == 24


# ============================================================================
# Review Tests
# ============================================================================


class TestPeriodicReview:
    """Tests for periodic review endpoints."""

    @pytest.mark.asyncio
    async def test_get_documents_due_for_review(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should list documents due for review."""
        response = await async_client.get(
            "/api/v1/document-control/review-due",
            params={"days_ahead": 365, "include_overdue": True},
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "overdue_count" in data
        assert "documents" in data

    @pytest.mark.asyncio
    async def test_complete_review(
        self, async_client: AsyncClient, setup_document_control, user_headers, db_session
    ):
        """Should complete a periodic review."""
        # Create a page due for review
        unique_id = uuid4().hex[:8]
        review_page = Page(
            id=str(uuid4()),
            title="Review Due Document",
            slug=f"review-due-{unique_id}",
            space_id=setup_document_control["space"].id,
            author_id=setup_document_control["user"].id,
            owner_id=setup_document_control["user"].id,
            content={"type": "doc", "content": []},
            version="1.0",
            status=PageStatus.EFFECTIVE.value,
            document_number=f"REVIEW-{uuid4().hex[:8]}",
            is_controlled=True,
            review_cycle_months=12,
            next_review_date=datetime.now(timezone.utc) - timedelta(days=5),  # Overdue
            git_commit_sha="review123abc456789012345678901234567890ab",
            is_active=True,
        )
        db_session.add(review_page)
        await db_session.commit()

        response = await async_client.post(
            f"/api/v1/document-control/pages/{review_page.id}/complete-review",
            json={},
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "reviewed_at" in data
        assert "next_review_date" in data

    @pytest.mark.asyncio
    async def test_complete_review_non_effective_fails(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should not allow completing review for non-effective documents."""
        page = setup_document_control["draft_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/complete-review",
            json={},
            headers=user_headers,
        )

        assert response.status_code == 400
        assert "effective" in response.json()["detail"].lower()


# ============================================================================
# Retention Policy Tests
# ============================================================================


class TestRetentionPolicies:
    """Tests for retention policy endpoints."""

    @pytest.mark.asyncio
    async def test_create_retention_policy(
        self, async_client: AsyncClient, setup_document_control, admin_headers
    ):
        """Admin should be able to create retention policy."""
        response = await async_client.post(
            "/api/v1/document-control/retention-policies",
            json={
                "name": "Standard Retention",
                "description": "Standard 7-year retention for quality records",
                "retention_years": 7,
                "disposition_method": "archive",
                "applicable_document_types": ["sop", "wi"],
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Standard Retention"

    @pytest.mark.asyncio
    async def test_create_retention_policy_requires_admin(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Non-admin should not be able to create retention policy."""
        response = await async_client.post(
            "/api/v1/document-control/retention-policies",
            json={
                "name": "Should Fail",
                "retention_years": 5,
                "disposition_method": "archive",
            },
            headers=user_headers,
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_retention_policies(
        self, async_client: AsyncClient, setup_document_control, admin_headers, user_headers
    ):
        """Should list retention policies."""
        # Create a policy first
        await async_client.post(
            "/api/v1/document-control/retention-policies",
            json={
                "name": "Listable Policy",
                "retention_years": 5,
                "disposition_method": "archive",
            },
            headers=admin_headers,
        )

        response = await async_client.get(
            "/api/v1/document-control/retention-policies",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "policies" in data
        assert len(data["policies"]) >= 1

    @pytest.mark.asyncio
    async def test_get_documents_due_for_disposition(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Should list documents approaching disposition."""
        response = await async_client.get(
            "/api/v1/document-control/retention-due",
            params={"days_ahead": 365},
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "documents" in data


# ============================================================================
# Approval Matrix Tests
# ============================================================================


class TestApprovalMatrices:
    """Tests for approval matrix endpoints."""

    @pytest.mark.asyncio
    async def test_create_approval_matrix(
        self, async_client: AsyncClient, setup_document_control, admin_headers
    ):
        """Admin should be able to create approval matrix."""
        approver = setup_document_control["approver"]

        response = await async_client.post(
            "/api/v1/document-control/approval-matrices",
            json={
                "name": "SOP Approval Matrix",
                "description": "Two-step approval for SOPs",
                "applicable_document_types": ["sop"],
                "steps": [
                    {
                        "order": 1,
                        "name": "Document Review",
                        "approver_type": "role",
                        "approver_value": "reviewer",
                    },
                    {
                        "order": 2,
                        "name": "Quality Approval",
                        "approver_type": "user",
                        "approver_value": str(approver.id),
                    },
                ],
                "require_sequential": True,
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "SOP Approval Matrix"

    @pytest.mark.asyncio
    async def test_create_approval_matrix_requires_admin(
        self, async_client: AsyncClient, setup_document_control, user_headers
    ):
        """Non-admin should not be able to create approval matrix."""
        response = await async_client.post(
            "/api/v1/document-control/approval-matrices",
            json={
                "name": "Should Fail",
                "steps": [{"order": 1, "name": "Step 1"}],
            },
            headers=user_headers,
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_approval_matrices(
        self, async_client: AsyncClient, setup_document_control, admin_headers, user_headers
    ):
        """Should list approval matrices."""
        # Create a matrix first
        await async_client.post(
            "/api/v1/document-control/approval-matrices",
            json={
                "name": "Listable Matrix",
                "steps": [{"order": 1, "name": "Review", "approver_type": "role", "approver_value": "reviewer"}],
            },
            headers=admin_headers,
        )

        response = await async_client.get(
            "/api/v1/document-control/approval-matrices",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "matrices" in data
        assert len(data["matrices"]) >= 1


# ============================================================================
# Approval Workflow Tests
# ============================================================================


class TestApprovalWorkflow:
    """Tests for approval workflow endpoints."""

    @pytest.fixture
    async def setup_approval_workflow(
        self, db_session: AsyncSession, setup_document_control
    ):
        """Set up a change request with approval workflow."""
        from src.db.models.change_request import ChangeRequest, ChangeRequestStatus

        org = setup_document_control["org"]
        user = setup_document_control["user"]
        approver = setup_document_control["approver"]
        page = setup_document_control["effective_page"]

        # Create approval matrix
        matrix = ApprovalMatrix(
            id=str(uuid4()),
            organization_id=org.id,
            name="Test Approval Matrix",
            steps=[
                {
                    "order": 1,
                    "name": "Quality Review",
                    "approver_type": "user",
                    "approver_value": str(approver.id),
                }
            ],
            require_sequential=True,
            is_active=True,
        )
        db_session.add(matrix)

        # Create change request with workflow
        cr = ChangeRequest(
            id=str(uuid4()),
            number=99,
            page_id=page.id,
            author_id=user.id,
            title="Test Change Request",
            description="Testing approval workflow",
            branch_name=f"draft/cr-99-{uuid4().hex[:8]}",
            base_commit_sha="abc123def456789012345678901234567890abcd",
            status=ChangeRequestStatus.SUBMITTED.value,
            submitted_at=datetime.now(timezone.utc),
            approval_matrix_id=matrix.id,
            current_approval_step=1,
            approval_status="pending",
        )
        db_session.add(cr)

        await db_session.commit()

        return {
            "matrix": matrix,
            "change_request": cr,
        }

    @pytest.mark.asyncio
    async def test_approve_change_request(
        self,
        async_client: AsyncClient,
        setup_document_control,
        setup_approval_workflow,
        approver_headers,
    ):
        """Approver should be able to approve change request."""
        cr = setup_approval_workflow["change_request"]

        response = await async_client.post(
            f"/api/v1/document-control/change-requests/{cr.id}/approve",
            json={
                "decision": "approved",
                "comment": "Approved after thorough review",
            },
            headers=approver_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["change_request_id"] == cr.id
        assert "approval_status" in data

    @pytest.mark.asyncio
    async def test_reject_change_request(
        self,
        async_client: AsyncClient,
        setup_document_control,
        setup_approval_workflow,
        approver_headers,
    ):
        """Approver should be able to reject change request."""
        cr = setup_approval_workflow["change_request"]

        response = await async_client.post(
            f"/api/v1/document-control/change-requests/{cr.id}/approve",
            json={
                "decision": "rejected",
                "comment": "Needs additional safety analysis",
            },
            headers=approver_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["change_request_id"] == cr.id

    @pytest.mark.asyncio
    async def test_get_workflow_status(
        self,
        async_client: AsyncClient,
        setup_document_control,
        setup_approval_workflow,
        user_headers,
    ):
        """Should return detailed workflow status."""
        cr = setup_approval_workflow["change_request"]

        response = await async_client.get(
            f"/api/v1/document-control/change-requests/{cr.id}/workflow-status",
            headers=user_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "change_request_id" in data
        assert "current_step" in data
        assert "steps" in data

    @pytest.mark.asyncio
    async def test_get_pending_approvals(
        self,
        async_client: AsyncClient,
        setup_document_control,
        setup_approval_workflow,
        approver_headers,
    ):
        """Should list change requests pending approval."""
        response = await async_client.get(
            "/api/v1/document-control/pending-approvals",
            headers=approver_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "change_requests" in data

    @pytest.mark.asyncio
    async def test_invalid_approval_decision(
        self,
        async_client: AsyncClient,
        setup_document_control,
        setup_approval_workflow,
        approver_headers,
    ):
        """Should reject invalid approval decisions."""
        cr = setup_approval_workflow["change_request"]

        response = await async_client.post(
            f"/api/v1/document-control/change-requests/{cr.id}/approve",
            json={"decision": "maybe"},
            headers=approver_headers,
        )

        assert response.status_code == 400
        assert "Invalid decision" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_workflow_status_not_found(
        self, async_client: AsyncClient, user_headers
    ):
        """Should return 404 for non-existent change request."""
        fake_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/document-control/change-requests/{fake_id}/workflow-status",
            headers=user_headers,
        )

        assert response.status_code == 404


# ============================================================================
# Authorization Tests
# ============================================================================


class TestAuthorization:
    """Tests for authorization requirements."""

    @pytest.mark.asyncio
    async def test_unauthenticated_request_rejected(
        self, async_client: AsyncClient, setup_document_control
    ):
        """Should reject unauthenticated requests."""
        page = setup_document_control["draft_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/number",
            json={"document_type": "sop"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(
        self, async_client: AsyncClient, setup_document_control
    ):
        """Should reject invalid tokens."""
        page = setup_document_control["draft_page"]

        response = await async_client.post(
            f"/api/v1/document-control/pages/{page.id}/number",
            json={"document_type": "sop"},
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == 401
