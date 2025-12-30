/**
 * LifecyclePanel - Document lifecycle management sidebar.
 *
 * Shows current status and allows transitions through lifecycle states.
 *
 * Sprint 9.5: Admin UI
 */

import { useState } from 'react';
import { contentApi, type PageStatus } from '../../lib/api';
import type { Page } from '../../types';

interface LifecyclePanelProps {
  page: Page;
  onStatusChanged?: (page: Page) => void;
}

// Valid transitions for each status
const VALID_TRANSITIONS: Record<PageStatus, { status: PageStatus; label: string; color: string }[]> = {
  draft: [
    { status: 'in_review', label: 'Submit for Review', color: 'blue' },
  ],
  in_review: [
    { status: 'approved', label: 'Approve', color: 'green' },
    { status: 'draft', label: 'Reject (Return to Draft)', color: 'red' },
  ],
  approved: [
    { status: 'effective', label: 'Make Effective', color: 'green' },
    { status: 'in_review', label: 'Request Changes', color: 'yellow' },
  ],
  effective: [
    { status: 'obsolete', label: 'Mark as Obsolete', color: 'orange' },
  ],
  obsolete: [
    { status: 'archived', label: 'Archive', color: 'gray' },
  ],
  archived: [],
};

// Status display configuration
const STATUS_CONFIG: Record<PageStatus, { label: string; color: string; bgColor: string; description: string }> = {
  draft: {
    label: 'Draft',
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    description: 'Document is being edited and not yet submitted for review.',
  },
  in_review: {
    label: 'In Review',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    description: 'Document is under review and pending approval.',
  },
  approved: {
    label: 'Approved',
    color: 'text-purple-700',
    bgColor: 'bg-purple-100',
    description: 'Document has been approved and is ready to become effective.',
  },
  effective: {
    label: 'Effective',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    description: 'Document is the current official version in use.',
  },
  obsolete: {
    label: 'Obsolete',
    color: 'text-orange-700',
    bgColor: 'bg-orange-100',
    description: 'Document has been superseded and is no longer in active use.',
  },
  archived: {
    label: 'Archived',
    color: 'text-gray-500',
    bgColor: 'bg-gray-50',
    description: 'Document has been archived and is retained for records only.',
  },
};

