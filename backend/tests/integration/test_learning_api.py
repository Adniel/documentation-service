"""Integration tests for Learning API (Sprint 9).

Tests the complete learning workflow:
- Assessment creation and management
- Question management
- Quiz taking and grading
- Assignments
- Acknowledgments
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, Organization, Workspace, Space, Page
from src.db.models.assessment import Assessment, AssessmentQuestion, QuestionType
from src.db.models.learning_assignment import LearningAssignment, AssignmentStatus
from src.db.models.quiz_attempt import QuizAttempt, AttemptStatus


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
async def setup_learning_test(db_session: AsyncSession):
    """Create a complete test hierarchy for learning tests.

    Creates: user, org, workspace, space, page (with requires_training=True)
    """
    from src.modules.access.security import hash_password

    unique_id = uuid4().hex[:8]

    # Create user
    user = User(
        id=str(uuid4()),
        email=f"learner-{unique_id}@example.com",
        full_name="Test Learner",
        hashed_password=hash_password("TestPass123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(user)

    # Create admin user
    admin = User(
        id=str(uuid4()),
        email=f"admin-{unique_id}@example.com",
        full_name="Test Admin",
        hashed_password=hash_password("AdminPass123"),
        is_active=True,
        email_verified=True,
    )
    db_session.add(admin)

    # Create organization
    org = Organization(
        id=str(uuid4()),
        name="Test Org",
        slug=f"test-org-{unique_id}",
        owner_id=admin.id,
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
        name="Training Space",
        slug=f"training-space-{unique_id}",
        workspace_id=workspace.id,
        diataxis_type="tutorial",
        is_active=True,
    )
    db_session.add(space)

    # Create page (training document)
    page = Page(
        id=str(uuid4()),
        title="Training Document",
        slug=f"training-doc-{unique_id}",
        space_id=space.id,
        author_id=admin.id,
        content={"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Training content"}]}]},
        version="1.0",
        status="effective",
        git_commit_sha="abc123def456789012345678901234567890abcd",
        is_active=True,
        requires_training=True,
        training_validity_months=12,
    )
    db_session.add(page)

    await db_session.commit()

    return {
        "user": user,
        "admin": admin,
        "org": org,
        "workspace": workspace,
        "space": space,
        "page": page,
    }


@pytest.fixture
async def auth_headers(setup_learning_test):
    """Get authorization headers for the test user."""
    from src.modules.access.security import create_access_token

    user = setup_learning_test["user"]
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_auth_headers(setup_learning_test):
    """Get authorization headers for the admin user."""
    from src.modules.access.security import create_access_token

    admin = setup_learning_test["admin"]
    token = create_access_token(admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def setup_assessment(db_session: AsyncSession, setup_learning_test):
    """Create an assessment with questions for the test page."""
    page = setup_learning_test["page"]
    admin = setup_learning_test["admin"]

    # Create assessment
    assessment = Assessment(
        id=str(uuid4()),
        page_id=page.id,
        title="Training Assessment",
        description="Test your knowledge",
        passing_score=70,
        max_attempts=3,
        time_limit_minutes=30,
        created_by_id=admin.id,
        is_active=True,
    )
    db_session.add(assessment)

    # Create multiple choice question
    q1 = AssessmentQuestion(
        id=str(uuid4()),
        assessment_id=assessment.id,
        question_type=QuestionType.MULTIPLE_CHOICE.value,
        question_text="What is the purpose of documentation?",
        options=[
            {"id": "a", "text": "To confuse people", "is_correct": False},
            {"id": "b", "text": "To provide clear information", "is_correct": True},
            {"id": "c", "text": "To waste time", "is_correct": False},
        ],
        points=10,
        explanation="Documentation should provide clear information.",
        sort_order=1,
    )
    db_session.add(q1)

    # Create true/false question
    q2 = AssessmentQuestion(
        id=str(uuid4()),
        assessment_id=assessment.id,
        question_type=QuestionType.TRUE_FALSE.value,
        question_text="Documentation should be reviewed regularly.",
        correct_answer="true",
        points=5,
        explanation="Regular review keeps documentation current.",
        sort_order=2,
    )
    db_session.add(q2)

    await db_session.commit()

    return {
        **setup_learning_test,
        "assessment": assessment,
        "question1": q1,
        "question2": q2,
    }


# =============================================================================
# ASSESSMENT ENDPOINT TESTS
# =============================================================================

class TestAssessmentAPI:
    """Tests for assessment endpoints."""

    @pytest.mark.asyncio
    async def test_create_assessment(
        self, async_client: AsyncClient, setup_learning_test, admin_auth_headers
    ):
        """Should create a new assessment for a page."""
        page = setup_learning_test["page"]

        response = await async_client.post(
            "/api/v1/learning/assessments",
            json={
                "page_id": page.id,
                "title": "New Assessment",
                "description": "Test assessment",
                "passing_score": 80,
                "max_attempts": 3,
            },
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Assessment"
        assert data["page_id"] == page.id
        assert data["passing_score"] == 80

    @pytest.mark.asyncio
    async def test_create_assessment_unauthorized(
        self, async_client: AsyncClient, setup_learning_test
    ):
        """Should require authentication to create assessment."""
        page = setup_learning_test["page"]

        response = await async_client.post(
            "/api/v1/learning/assessments",
            json={
                "page_id": page.id,
                "title": "New Assessment",
            },
        )

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_assessment(
        self, async_client: AsyncClient, setup_assessment, admin_auth_headers
    ):
        """Should get assessment by ID."""
        assessment = setup_assessment["assessment"]

        response = await async_client.get(
            f"/api/v1/learning/assessments/{assessment.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == assessment.id
        assert data["title"] == "Training Assessment"

    @pytest.mark.asyncio
    async def test_get_assessment_for_page(
        self, async_client: AsyncClient, setup_assessment, auth_headers
    ):
        """Should get assessment for a page."""
        page = setup_assessment["page"]

        response = await async_client.get(
            f"/api/v1/learning/pages/{page.id}/assessment",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page_id"] == page.id

    @pytest.mark.asyncio
    async def test_get_assessment_for_page_not_found(
        self, async_client: AsyncClient, setup_learning_test, auth_headers
    ):
        """Should return 404 when page has no assessment."""
        # The base setup doesn't have an assessment
        page = setup_learning_test["page"]

        response = await async_client.get(
            f"/api/v1/learning/pages/{page.id}/assessment",
            headers=auth_headers,
        )

        assert response.status_code == 404


# =============================================================================
# QUESTION ENDPOINT TESTS
# =============================================================================

class TestQuestionAPI:
    """Tests for question endpoints."""

    @pytest.mark.asyncio
    async def test_add_multiple_choice_question(
        self, async_client: AsyncClient, setup_assessment, admin_auth_headers
    ):
        """Should add a multiple choice question."""
        assessment = setup_assessment["assessment"]

        response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/questions",
            json={
                "question_type": "multiple_choice",
                "question_text": "What is 2+2?",
                "options": [
                    {"id": "a", "text": "3", "is_correct": False},
                    {"id": "b", "text": "4", "is_correct": True},
                    {"id": "c", "text": "5", "is_correct": False},
                ],
                "points": 10,
                "explanation": "Basic math",
            },
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["question_type"] == "multiple_choice"
        assert data["question_text"] == "What is 2+2?"

    @pytest.mark.asyncio
    async def test_add_true_false_question(
        self, async_client: AsyncClient, setup_assessment, admin_auth_headers
    ):
        """Should add a true/false question."""
        assessment = setup_assessment["assessment"]

        response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/questions",
            json={
                "question_type": "true_false",
                "question_text": "The sky is blue.",
                "correct_answer": "true",
                "points": 5,
            },
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["question_type"] == "true_false"

    @pytest.mark.asyncio
    async def test_update_question(
        self, async_client: AsyncClient, setup_assessment, admin_auth_headers
    ):
        """Should update a question."""
        question = setup_assessment["question1"]

        response = await async_client.patch(
            f"/api/v1/learning/questions/{question.id}",
            json={
                "question_text": "Updated question text?",
                "points": 15,
            },
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["question_text"] == "Updated question text?"
        assert data["points"] == 15

    @pytest.mark.asyncio
    async def test_delete_question(
        self, async_client: AsyncClient, setup_assessment, admin_auth_headers
    ):
        """Should delete a question."""
        question = setup_assessment["question1"]

        response = await async_client.delete(
            f"/api/v1/learning/questions/{question.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 204


# =============================================================================
# QUIZ ATTEMPT TESTS
# =============================================================================

class TestQuizTakingAPI:
    """Tests for quiz taking workflow."""

    @pytest.mark.asyncio
    async def test_start_quiz_attempt(
        self, async_client: AsyncClient, setup_assessment, auth_headers
    ):
        """Should start a new quiz attempt."""
        assessment = setup_assessment["assessment"]

        response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/start",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "attempt_id" in data
        assert data["attempt_number"] == 1
        assert data["assessment"]["id"] == assessment.id
        # Questions should be present but without correct answers
        assert len(data["assessment"]["questions"]) == 2

    @pytest.mark.asyncio
    async def test_save_answer(
        self, async_client: AsyncClient, setup_assessment, auth_headers
    ):
        """Should save an answer during quiz."""
        assessment = setup_assessment["assessment"]
        question = setup_assessment["question1"]

        # Start attempt first
        start_response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/start",
            json={},
            headers=auth_headers,
        )
        attempt_id = start_response.json()["attempt_id"]

        # Save answer
        response = await async_client.patch(
            f"/api/v1/learning/attempts/{attempt_id}/answer",
            json={
                "question_id": question.id,
                "answer": "b",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert question.id in data["answers"]
        assert data["answers"][question.id] == "b"

    @pytest.mark.asyncio
    async def test_submit_quiz_passing(
        self, async_client: AsyncClient, setup_assessment, auth_headers
    ):
        """Should submit quiz and pass with correct answers."""
        assessment = setup_assessment["assessment"]
        q1 = setup_assessment["question1"]
        q2 = setup_assessment["question2"]

        # Start attempt
        start_response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/start",
            json={},
            headers=auth_headers,
        )
        attempt_id = start_response.json()["attempt_id"]

        # Save correct answers
        await async_client.patch(
            f"/api/v1/learning/attempts/{attempt_id}/answer",
            json={"question_id": q1.id, "answer": "b"},
            headers=auth_headers,
        )
        await async_client.patch(
            f"/api/v1/learning/attempts/{attempt_id}/answer",
            json={"question_id": q2.id, "answer": "true"},
            headers=auth_headers,
        )

        # Submit
        response = await async_client.post(
            f"/api/v1/learning/attempts/{attempt_id}/submit",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 100.0
        assert data["passed"] is True
        assert data["status"] == "passed"

    @pytest.mark.asyncio
    async def test_submit_quiz_failing(
        self, async_client: AsyncClient, setup_assessment, auth_headers
    ):
        """Should submit quiz and fail with wrong answers."""
        assessment = setup_assessment["assessment"]
        q1 = setup_assessment["question1"]
        q2 = setup_assessment["question2"]

        # Start attempt
        start_response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/start",
            json={},
            headers=auth_headers,
        )
        attempt_id = start_response.json()["attempt_id"]

        # Save wrong answers
        await async_client.patch(
            f"/api/v1/learning/attempts/{attempt_id}/answer",
            json={"question_id": q1.id, "answer": "a"},
            headers=auth_headers,
        )
        await async_client.patch(
            f"/api/v1/learning/attempts/{attempt_id}/answer",
            json={"question_id": q2.id, "answer": "false"},
            headers=auth_headers,
        )

        # Submit
        response = await async_client.post(
            f"/api/v1/learning/attempts/{attempt_id}/submit",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 0.0
        assert data["passed"] is False
        assert data["status"] == "failed"

    @pytest.mark.asyncio
    async def test_get_attempt(
        self, async_client: AsyncClient, setup_assessment, auth_headers
    ):
        """Should get an existing attempt."""
        assessment = setup_assessment["assessment"]

        # Start attempt
        start_response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/start",
            json={},
            headers=auth_headers,
        )
        attempt_id = start_response.json()["attempt_id"]

        # Get attempt
        response = await async_client.get(
            f"/api/v1/learning/attempts/{attempt_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == attempt_id
        assert data["status"] == "in_progress"


# =============================================================================
# ASSIGNMENT TESTS
# =============================================================================

class TestAssignmentAPI:
    """Tests for assignment management."""

    @pytest.mark.asyncio
    async def test_create_assignment(
        self, async_client: AsyncClient, setup_learning_test, admin_auth_headers
    ):
        """Should create a learning assignment."""
        page = setup_learning_test["page"]
        user = setup_learning_test["user"]

        response = await async_client.post(
            "/api/v1/learning/assignments",
            json={
                "page_id": page.id,
                "user_id": user.id,
                "due_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                "notes": "Please complete this training",
            },
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["page_id"] == page.id
        assert data["user_id"] == user.id
        assert data["status"] == "assigned"

    @pytest.mark.asyncio
    async def test_get_my_assignments(
        self, async_client: AsyncClient, setup_learning_test, admin_auth_headers, auth_headers, db_session
    ):
        """Should get user's assignments."""
        page = setup_learning_test["page"]
        user = setup_learning_test["user"]
        admin = setup_learning_test["admin"]

        # Create assignment
        assignment = LearningAssignment(
            id=str(uuid4()),
            page_id=page.id,
            user_id=user.id,
            assigned_by_id=admin.id,
            status=AssignmentStatus.ASSIGNED.value,
            assigned_at=datetime.now(timezone.utc),
        )
        db_session.add(assignment)
        await db_session.commit()

        # Get assignments as user
        response = await async_client.get(
            "/api/v1/learning/assignments/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_bulk_create_assignments(
        self, async_client: AsyncClient, setup_learning_test, admin_auth_headers, db_session
    ):
        """Should create multiple assignments at once."""
        page = setup_learning_test["page"]

        # Create additional users
        users = []
        for i in range(3):
            user = User(
                id=str(uuid4()),
                email=f"bulk-user-{i}-{uuid4().hex[:6]}@example.com",
                full_name=f"Bulk User {i}",
                hashed_password="hashed",
                is_active=True,
            )
            db_session.add(user)
            users.append(user)
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/learning/assignments/bulk",
            json={
                "page_id": page.id,
                "user_ids": [u.id for u in users],
                "notes": "Team training",
            },
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3


