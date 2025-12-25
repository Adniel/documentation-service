"""Grading service for learning module.

Handles automatic grading of quiz attempts.

Sprint 9: Learning Module Basics
"""

from typing import List

from src.db.models.assessment import Assessment, AssessmentQuestion, QuestionType
from src.db.models.quiz_attempt import QuizAttempt, AttemptStatus
from src.modules.learning.schemas import GradeResult


def grade_question(question: AssessmentQuestion, user_answer: str | None) -> dict:
    """Grade a single question.

    Args:
        question: The question to grade
        user_answer: User's submitted answer

    Returns:
        Dict with grading result for this question
    """
    is_correct = question.is_answer_correct(user_answer)

    return {
        "question_id": str(question.id),
        "question_type": question.question_type,
        "user_answer": user_answer,
        "is_correct": is_correct,
        "points_earned": question.points if is_correct else 0,
        "points_possible": question.points,
        "correct_answer": _get_correct_answer_display(question),
        "explanation": question.explanation,
    }


def _get_correct_answer_display(question: AssessmentQuestion) -> str | None:
    """Get the correct answer for display.

    For multiple choice, returns the correct option text.
    For true/false and fill_blank, returns the correct_answer field.
    """
    if question.question_type == QuestionType.MULTIPLE_CHOICE.value:
        if question.options:
            for option in question.options:
                if option.get("is_correct"):
                    return option.get("text", option.get("id"))
        return None
    return question.correct_answer


def grade_attempt(
    attempt: QuizAttempt,
    questions: List[AssessmentQuestion],
    passing_score: int,
) -> GradeResult:
    """Grade a complete quiz attempt.

    Args:
        attempt: The quiz attempt to grade
        questions: List of questions in the assessment
        passing_score: Passing percentage (0-100)

    Returns:
        GradeResult with score and pass/fail status
    """
    if not questions:
        # No questions means automatic pass
        return GradeResult(
            score=100.0,
            passed=True,
            earned_points=0,
            total_points=0,
            passing_score=passing_score,
            question_results=[],
        )

    total_points = sum(q.points for q in questions)
    earned_points = 0
    question_results = []

    for question in questions:
        user_answer = attempt.answers.get(str(question.id)) if attempt.answers else None
        result = grade_question(question, user_answer)
        question_results.append(result)
        earned_points += result["points_earned"]

    # Calculate score as percentage
    score = (earned_points / total_points * 100) if total_points > 0 else 100.0
    passed = score >= passing_score

    return GradeResult(
        score=round(score, 2),
        passed=passed,
        earned_points=earned_points,
        total_points=total_points,
        passing_score=passing_score,
        question_results=question_results,
    )


def update_attempt_with_grade(attempt: QuizAttempt, grade_result: GradeResult) -> None:
    """Update a quiz attempt with grading results.

    Args:
        attempt: The attempt to update
        grade_result: The grading result
    """
    attempt.score = grade_result.score
    attempt.earned_points = grade_result.earned_points
    attempt.total_points = grade_result.total_points
    attempt.passing_score = grade_result.passing_score
    attempt.status = (
        AttemptStatus.PASSED.value if grade_result.passed else AttemptStatus.FAILED.value
    )
