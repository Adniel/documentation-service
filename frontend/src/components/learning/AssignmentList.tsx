/**
 * AssignmentList - Displays user's training assignments.
 *
 * Shows pending, in-progress, and completed assignments with status and due dates.
 *
 * Sprint 9: Learning Module Basics
 */

import { useState, useEffect, useCallback } from 'react';
import { learningApi, type LearningAssignment, type AssignmentStatus } from '../../lib/api';

interface AssignmentListProps {
  onStartAssignment?: (assignment: LearningAssignment) => void;
  showCompleted?: boolean;
}

const STATUS_STYLES: Record<AssignmentStatus, { bg: string; text: string; label: string }> = {
  assigned: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Assigned' },
  in_progress: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'In Progress' },
  completed: { bg: 'bg-green-100', text: 'text-green-700', label: 'Completed' },
  overdue: { bg: 'bg-red-100', text: 'text-red-700', label: 'Overdue' },
  cancelled: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Cancelled' },
};

export function AssignmentList({ onStartAssignment, showCompleted = false }: AssignmentListProps) {
  const [assignments, setAssignments] = useState<LearningAssignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [includeCompleted, setIncludeCompleted] = useState(showCompleted);

  const loadAssignments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await learningApi.getMyAssignments(includeCompleted);
      setAssignments(data);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load assignments.');
    } finally {
      setLoading(false);
    }
  }, [includeCompleted]);

  useEffect(() => {
    loadAssignments();
  }, [loadAssignments]);

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'No due date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const isOverdue = (assignment: LearningAssignment): boolean => {
    if (!assignment.due_date) return false;
    if (assignment.status === 'completed' || assignment.status === 'cancelled') return false;
    return new Date(assignment.due_date) < new Date();
  };

  const getDaysUntilDue = (dueDate: string | undefined): number | null => {
    if (!dueDate) return null;
    const due = new Date(dueDate);
    const now = new Date();
    const diffTime = due.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Loading assignments...</span>
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
          onClick={loadAssignments}
          className="mt-4 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 rounded-md transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header with filter */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">My Training Assignments</h2>
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={includeCompleted}
            onChange={(e) => setIncludeCompleted(e.target.checked)}
            className="rounded border-gray-300"
          />
          Show completed
        </label>
      </div>

      {/* Assignment list */}
      {assignments.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No assignments</h3>
          <p className="mt-1 text-sm text-gray-500">
            You don&apos;t have any pending training assignments.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {assignments.map((assignment) => {
            const status = isOverdue(assignment) ? 'overdue' : assignment.status;
            const statusStyle = STATUS_STYLES[status as AssignmentStatus];
            const daysUntilDue = getDaysUntilDue(assignment.due_date);

            return (
              <div
                key={assignment.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base font-medium text-gray-900 truncate">
                      {assignment.page?.title || 'Untitled Document'}
                    </h3>
                    <div className="mt-1 flex items-center gap-3 text-sm text-gray-500">
                      <span>Assigned: {formatDate(assignment.assigned_at)}</span>
                      {assignment.due_date && (
                        <>
                          <span className="text-gray-300">|</span>
                          <span
                            className={
                              daysUntilDue !== null && daysUntilDue <= 3 && status !== 'completed'
                                ? daysUntilDue < 0
                                  ? 'text-red-600 font-medium'
                                  : 'text-amber-600 font-medium'
                                : ''
                            }
                          >
                            Due: {formatDate(assignment.due_date)}
                            {daysUntilDue !== null &&
                              daysUntilDue >= 0 &&
                              daysUntilDue <= 3 &&
                              status !== 'completed' && (
                                <span className="ml-1">
                                  ({daysUntilDue === 0 ? 'Today' : `${daysUntilDue} day${daysUntilDue !== 1 ? 's' : ''}`})
                                </span>
                              )}
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 ml-4">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${statusStyle.bg} ${statusStyle.text}`}
                    >
                      {statusStyle.label}
                    </span>

                    {onStartAssignment &&
                      (assignment.status === 'assigned' || assignment.status === 'in_progress') && (
                        <button
                          onClick={() => onStartAssignment(assignment)}
                          className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                        >
                          {assignment.status === 'assigned' ? 'Start' : 'Continue'}
                        </button>
                      )}
                  </div>
                </div>

                {/* Completed info */}
                {assignment.status === 'completed' && assignment.completed_at && (
                  <div className="mt-3 pt-3 border-t border-gray-100 text-sm text-gray-500">
                    <svg
                      className="inline-block w-4 h-4 text-green-500 mr-1"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Completed on {formatDate(assignment.completed_at)}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default AssignmentList;
