"""Unit tests for the learning module grading service.

Sprint 9: Learning Module Basics
Tests automatic quiz grading logic.
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from src.db.models.assessment import QuestionType
from src.db.models.quiz_attempt import AttemptStatus
from src.modules.learning.grading_service import (
    grade_question,
    grade_attempt,
    update_attempt_with_grade,
    _get_correct_answer_display,
)
from src.modules.learning.schemas import GradeResult


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_mc_question():
    """Create a mock multiple choice question."""
    question = MagicMock()
    question.id = "q1"
    question.question_type = QuestionType.MULTIPLE_CHOICE.value
    question.question_text = "What is 2+2?"
    question.options = [
        {"id": "a", "text": "3", "is_correct": False},
        {"id": "b", "text": "4", "is_correct": True},
        {"id": "c", "text": "5", "is_correct": False},
    ]
    question.correct_answer = None
    question.points = 10
    question.explanation = "2+2=4"
    question.is_answer_correct = lambda ans: ans == "b"
    return question


@pytest.fixture
def mock_tf_question():
    """Create a mock true/false question."""
    question = MagicMock()
    question.id = "q2"
    question.question_type = QuestionType.TRUE_FALSE.value
    question.question_text = "Is the sky blue?"
    question.options = None
    question.correct_answer = "true"
    question.points = 5
    question.explanation = "The sky appears blue due to Rayleigh scattering."
    question.is_answer_correct = lambda ans: ans and ans.lower() == "true"
    return question


@pytest.fixture
def mock_fill_blank_question():
    """Create a mock fill-in-the-blank question."""
    question = MagicMock()
    question.id = "q3"
    question.question_type = QuestionType.FILL_BLANK.value
    question.question_text = "The capital of France is ___."
    question.options = None
    question.correct_answer = "Paris"
    question.points = 5
    question.explanation = "Paris is the capital of France."
    question.is_answer_correct = lambda ans: ans and ans.lower() == "paris"
    return question


@pytest.fixture
def mock_attempt():
    """Create a mock quiz attempt."""
    attempt = MagicMock()
    attempt.answers = {"q1": "b", "q2": "true"}
    return attempt


# =============================================================================
# GRADE QUESTION TESTS
# =============================================================================

class TestGradeQuestion:
    """Tests for grade_question function."""

    def test_correct_mc_answer(self, mock_mc_question):
        """Test grading a correct multiple choice answer."""
        result = grade_question(mock_mc_question, "b")

        assert result["question_id"] == "q1"
        assert result["is_correct"] is True
        assert result["points_earned"] == 10
        assert result["points_possible"] == 10
        assert result["user_answer"] == "b"

    def test_incorrect_mc_answer(self, mock_mc_question):
        """Test grading an incorrect multiple choice answer."""
        result = grade_question(mock_mc_question, "a")

        assert result["is_correct"] is False
        assert result["points_earned"] == 0
        assert result["points_possible"] == 10

    def test_null_answer(self, mock_mc_question):
        """Test grading when no answer provided."""
        result = grade_question(mock_mc_question, None)

        assert result["is_correct"] is False
        assert result["points_earned"] == 0
        assert result["user_answer"] is None

    def test_correct_tf_answer(self, mock_tf_question):
        """Test grading a correct true/false answer."""
        result = grade_question(mock_tf_question, "true")

        assert result["is_correct"] is True
        assert result["points_earned"] == 5

    def test_incorrect_tf_answer(self, mock_tf_question):
        """Test grading an incorrect true/false answer."""
        result = grade_question(mock_tf_question, "false")

        assert result["is_correct"] is False
        assert result["points_earned"] == 0

    def test_correct_fill_blank_answer(self, mock_fill_blank_question):
        """Test grading a correct fill-in-blank answer."""
        result = grade_question(mock_fill_blank_question, "Paris")

        assert result["is_correct"] is True
        assert result["points_earned"] == 5

    def test_explanation_included(self, mock_mc_question):
        """Test that explanation is included in result."""
        result = grade_question(mock_mc_question, "b")

        assert result["explanation"] == "2+2=4"


# =============================================================================
# GET CORRECT ANSWER DISPLAY TESTS
# =============================================================================

class TestGetCorrectAnswerDisplay:
    """Tests for _get_correct_answer_display function."""

    def test_mc_returns_correct_option_text(self, mock_mc_question):
        """Test that MC questions return the correct option text."""
        result = _get_correct_answer_display(mock_mc_question)

        assert result == "4"

    def test_tf_returns_correct_answer(self, mock_tf_question):
        """Test that T/F questions return the correct_answer field."""
        result = _get_correct_answer_display(mock_tf_question)

        assert result == "true"

    def test_fill_blank_returns_correct_answer(self, mock_fill_blank_question):
        """Test that fill-in-blank returns the correct_answer field."""
        result = _get_correct_answer_display(mock_fill_blank_question)

        assert result == "Paris"

    def test_mc_with_no_options_returns_none(self):
        """Test MC question with no options returns None."""
        question = MagicMock()
        question.question_type = QuestionType.MULTIPLE_CHOICE.value
        question.options = None

        result = _get_correct_answer_display(question)

        assert result is None


# =============================================================================
# GRADE ATTEMPT TESTS
# =============================================================================

class TestGradeAttempt:
    """Tests for grade_attempt function."""

    def test_perfect_score(self, mock_mc_question, mock_tf_question):
        """Test grading an attempt with all correct answers."""
        attempt = MagicMock()
        attempt.answers = {"q1": "b", "q2": "true"}
        questions = [mock_mc_question, mock_tf_question]

        result = grade_attempt(attempt, questions, passing_score=80)

        assert result.score == 100.0
        assert result.passed is True
        assert result.earned_points == 15
        assert result.total_points == 15
        assert len(result.question_results) == 2

    def test_partial_score(self, mock_mc_question, mock_tf_question):
        """Test grading an attempt with some incorrect answers."""
        attempt = MagicMock()
        attempt.answers = {"q1": "b", "q2": "false"}  # q1 correct, q2 wrong
        questions = [mock_mc_question, mock_tf_question]

        result = grade_attempt(attempt, questions, passing_score=80)

        # 10 out of 15 points = 66.67%
        assert result.score == pytest.approx(66.67, rel=0.01)
        assert result.passed is False
        assert result.earned_points == 10
        assert result.total_points == 15

    def test_failing_score(self, mock_mc_question, mock_tf_question):
        """Test grading an attempt that fails."""
        attempt = MagicMock()
        attempt.answers = {"q1": "a", "q2": "false"}  # both wrong
        questions = [mock_mc_question, mock_tf_question]

        result = grade_attempt(attempt, questions, passing_score=80)

        assert result.score == 0.0
        assert result.passed is False
        assert result.earned_points == 0

    def test_passing_at_threshold(self, mock_mc_question, mock_tf_question):
        """Test grading an attempt exactly at passing threshold."""
        attempt = MagicMock()
        attempt.answers = {"q1": "b", "q2": "false"}  # 10/15 = 66.67%
        questions = [mock_mc_question, mock_tf_question]

        result = grade_attempt(attempt, questions, passing_score=66)

        # 66.67% >= 66%
        assert result.passed is True

    def test_empty_questions_list(self):
        """Test grading with no questions (edge case)."""
        attempt = MagicMock()
        attempt.answers = {}

        result = grade_attempt(attempt, questions=[], passing_score=80)

        assert result.score == 100.0
        assert result.passed is True
        assert result.total_points == 0

    def test_missing_answers(self, mock_mc_question, mock_tf_question):
        """Test grading when some answers are missing."""
        attempt = MagicMock()
        attempt.answers = {"q1": "b"}  # Missing q2 answer
        questions = [mock_mc_question, mock_tf_question]

        result = grade_attempt(attempt, questions, passing_score=80)

        # Only q1 correct (10/15)
        assert result.earned_points == 10
        assert result.total_points == 15

    def test_null_answers_dict(self, mock_mc_question):
        """Test grading when answers dict is None."""
        attempt = MagicMock()
        attempt.answers = None
        questions = [mock_mc_question]

        result = grade_attempt(attempt, questions, passing_score=80)

        assert result.earned_points == 0
        assert result.passed is False


# =============================================================================
# UPDATE ATTEMPT WITH GRADE TESTS
# =============================================================================

class TestUpdateAttemptWithGrade:
    """Tests for update_attempt_with_grade function."""

    def test_update_passed_attempt(self):
        """Test updating an attempt that passed."""
        attempt = MagicMock()
        grade_result = GradeResult(
            score=85.0,
            passed=True,
            earned_points=17,
            total_points=20,
            passing_score=80,
            question_results=[],
        )

        update_attempt_with_grade(attempt, grade_result)

        assert attempt.score == 85.0
        assert attempt.earned_points == 17
        assert attempt.total_points == 20
        assert attempt.passing_score == 80
        assert attempt.status == AttemptStatus.PASSED.value

    def test_update_failed_attempt(self):
        """Test updating an attempt that failed."""
        attempt = MagicMock()
        grade_result = GradeResult(
            score=50.0,
            passed=False,
            earned_points=10,
            total_points=20,
            passing_score=80,
            question_results=[],
        )

        update_attempt_with_grade(attempt, grade_result)

        assert attempt.score == 50.0
        assert attempt.status == AttemptStatus.FAILED.value

    def test_update_edge_case_zero_points(self):
        """Test updating an attempt with zero points."""
        attempt = MagicMock()
        grade_result = GradeResult(
            score=100.0,
            passed=True,
            earned_points=0,
            total_points=0,
            passing_score=80,
            question_results=[],
        )

        update_attempt_with_grade(attempt, grade_result)

        assert attempt.score == 100.0
        assert attempt.total_points == 0
        assert attempt.status == AttemptStatus.PASSED.value


# =============================================================================
# INTEGRATION-LIKE UNIT TESTS
# =============================================================================

class TestGradingWorkflow:
    """Integration-like tests for the full grading workflow."""

    def test_complete_grading_workflow(
        self, mock_mc_question, mock_tf_question, mock_fill_blank_question
    ):
        """Test complete grading workflow with multiple question types."""
        attempt = MagicMock()
        attempt.answers = {
            "q1": "b",      # Correct (10 points)
            "q2": "true",   # Correct (5 points)
            "q3": "Paris",  # Correct (5 points)
        }
        questions = [mock_mc_question, mock_tf_question, mock_fill_blank_question]

        # Grade the attempt
        grade_result = grade_attempt(attempt, questions, passing_score=70)

        assert grade_result.score == 100.0
        assert grade_result.passed is True
        assert grade_result.earned_points == 20
        assert grade_result.total_points == 20

        # Update the attempt
        update_attempt_with_grade(attempt, grade_result)

        assert attempt.status == AttemptStatus.PASSED.value

    def test_grading_preserves_question_details(self, mock_mc_question):
        """Test that grading preserves all question details in results."""
        attempt = MagicMock()
        attempt.answers = {"q1": "a"}  # Wrong answer
        questions = [mock_mc_question]

        result = grade_attempt(attempt, questions, passing_score=80)

        q_result = result.question_results[0]
        assert q_result["question_id"] == "q1"
        assert q_result["question_type"] == QuestionType.MULTIPLE_CHOICE.value
        assert q_result["user_answer"] == "a"
        assert q_result["is_correct"] is False
        assert q_result["correct_answer"] == "4"
        assert q_result["explanation"] == "2+2=4"
