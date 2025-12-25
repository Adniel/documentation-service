/**
 * QuizTaking - Main quiz taking interface.
 *
 * Handles quiz start, progress, auto-save answers, and submission.
 * Displays results with grading after submission.
 *
 * Sprint 9: Learning Module Basics
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  learningApi,
  type AssessmentPublic,
  type QuizAttempt,
  type GradeResult,
} from '../../lib/api';
import { QuestionCard } from './QuestionCard';

interface QuizTakingProps {
  pageId: string;
  assignmentId?: string;
  onComplete?: (passed: boolean, score: number) => void;
  onBack?: () => void;
}

type QuizState = 'loading' | 'ready' | 'in_progress' | 'submitting' | 'completed' | 'error';

export function QuizTaking({ pageId, assignmentId, onComplete, onBack }: QuizTakingProps) {
  const [state, setState] = useState<QuizState>('loading');
  const [error, setError] = useState<string | null>(null);
  const [quiz, setQuiz] = useState<AssessmentPublic | null>(null);
  const [attempt, setAttempt] = useState<QuizAttempt | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [gradeResult, setGradeResult] = useState<GradeResult | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [saving, setSaving] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  // Load quiz on mount
  useEffect(() => {
    const loadQuiz = async () => {
      try {
        const quizData = await learningApi.getQuiz(pageId);
        setQuiz(quizData);
        setState('ready');
      } catch (err) {
        const error = err as { response?: { status?: number; data?: { detail?: string } } };
        if (error.response?.status === 404) {
          setError('No assessment found for this document.');
        } else {
          setError(error.response?.data?.detail || 'Failed to load quiz.');
        }
        setState('error');
      }
    };

    loadQuiz();
  }, [pageId]);

  // Timer countdown
  useEffect(() => {
    if (state !== 'in_progress' || timeRemaining === null) return;

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev === null || prev <= 0) {
          clearInterval(timer);
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [state, timeRemaining]);

  const handleStart = useCallback(async () => {
    if (!quiz) return;

    try {
      setState('loading');
      const attemptData = await learningApi.startAttempt(quiz.id, assignmentId);
      setAttempt(attemptData);
      setAnswers(attemptData.answers || {});

      // Set timer if time limit exists
      if (quiz.time_limit_minutes) {
        setTimeRemaining(quiz.time_limit_minutes * 60);
      }

      setState('in_progress');
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to start quiz.');
      setState('error');
    }
  }, [quiz, assignmentId]);

  const handleAnswerChange = useCallback(
    async (questionId: string, answer: string) => {
      if (!attempt) return;

      setAnswers((prev) => ({ ...prev, [questionId]: answer }));

      // Auto-save answer
      setSaving(true);
      try {
        await learningApi.saveAnswer(attempt.id, questionId, answer);
      } catch {
        // Silently fail auto-save, answer is still in local state
      } finally {
        setSaving(false);
      }
    },
    [attempt]
  );

  const handleSubmit = useCallback(async () => {
    if (!attempt) return;

    try {
      setState('submitting');
      const result = await learningApi.submitAttempt(attempt.id);
      setGradeResult(result.grade_result);
      setState('completed');

      if (onComplete) {
        onComplete(result.grade_result.passed, result.grade_result.score);
      }
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to submit quiz.');
      setState('error');
    }
  }, [attempt, onComplete]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progress = useMemo(() => {
    if (!quiz) return 0;
    const answered = Object.keys(answers).length;
    return Math.round((answered / quiz.question_count) * 100);
  }, [quiz, answers]);

  const currentQuestion = quiz?.questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === (quiz?.questions.length || 0) - 1;
  const allAnswered = quiz ? Object.keys(answers).length === quiz.question_count : false;

  // Loading state
  if (state === 'loading') {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Loading quiz...</span>
      </div>
    );
  }

  // Error state
  if (state === 'error') {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-start gap-3">
          <svg className="w-5 h-5 text-red-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <h3 className="font-medium text-red-800">Error</h3>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        </div>
        {onBack && (
          <button
            onClick={onBack}
            className="mt-4 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 rounded-md transition-colors"
          >
            Go Back
          </button>
        )}
      </div>
    );
  }

  // Ready state - show quiz intro
  if (state === 'ready' && quiz) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">{quiz.title}</h2>
          {quiz.description && <p className="text-gray-600 mb-6">{quiz.description}</p>}

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{quiz.question_count}</div>
              <div className="text-sm text-gray-500">Questions</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{quiz.passing_score}%</div>
              <div className="text-sm text-gray-500">Passing Score</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{quiz.total_points}</div>
              <div className="text-sm text-gray-500">Total Points</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {quiz.time_limit_minutes ? `${quiz.time_limit_minutes} min` : 'None'}
              </div>
              <div className="text-sm text-gray-500">Time Limit</div>
            </div>
          </div>

          {quiz.max_attempts && (
            <div className="mb-6 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
              <strong>Note:</strong> You have a maximum of {quiz.max_attempts} attempt
              {quiz.max_attempts !== 1 ? 's' : ''} for this quiz.
            </div>
          )}

          <div className="flex gap-3">
            {onBack && (
              <button
                onClick={onBack}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              >
                Back
              </button>
            )}
            <button
              onClick={handleStart}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
            >
              Start Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  // In progress - show questions
  if (state === 'in_progress' && quiz && currentQuestion) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        {/* Progress bar and timer */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">
              Progress: {progress}% ({Object.keys(answers).length}/{quiz.question_count} answered)
            </span>
            <div className="flex items-center gap-3">
              {saving && (
                <span className="text-xs text-gray-400 flex items-center gap-1">
                  <div className="animate-spin rounded-full h-3 w-3 border-b border-gray-400" />
                  Saving...
                </span>
              )}
              {timeRemaining !== null && (
                <span
                  className={`text-sm font-medium ${
                    timeRemaining < 60 ? 'text-red-600' : 'text-gray-600'
                  }`}
                >
                  Time: {formatTime(timeRemaining)}
                </span>
              )}
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question card */}
        <QuestionCard
          question={currentQuestion}
          questionNumber={currentQuestionIndex + 1}
          totalQuestions={quiz.question_count}
          selectedAnswer={answers[currentQuestion.id]}
          onAnswerChange={handleAnswerChange}
        />

        {/* Navigation */}
        <div className="mt-6 flex items-center justify-between">
          <button
            onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
            disabled={currentQuestionIndex === 0}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div className="flex gap-1">
            {quiz.questions.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentQuestionIndex(idx)}
                className={`w-8 h-8 rounded-md text-xs font-medium transition-colors ${
                  idx === currentQuestionIndex
                    ? 'bg-blue-600 text-white'
                    : answers[quiz.questions[idx].id]
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {idx + 1}
              </button>
            ))}
          </div>

          {isLastQuestion ? (
            <button
              onClick={handleSubmit}
              disabled={!allAnswered}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Submit Quiz
            </button>
          ) : (
            <button
              onClick={() =>
                setCurrentQuestionIndex((prev) => Math.min(quiz.question_count - 1, prev + 1))
              }
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
            >
              Next
            </button>
          )}
        </div>
      </div>
    );
  }

  // Submitting state
  if (state === 'submitting') {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Submitting quiz...</span>
      </div>
    );
  }

  // Completed - show results
  if (state === 'completed' && quiz && gradeResult) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        {/* Results summary */}
        <div
          className={`mb-6 p-6 rounded-lg ${
            gradeResult.passed ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}
        >
          <div className="flex items-center gap-4">
            {gradeResult.passed ? (
              <svg className="w-12 h-12 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg className="w-12 h-12 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            <div>
              <h2 className={`text-2xl font-bold ${gradeResult.passed ? 'text-green-800' : 'text-red-800'}`}>
                {gradeResult.passed ? 'Congratulations! You Passed!' : 'You Did Not Pass'}
              </h2>
              <p className={`text-lg ${gradeResult.passed ? 'text-green-700' : 'text-red-700'}`}>
                Score: {gradeResult.score.toFixed(1)}% ({gradeResult.earned_points}/{gradeResult.total_points}{' '}
                points)
              </p>
              <p className={`text-sm ${gradeResult.passed ? 'text-green-600' : 'text-red-600'}`}>
                Passing score: {gradeResult.passing_score}%
              </p>
            </div>
          </div>
        </div>

        {/* Question review */}
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Your Answers</h3>
        <div className="space-y-4">
          {quiz.questions.map((question, idx) => {
            const result = gradeResult.question_results.find((r) => r.question_id === question.id);
            return (
              <QuestionCard
                key={question.id}
                question={question}
                questionNumber={idx + 1}
                totalQuestions={quiz.question_count}
                selectedAnswer={answers[question.id]}
                onAnswerChange={() => {}}
                disabled
                showResult
                isCorrect={result?.is_correct}
                correctAnswer={result?.correct_answer}
                explanation={result?.explanation}
              />
            );
          })}
        </div>

        {/* Actions */}
        <div className="mt-6 flex gap-3">
          {onBack && (
            <button
              onClick={onBack}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 hover:bg-gray-50 rounded-md transition-colors"
            >
              Back to Document
            </button>
          )}
        </div>
      </div>
    );
  }

  return null;
}

export default QuizTaking;