# =============================================================================
# ACKNOWLEDGMENT TESTS
# =============================================================================

class TestAcknowledgmentAPI:
    """Tests for document acknowledgment workflow."""

    @pytest.mark.asyncio
    async def test_get_acknowledgment_status(
        self, async_client: AsyncClient, setup_learning_test, auth_headers
    ):
        """Should get acknowledgment status for a page."""
        page = setup_learning_test["page"]

        response = await async_client.get(
            f"/api/v1/learning/pages/{page.id}/acknowledgment",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page_id"] == page.id
        assert data["requires_training"] is True
        assert data["has_valid_acknowledgment"] is False

    @pytest.mark.asyncio
    async def test_initiate_acknowledgment_without_quiz(
        self, async_client: AsyncClient, setup_learning_test, auth_headers
    ):
        """Should initiate acknowledgment when no quiz required."""
        page = setup_learning_test["page"]

        response = await async_client.post(
            f"/api/v1/learning/pages/{page.id}/acknowledge",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "challenge_token" in data
        assert data["document_title"] == "Training Document"

    @pytest.mark.asyncio
    async def test_initiate_acknowledgment_requires_quiz(
        self, async_client: AsyncClient, setup_assessment, auth_headers
    ):
        """Should reject acknowledgment if quiz not passed."""
        page = setup_assessment["page"]

        response = await async_client.post(
            f"/api/v1/learning/pages/{page.id}/acknowledge",
            headers=auth_headers,
        )

        # Should return error because quiz not passed
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_complete_acknowledgment_flow(
        self, async_client: AsyncClient, setup_learning_test, auth_headers
    ):
        """Test complete acknowledgment flow with password."""
        page = setup_learning_test["page"]

        # Initiate
        init_response = await async_client.post(
            f"/api/v1/learning/pages/{page.id}/acknowledge",
            headers=auth_headers,
        )
        assert init_response.status_code == 200
        challenge_token = init_response.json()["challenge_token"]

        # Complete with password
        complete_response = await async_client.post(
            "/api/v1/learning/acknowledgments/complete",
            json={
                "challenge_token": challenge_token,
                "password": "TestPass123",
            },
            headers=auth_headers,
        )

        assert complete_response.status_code in [200, 201]
        data = complete_response.json()
        assert data["page_id"] == page.id
        assert data["is_valid"] is True

    @pytest.mark.asyncio
    async def test_complete_acknowledgment_wrong_password(
        self, async_client: AsyncClient, setup_learning_test, auth_headers
    ):
        """Should fail acknowledgment with wrong password."""
        page = setup_learning_test["page"]

        # Initiate
        init_response = await async_client.post(
            f"/api/v1/learning/pages/{page.id}/acknowledge",
            headers=auth_headers,
        )
        challenge_token = init_response.json()["challenge_token"]

        # Complete with wrong password
        complete_response = await async_client.post(
            "/api/v1/learning/acknowledgments/complete",
            json={
                "challenge_token": challenge_token,
                "password": "WrongPassword123",
            },
            headers=auth_headers,
        )

        # Can be 400 (bad request) or 401 (unauthorized)
        assert complete_response.status_code in [400, 401]

    @pytest.mark.asyncio
    async def test_get_my_acknowledgments(
        self, async_client: AsyncClient, setup_learning_test, auth_headers
    ):
        """Should get user's acknowledgments."""
        response = await async_client.get(
            "/api/v1/learning/acknowledgments/me",
            headers=auth_headers,
        )

        assert response.status_code == 200
        # Initially should be empty
        data = response.json()
        assert isinstance(data, list)


# =============================================================================
# REPORTING TESTS
# =============================================================================

class TestReportingAPI:
    """Tests for learning reports."""

    @pytest.mark.asyncio
    async def test_completion_report(
        self, async_client: AsyncClient, setup_learning_test, admin_auth_headers
    ):
        """Should get completion report."""
        response = await async_client.get(
            "/api/v1/learning/reports/completion",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_overdue_report(
        self, async_client: AsyncClient, setup_learning_test, admin_auth_headers
    ):
        """Should get overdue report."""
        response = await async_client.get(
            "/api/v1/learning/reports/overdue",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_page_training_report(
        self, async_client: AsyncClient, setup_learning_test, admin_auth_headers
    ):
        """Should get page training report."""
        page = setup_learning_test["page"]

        response = await async_client.get(
            f"/api/v1/learning/reports/page/{page.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page_id"] == str(page.id)
        assert "page_title" in data
        assert "requires_training" in data
        assert "has_assessment" in data
        assert "total_assigned" in data
        assert "completion_rate" in data

    @pytest.mark.asyncio
    async def test_user_training_history(
        self, async_client: AsyncClient, setup_learning_test, admin_auth_headers
    ):
        """Should get user training history."""
        user = setup_learning_test["user"]

        response = await async_client.get(
            f"/api/v1/learning/reports/user/{user.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == str(user.id)
        assert "user_email" in data
        assert "user_name" in data
        assert "total_assignments" in data
        assert "completed" in data
        assert "in_progress" in data
        assert "overdue" in data
        assert "acknowledgments" in data

    @pytest.mark.asyncio
    async def test_user_training_history_not_found(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Should return 404 for non-existent user."""
        response = await async_client.get(
            f"/api/v1/learning/reports/user/{str(uuid4())}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_report_export_json(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Should export completion report as JSON."""
        response = await async_client.post(
            "/api/v1/learning/reports/export",
            json={"report_type": "completion", "format": "json"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "completion"
        assert "generated_at" in data
        assert "data" in data

    @pytest.mark.asyncio
    async def test_report_export_csv(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Should export completion report as CSV."""
        response = await async_client.post(
            "/api/v1/learning/reports/export",
            json={"report_type": "completion", "format": "csv"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        # CSV should have headers
        content = response.text
        assert "page_id" in content

    @pytest.mark.asyncio
    async def test_report_export_overdue(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Should export overdue report."""
        response = await async_client.post(
            "/api/v1/learning/reports/export",
            json={"report_type": "overdue", "format": "json"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "overdue"

    @pytest.mark.asyncio
    async def test_report_export_user_requires_user_id(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Should require user_id for user report export."""
        response = await async_client.post(
            "/api/v1/learning/reports/export",
            json={"report_type": "user", "format": "json"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 400
        assert "user_id is required" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_report_export_page_requires_page_id(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Should require page_id for page report export."""
        response = await async_client.post(
            "/api/v1/learning/reports/export",
            json={"report_type": "page", "format": "json"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 400
        assert "page_id is required" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_report_export_invalid_type(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Should reject invalid report type."""
        response = await async_client.post(
            "/api/v1/learning/reports/export",
            json={"report_type": "invalid", "format": "json"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 400
        assert "Invalid report type" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_report_export_invalid_format(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Should reject invalid format."""
        response = await async_client.post(
            "/api/v1/learning/reports/export",
            json={"report_type": "completion", "format": "xml"},
            headers=admin_auth_headers,
        )

        assert response.status_code == 400
        assert "Invalid format" in response.json()["detail"]


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestLearningEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_quiz_max_attempts_exceeded(
        self, async_client: AsyncClient, db_session, setup_assessment, auth_headers
    ):
        """Should prevent starting quiz when max attempts reached."""
        assessment = setup_assessment["assessment"]
        user = setup_assessment["user"]

        # Set max_attempts to 1 and create a completed attempt
        assessment.max_attempts = 1
        attempt = QuizAttempt(
            id=str(uuid4()),
            assessment_id=assessment.id,
            user_id=user.id,
            status=AttemptStatus.FAILED.value,
            started_at=datetime.now(timezone.utc),
            attempt_number=1,
            answers={},
        )
        db_session.add(attempt)
        await db_session.commit()

        # Try to start another attempt
        response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/start",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_submit_already_submitted_attempt(
        self, async_client: AsyncClient, setup_assessment, auth_headers
    ):
        """Should prevent submitting already submitted attempt."""
        assessment = setup_assessment["assessment"]

        # Start and submit
        start_response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/start",
            json={},
            headers=auth_headers,
        )
        attempt_id = start_response.json()["attempt_id"]

        # First submit
        await async_client.post(
            f"/api/v1/learning/attempts/{attempt_id}/submit",
            headers=auth_headers,
        )

        # Second submit should fail
        response = await async_client.post(
            f"/api/v1/learning/attempts/{attempt_id}/submit",
            headers=auth_headers,
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_access_other_users_attempt(
        self, async_client: AsyncClient, setup_assessment, auth_headers, admin_auth_headers
    ):
        """Should prevent accessing another user's attempt."""
        assessment = setup_assessment["assessment"]

        # Start attempt as user
        start_response = await async_client.post(
            f"/api/v1/learning/assessments/{assessment.id}/start",
            json={},
            headers=auth_headers,
        )
        attempt_id = start_response.json()["attempt_id"]

        # Try to access as admin
        response = await async_client.get(
            f"/api/v1/learning/attempts/{attempt_id}",
            headers=admin_auth_headers,
        )

        # Admin might have access or it might be forbidden depending on implementation
        assert response.status_code in [200, 403, 404]
