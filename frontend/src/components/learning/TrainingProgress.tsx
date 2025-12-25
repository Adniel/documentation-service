/**
 * TrainingProgress - User's training progress dashboard.
 *
 * Shows overall progress, recent acknowledgments, and completion statistics.
 *
 * Sprint 9: Learning Module Basics
 */

import { useState, useEffect, useCallback } from 'react';
import {
  learningApi,
  type LearningAssignment,
  type TrainingAcknowledgment,
  type QuizAttempt,
} from '../../lib/api';

interface TrainingProgressProps {
  userId?: string;
  onViewAssignment?: (assignment: LearningAssignment) => void;
}

interface Stats {
  totalAssignments: number;
  completedAssignments: number;
  pendingAssignments: number;
  overdueAssignments: number;
  validAcknowledgments: number;
  passedQuizzes: number;
  failedQuizzes: number;
}

export function TrainingProgress({ onViewAssignment }: TrainingProgressProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assignments, setAssignments] = useState<LearningAssignment[]>([]);
  const [acknowledgments, setAcknowledgments] = useState<TrainingAcknowledgment[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_attempts, setAttempts] = useState<QuizAttempt[]>([]);
  const [stats, setStats] = useState<Stats>({
    totalAssignments: 0,
    completedAssignments: 0,
    pendingAssignments: 0,
    overdueAssignments: 0,
    validAcknowledgments: 0,
    passedQuizzes: 0,
    failedQuizzes: 0,
  });

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all data in parallel
      const [assignmentsData, acknowledgmentsData, attemptsData] = await Promise.all([
        learningApi.getMyAssignments(true),
        learningApi.getMyAcknowledgments(false),
        learningApi.getMyAttempts(),
      ]);

      setAssignments(assignmentsData);
      setAcknowledgments(acknowledgmentsData);
      setAttempts(attemptsData);

      // Calculate stats
      const now = new Date();
      const overdue = assignmentsData.filter(
        (a) =>
          a.due_date &&
          new Date(a.due_date) < now &&
          a.status !== 'completed' &&
          a.status !== 'cancelled'
      ).length;

      setStats({
        totalAssignments: assignmentsData.length,
        completedAssignments: assignmentsData.filter((a) => a.status === 'completed').length,
        pendingAssignments: assignmentsData.filter(
          (a) => a.status === 'assigned' || a.status === 'in_progress'
        ).length,
        overdueAssignments: overdue,
        validAcknowledgments: acknowledgmentsData.filter((a) => a.is_valid).length,
        passedQuizzes: attemptsData.filter((a) => a.status === 'passed').length,
        failedQuizzes: attemptsData.filter((a) => a.status === 'failed').length,
      });
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load training data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const completionRate =
    stats.totalAssignments > 0
      ? Math.round((stats.completedAssignments / stats.totalAssignments) * 100)
      : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Loading training data...</span>
      </div>
    );
  }

  if (error) {
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
        <button
          onClick={loadData}
          className="mt-4 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 rounded-md transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-3xl font-bold text-blue-600">{stats.pendingAssignments}</div>
          <div className="text-sm text-gray-500">Pending</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-3xl font-bold text-green-600">{stats.completedAssignments}</div>
          <div className="text-sm text-gray-500">Completed</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-3xl font-bold text-red-600">{stats.overdueAssignments}</div>
          <div className="text-sm text-gray-500">Overdue</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-3xl font-bold text-purple-600">{completionRate}%</div>
          <div className="text-sm text-gray-500">Completion Rate</div>
        </div>
      </div>

      {/* Overall Progress */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Progress</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Assignment Completion</span>
              <span className="font-medium text-gray-900">
                {stats.completedAssignments} / {stats.totalAssignments}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${completionRate}%` }}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-100">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{stats.validAcknowledgments}</div>
              <div className="text-xs text-gray-500">Valid Acknowledgments</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.passedQuizzes}</div>
              <div className="text-xs text-gray-500">Quizzes Passed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.failedQuizzes}</div>
              <div className="text-xs text-gray-500">Quizzes Failed</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Acknowledgments */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Acknowledgments</h3>
        {acknowledgments.length === 0 ? (
          <p className="text-gray-500 text-sm">No acknowledgments yet.</p>
        ) : (
          <div className="space-y-3">
            {acknowledgments.slice(0, 5).map((ack) => (
              <div
                key={ack.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    {ack.page_version}
                  </div>
                  <div className="text-xs text-gray-500">
                    Acknowledged: {formatDate(ack.acknowledged_at)}
                    {ack.valid_until && (
                      <span className="ml-2">
                        | Valid until: {formatDate(ack.valid_until)}
                      </span>
                    )}
                  </div>
                </div>
                <span
                  className={`px-2 py-1 text-xs font-medium rounded ${
                    ack.is_valid
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {ack.is_valid ? 'Valid' : 'Expired'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pending Assignments */}
      {stats.pendingAssignments > 0 && (
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Assignments</h3>
          <div className="space-y-3">
            {assignments
              .filter((a) => a.status === 'assigned' || a.status === 'in_progress')
              .slice(0, 5)
              .map((assignment) => (
                <div
                  key={assignment.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {assignment.page?.title || 'Untitled Document'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {assignment.due_date
                        ? `Due: ${formatDate(assignment.due_date)}`
                        : 'No due date'}
                    </div>
                  </div>
                  {onViewAssignment && (
                    <button
                      onClick={() => onViewAssignment(assignment)}
                      className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                    >
                      View
                    </button>
                  )}
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default TrainingProgress;