export function LifecyclePanel({ page, onStatusChanged }: LifecyclePanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTransitionDialog, setShowTransitionDialog] = useState(false);
  const [selectedTransition, setSelectedTransition] = useState<PageStatus | null>(null);
  const [reason, setReason] = useState('');
  const [effectiveDate, setEffectiveDate] = useState('');

  const currentStatus = page.status as PageStatus;
  const statusConfig = STATUS_CONFIG[currentStatus];
  const availableTransitions = VALID_TRANSITIONS[currentStatus] || [];

  const handleTransition = async () => {
    if (!selectedTransition || reason.length < 10) return;

    setLoading(true);
    setError(null);

    try {
      const updatedPage = await contentApi.transitionStatus(
        page.id,
        selectedTransition,
        reason,
        selectedTransition === 'effective' && effectiveDate ? effectiveDate : undefined
      );
      onStatusChanged?.(updatedPage);
      setShowTransitionDialog(false);
      setSelectedTransition(null);
      setReason('');
      setEffectiveDate('');
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string | { message?: string } } } };
      const detail = error.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (typeof detail === 'object' && detail?.message) {
        setError(detail.message);
      } else {
        setError('Failed to transition document status');
      }
    } finally {
      setLoading(false);
    }
  };

  const openTransitionDialog = (status: PageStatus) => {
    setSelectedTransition(status);
    setReason('');
    setEffectiveDate('');
    setError(null);
    setShowTransitionDialog(true);
  };

  const getTransitionLabel = (status: PageStatus): string => {
    const transition = availableTransitions.find((t) => t.status === status);
    return transition?.label || status;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-4">
      <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
        Document Lifecycle
      </h3>

      {/* Current Status */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1.5 text-sm font-medium rounded-full ${statusConfig.bgColor} ${statusConfig.color}`}
          >
            {statusConfig.label}
          </span>
        </div>
        <p className="text-xs text-gray-500">{statusConfig.description}</p>
      </div>

      {/* Lifecycle Diagram */}
      <div className="py-3 border-t border-b border-gray-100">
        <div className="flex items-center justify-between text-xs">
          {(['draft', 'in_review', 'approved', 'effective', 'obsolete', 'archived'] as PageStatus[]).map(
            (status, index) => (
              <div key={status} className="flex items-center">
                <div
                  className={`w-2 h-2 rounded-full ${
                    status === currentStatus
                      ? 'bg-blue-600 ring-2 ring-blue-200'
                      : ['draft', 'in_review', 'approved', 'effective', 'obsolete', 'archived']
                          .indexOf(currentStatus) >= index
                      ? 'bg-green-500'
                      : 'bg-gray-300'
                  }`}
                  title={STATUS_CONFIG[status].label}
                />
                {index < 5 && (
                  <div
                    className={`w-4 h-0.5 ${
                      ['draft', 'in_review', 'approved', 'effective', 'obsolete', 'archived']
                        .indexOf(currentStatus) > index
                        ? 'bg-green-500'
                        : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            )
          )}
        </div>
        <div className="flex justify-between mt-1 text-[10px] text-gray-400">
          <span>Draft</span>
          <span>Review</span>
          <span>Approved</span>
          <span>Effective</span>
          <span>Obsolete</span>
          <span>Archived</span>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Available Transitions */}
      {availableTransitions.length > 0 ? (
        <div className="space-y-2">
          <span className="text-xs font-medium text-gray-500">Available Actions</span>
          <div className="flex flex-col gap-2">
            {availableTransitions.map((transition) => (
              <button
                key={transition.status}
                onClick={() => openTransitionDialog(transition.status)}
                disabled={loading}
                className={`w-full px-3 py-2 text-sm font-medium rounded-md border transition-colors disabled:opacity-50 ${
                  transition.color === 'green'
                    ? 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100'
                    : transition.color === 'blue'
                    ? 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100'
                    : transition.color === 'yellow'
                    ? 'bg-yellow-50 border-yellow-200 text-yellow-700 hover:bg-yellow-100'
                    : transition.color === 'orange'
                    ? 'bg-orange-50 border-orange-200 text-orange-700 hover:bg-orange-100'
                    : transition.color === 'red'
                    ? 'bg-red-50 border-red-200 text-red-700 hover:bg-red-100'
                    : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {transition.label}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-xs text-gray-400 italic">
          No further transitions available. Document is in terminal state.
        </p>
      )}

      {/* Transition Dialog */}
      {showTransitionDialog && selectedTransition && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold text-gray-900">
                {getTransitionLabel(selectedTransition)}
              </h4>
              <button
                onClick={() => setShowTransitionDialog(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm">
                <span className={`px-2 py-1 rounded ${STATUS_CONFIG[currentStatus].bgColor} ${STATUS_CONFIG[currentStatus].color}`}>
                  {STATUS_CONFIG[currentStatus].label}
                </span>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                <span className={`px-2 py-1 rounded ${STATUS_CONFIG[selectedTransition].bgColor} ${STATUS_CONFIG[selectedTransition].color}`}>
                  {STATUS_CONFIG[selectedTransition].label}
                </span>
              </div>

              {/* Effective Date (only for "effective" transition) */}
              {selectedTransition === 'effective' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Effective Date (optional)
                  </label>
                  <input
                    type="date"
                    value={effectiveDate}
                    onChange={(e) => setEffectiveDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Leave empty to make effective immediately.
                  </p>
                </div>
              )}

              {/* Reason (required) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reason <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={3}
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    reason.length > 0 && reason.length < 10 ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Provide a reason for this status change (min 10 characters)..."
                />
                {reason.length > 0 && reason.length < 10 && (
                  <p className="mt-1 text-xs text-red-500">
                    Reason must be at least 10 characters ({10 - reason.length} more needed)
                  </p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  Required for ISO 9001 and 21 CFR Part 11 compliance.
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                onClick={() => setShowTransitionDialog(false)}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleTransition}
                disabled={loading || reason.length < 10}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
              >
                {loading && (
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                )}
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LifecyclePanel;
