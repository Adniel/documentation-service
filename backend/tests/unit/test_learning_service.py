"""Unit tests for the learning module service.

Sprint 9: Learning Module Basics
Tests CRUD operations for assessments, questions, assignments, and attempts.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from src.db.models.assessment import Assessment, AssessmentQuestion, QuestionType
from src.db.models.learning_assignment import LearningAssignment, AssignmentStatus
from src.db.models.quiz_attempt import QuizAttempt, AttemptStatus
from src.modules.learning.schemas import (
    AssessmentCreate,
    AssessmentUpdate,
    QuestionCreate,
    QuestionUpdate,
    AssignmentCreate,
    AssignmentBulkCreate,
    QuestionPublic,
    MultipleChoiceOption,
)
from src.modules.learning import service


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def sample_assessment_create():
    """Sample assessment creation data."""
    return AssessmentCreate(
        page_id=str(uuid4()),
        title="Test Assessment",
        description="A test assessment",
        passing_score=80,
        max_attempts=3,
        time_limit_minutes=30,
    )


@pytest.fixture
def sample_question_create():
    """Sample question creation data."""
    return QuestionCreate(
        question_type=QuestionType.MULTIPLE_CHOICE,
        question_text="What is 2+2?",
        options=[
            MultipleChoiceOption(id="a", text="3", is_correct=False),
            MultipleChoiceOption(id="b", text="4", is_correct=True),
            MultipleChoiceOption(id="c", text="5", is_correct=False),
        ],
        points=10,
        explanation="Basic math",
    )


@pytest.fixture
def sample_tf_question_create():
    """Sample true/false question creation data."""
    return QuestionCreate(
        question_type=QuestionType.TRUE_FALSE,
        question_text="Is the earth round?",
        correct_answer="true",
        points=5,
        explanation="The earth is spherical",
    )


@pytest.fixture
def sample_assignment_create():
    """Sample assignment creation data."""
    return AssignmentCreate(
        page_id=str(uuid4()),
        user_id=str(uuid4()),
        due_date=datetime.now(timezone.utc) + timedelta(days=7),
        notes="Complete this training",
    )


@pytest.fixture
def mock_assessment():
    """Create a mock assessment."""
    assessment = MagicMock(spec=Assessment)
    assessment.id = str(uuid4())
    assessment.page_id = str(uuid4())
    assessment.title = "Test Assessment"
    assessment.description = "Test description"
    assessment.passing_score = 80
    assessment.max_attempts = 3
    assessment.time_limit_minutes = 30
    assessment.is_active = True
    assessment.questions = []
    return assessment


@pytest.fixture
def mock_question():
    """Create a mock question."""
    question = MagicMock(spec=AssessmentQuestion)
    question.id = str(uuid4())
    question.assessment_id = str(uuid4())
    question.question_type = QuestionType.MULTIPLE_CHOICE.value
    question.question_text = "What is 2+2?"
    question.options = [
        {"id": "a", "text": "3", "is_correct": False},
        {"id": "b", "text": "4", "is_correct": True},
    ]
    question.correct_answer = None
    question.points = 10
    question.explanation = "Basic math"
    question.sort_order = 1
    return question


@pytest.fixture
def mock_assignment():
    """Create a mock assignment."""
    assignment = MagicMock(spec=LearningAssignment)
    assignment.id = str(uuid4())
    assignment.page_id = str(uuid4())
    assignment.user_id = str(uuid4())
    assignment.assigned_by_id = str(uuid4())
    assignment.status = AssignmentStatus.ASSIGNED.value
    assignment.due_date = datetime.now(timezone.utc) + timedelta(days=7)
    assignment.assigned_at = datetime.now(timezone.utc)
    assignment.page = MagicMock()
    assignment.user = MagicMock()
    return assignment


@pytest.fixture
def mock_attempt():
    """Create a mock quiz attempt."""
    attempt = MagicMock(spec=QuizAttempt)
    attempt.id = str(uuid4())
    attempt.assessment_id = str(uuid4())
    attempt.user_id = str(uuid4())
    attempt.assignment_id = None
    attempt.status = AttemptStatus.IN_PROGRESS.value
    attempt.answers = {}
    attempt.started_at = datetime.now(timezone.utc)
    attempt.submitted_at = None
    attempt.attempt_number = 1
    return attempt


# =============================================================================
# ASSESSMENT TESTS
# =============================================================================

class TestAssessmentOperations:
    """Tests for assessment CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_assessment(self, mock_db, sample_assessment_create):
        """Test creating a new assessment."""
        user_id = str(uuid4())

        # Mock the db operations
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        result = await service.create_assessment(
            mock_db, sample_assessment_create, user_id
        )

        # Verify db.add was called with an Assessment
        mock_db.add.assert_called_once()
        added_obj = mock_db.add.call_args[0][0]
        assert isinstance(added_obj, Assessment)
        assert added_obj.title == "Test Assessment"
        assert added_obj.page_id == sample_assessment_create.page_id
        assert added_obj.passing_score == 80
        assert added_obj.created_by_id == user_id

    @pytest.mark.asyncio
    async def test_get_assessment(self, mock_db, mock_assessment):
        """Test getting an assessment by ID."""
        # Setup mock response
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_assessment
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.get_assessment(mock_db, mock_assessment.id)

        assert result == mock_assessment
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assessment_not_found(self, mock_db):
        """Test getting an assessment that doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.get_assessment(mock_db, str(uuid4()))

        assert result is None

    @pytest.mark.asyncio
    async def test_update_assessment(self, mock_db, mock_assessment):
        """Test updating an assessment."""
        update_data = AssessmentUpdate(title="Updated Title", passing_score=70)

        result = await service.update_assessment(mock_db, mock_assessment, update_data)

        assert mock_assessment.title == "Updated Title"
        assert mock_assessment.passing_score == 70
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_assessment(self, mock_db, mock_assessment):
        """Test deleting an assessment."""
        await service.delete_assessment(mock_db, mock_assessment)

        mock_db.delete.assert_called_once_with(mock_assessment)
        mock_db.flush.assert_called_once()


# =============================================================================
# QUESTION TESTS
# =============================================================================

class TestQuestionOperations:
    """Tests for question CRUD operations."""

    @pytest.mark.asyncio
    async def test_add_mc_question(self, mock_db, sample_question_create):
        """Test adding a multiple choice question."""
        assessment_id = str(uuid4())

        # Mock getting max sort order
        mock_result = MagicMock()
        mock_result.scalar.return_value = 2
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.add_question(mock_db, assessment_id, sample_question_create)

        mock_db.add.assert_called_once()
        added_obj = mock_db.add.call_args[0][0]
        assert isinstance(added_obj, AssessmentQuestion)
        assert added_obj.question_type == QuestionType.MULTIPLE_CHOICE.value
        assert added_obj.question_text == "What is 2+2?"
        assert added_obj.points == 10
        assert added_obj.sort_order == 3  # max + 1

    @pytest.mark.asyncio
    async def test_add_tf_question(self, mock_db, sample_tf_question_create):
        """Test adding a true/false question."""
        assessment_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.add_question(mock_db, assessment_id, sample_tf_question_create)

        added_obj = mock_db.add.call_args[0][0]
        assert added_obj.question_type == QuestionType.TRUE_FALSE.value
        assert added_obj.correct_answer == "true"

    @pytest.mark.asyncio
    async def test_update_question(self, mock_db, mock_question):
        """Test updating a question."""
        update_data = QuestionUpdate(question_text="Updated question?", points=20)

        result = await service.update_question(mock_db, mock_question, update_data)

        assert mock_question.question_text == "Updated question?"
        assert mock_question.points == 20
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_question(self, mock_db, mock_question):
        """Test deleting a question."""
        await service.delete_question(mock_db, mock_question)

        mock_db.delete.assert_called_once_with(mock_question)

    @pytest.mark.asyncio
    async def test_reorder_questions(self, mock_db):
        """Test reordering questions."""
        q1 = MagicMock()
        q1.id = "q1"
        q1.sort_order = 1
        q2 = MagicMock()
        q2.id = "q2"
        q2.sort_order = 2
        q3 = MagicMock()
        q3.id = "q3"
        q3.sort_order = 3

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [q1, q2, q3]
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Reorder: q3, q1, q2
        result = await service.reorder_questions(mock_db, "assessment_id", ["q3", "q1", "q2"])

        assert q3.sort_order == 0
        assert q1.sort_order == 1
        assert q2.sort_order == 2


# =============================================================================
# ASSIGNMENT TESTS
# =============================================================================

class TestAssignmentOperations:
    """Tests for assignment CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_assignment(self, mock_db, sample_assignment_create):
        """Test creating a learning assignment."""
        assigned_by_id = str(uuid4())

        result = await service.create_assignment(
            mock_db, sample_assignment_create, assigned_by_id
        )

        mock_db.add.assert_called_once()
        added_obj = mock_db.add.call_args[0][0]
        assert isinstance(added_obj, LearningAssignment)
        assert added_obj.page_id == sample_assignment_create.page_id
        assert added_obj.user_id == sample_assignment_create.user_id
        assert added_obj.assigned_by_id == assigned_by_id
        assert added_obj.notes == "Complete this training"

    @pytest.mark.asyncio
    async def test_create_bulk_assignments(self, mock_db):
        """Test creating multiple assignments at once."""
        user_ids = [str(uuid4()) for _ in range(3)]
        bulk_create = AssignmentBulkCreate(
            page_id=str(uuid4()),
            user_ids=user_ids,
            due_date=datetime.now(timezone.utc) + timedelta(days=7),
            notes="Training for team",
        )
        assigned_by_id = str(uuid4())

        result = await service.create_bulk_assignments(
            mock_db, bulk_create, assigned_by_id
        )

        # Should add 3 assignments
        assert mock_db.add.call_count == 3

    @pytest.mark.asyncio
    async def test_list_assignments_with_filters(self, mock_db, mock_assignment):
        """Test listing assignments with various filters."""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_assignment]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

        assignments, total = await service.list_assignments(
            mock_db,
            user_id=mock_assignment.user_id,
            status=AssignmentStatus.ASSIGNED,
            limit=10,
        )

        assert len(assignments) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_cancel_assignment(self, mock_db, mock_assignment):
        """Test canceling an assignment."""
        result = await service.cancel_assignment(mock_db, mock_assignment)

        mock_assignment.cancel.assert_called_once()
        mock_db.flush.assert_called_once()


# =============================================================================
# QUIZ ATTEMPT TESTS
# =============================================================================

class TestQuizAttemptOperations:
    """Tests for quiz attempt operations."""

    @pytest.mark.asyncio
    async def test_start_attempt(self, mock_db):
        """Test starting a new quiz attempt."""
        assessment_id = str(uuid4())
        user_id = str(uuid4())

        # Mock count result for attempt number
        mock_count = MagicMock()
        mock_count.scalar.return_value = 0
        mock_db.execute = AsyncMock(return_value=mock_count)

        result = await service.start_attempt(mock_db, assessment_id, user_id)

        mock_db.add.assert_called_once()
        added_obj = mock_db.add.call_args[0][0]
        assert isinstance(added_obj, QuizAttempt)
        assert added_obj.assessment_id == assessment_id
        assert added_obj.user_id == user_id
        assert added_obj.attempt_number == 1
        assert added_obj.status == AttemptStatus.IN_PROGRESS.value

    @pytest.mark.asyncio
    async def test_start_subsequent_attempt(self, mock_db):
        """Test starting a second attempt counts correctly."""
        assessment_id = str(uuid4())
        user_id = str(uuid4())

        # Mock count result showing 2 previous attempts
        mock_count = MagicMock()
        mock_count.scalar.return_value = 2
        mock_db.execute = AsyncMock(return_value=mock_count)

        result = await service.start_attempt(mock_db, assessment_id, user_id)

        added_obj = mock_db.add.call_args[0][0]
        assert added_obj.attempt_number == 3

    @pytest.mark.asyncio
    async def test_save_answer(self, mock_db, mock_attempt):
        """Test saving an answer to an attempt."""
        question_id = str(uuid4())
        answer = "b"

        result = await service.save_answer(mock_db, mock_attempt, question_id, answer)

        mock_attempt.set_answer.assert_called_once_with(question_id, answer)
        mock_db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_in_progress_attempt(self, mock_db, mock_attempt):
        """Test getting an in-progress attempt."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_attempt
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.get_in_progress_attempt(
            mock_db,
            mock_attempt.assessment_id,
            mock_attempt.user_id,
        )

        assert result == mock_attempt

    @pytest.mark.asyncio
    async def test_get_passing_attempt(self, mock_db, mock_attempt):
        """Test getting a passing attempt."""
        mock_attempt.status = AttemptStatus.PASSED.value
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_attempt
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await service.get_passing_attempt(
            mock_db,
            mock_attempt.assessment_id,
            mock_attempt.user_id,
        )

        assert result == mock_attempt
        assert result.status == AttemptStatus.PASSED.value


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestHelperFunctions:
    """Tests for helper functions."""

    def test_prepare_assessment_for_quiz(self, mock_assessment, mock_question):
        """Test preparing assessment for quiz (hiding answers)."""
        mock_question.sort_order = 1
        mock_assessment.questions = [mock_question]

        result = service.prepare_assessment_for_quiz(mock_assessment)

        assert result.id == mock_assessment.id
        assert result.title == mock_assessment.title
        assert len(result.questions) == 1

        # Check that is_correct is not in options
        public_q = result.questions[0]
        assert public_q.options is not None
        for opt in public_q.options:
            assert "is_correct" not in opt

    def test_prepare_assessment_calculates_totals(self, mock_assessment, mock_question):
        """Test that prepare_assessment_for_quiz calculates question count and points."""
        mock_question.points = 10
        mock_question.sort_order = 1
        mock_assessment.questions = [mock_question, mock_question]

        result = service.prepare_assessment_for_quiz(mock_assessment)

        assert result.question_count == 2
        assert result.total_points == 20

    def test_prepare_assessment_orders_questions(self, mock_assessment):
        """Test that questions are sorted by sort_order."""
        q1 = MagicMock()
        q1.id = "q1"
        q1.question_type = "multiple_choice"
        q1.question_text = "Q1"
        q1.options = [{"id": "a", "text": "A", "is_correct": True}]
        q1.points = 5
        q1.sort_order = 2

        q2 = MagicMock()
        q2.id = "q2"
        q2.question_type = "true_false"
        q2.question_text = "Q2"
        q2.options = None
        q2.points = 5
        q2.sort_order = 1

        mock_assessment.questions = [q1, q2]

        result = service.prepare_assessment_for_quiz(mock_assessment)

        # Q2 should come first (sort_order=1)
        assert result.questions[0].id == "q2"
        assert result.questions[1].id == "q1"
