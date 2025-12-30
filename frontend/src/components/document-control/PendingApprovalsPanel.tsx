/**
 * PendingApprovalsPanel - View and act on pending approvals.
 *
 * Displays:
 * - Documents awaiting the current user's approval
 * - Approval history
 * - Quick approve/reject actions
 *
 * Sprint 9.5: Admin UI
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentControlApi } from '../../lib/api';

interface PendingApproval {
  id: string;
  number: string;
  title: string;
  page_title: string;
  approval_status: string;
  current_step: number | null;
  submitted_at: string | null;
}

export function PendingApprovalsPanel() {
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [comment, setComment] = useState('');
  const [showRejectDialog, setShowRejectDialog] = useState(false);

  // Fetch pending approvals
  const { data, isLoading, error } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: () => documentControlApi.getPendingApprovals(),
  });

  const pendingApprovals = (data?.change_requests || []) as PendingApproval[];

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: async ({ crId, comment }: { crId: string; comment?: string }) => {
      await documentControlApi.recordApprovalDecision(crId, 'approved', comment);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] });
      setSelectedId(null);
      setComment('');
    },
  });

  // Reject mutation
  const rejectMutation = useMutation({
    mutationFn: async ({ crId, comment }: { crId: string; comment: string }) => {
      await documentControlApi.recordApprovalDecision(crId, 'rejected', comment);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-approvals'] });
      setSelectedId(null);
      setComment('');
      setShowRejectDialog(false);
    },
  });

  const handleApprove = (crId: string) => {
    approveMutation.mutate({ crId, comment: comment || undefined });
  };

  const handleReject = () => {
    if (!selectedId || !comment.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }
    rejectMutation.mutate({ crId: selectedId, comment: comment.trim() });
  };

  if (isLoading) {
    return (
      <div className="p-6 text-center text-gray-500">
        <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2" />
        Loading pending approvals...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center text-red-500">
        Error loading pending approvals: {(error as Error).message}
      </div>
    );
  }

  if (pendingApprovals.length === 0) {
    return (
      <div className="p-8 text-center">
        <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-gray-500">No pending approvals</p>
        <p className="text-sm text-gray-400 mt-1">You're all caught up!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">
          Pending Approvals ({pendingApprovals.length})
        </h3>
      </div>

      {/* List */}
      <div className="space-y-3">
        {pendingApprovals.map((approval) => (
          <div
            key={approval.id}
            className={`border rounded-lg p-4 transition ${
              selectedId === approval.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {approval.page_title || approval.title}
                  </h4>
                  <span className="text-xs text-gray-500 font-mono">
                    {approval.number}
                  </span>
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  {approval.submitted_at
                    ? `Submitted ${new Date(approval.submitted_at).toLocaleDateString()}`
                    : 'Pending submission'}
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <span className="inline-flex items-center px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
                    Step {approval.current_step || 1}
                  </span>
                  <span className="text-xs text-gray-400">
                    {approval.approval_status}
                  </span>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center gap-2 ml-4">
                <button
                  onClick={() => handleApprove(approval.id)}
                  disabled={approveMutation.isPending}
                  className="px-3 py-1.5 text-sm text-green-700 bg-green-100 hover:bg-green-200 rounded-md transition disabled:opacity-50"
                >
                  Approve
                </button>
                <button
                  onClick={() => {
                    setSelectedId(approval.id);
                    setShowRejectDialog(true);
                  }}
                  className="px-3 py-1.5 text-sm text-red-700 bg-red-100 hover:bg-red-200 rounded-md transition"
                >
                  Reject
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Reject Dialog */}
      {showRejectDialog && selectedId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setShowRejectDialog(false)}
          />
          <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Reject Approval
            </h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reason for Rejection *
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Please provide a reason for rejecting this document..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            {rejectMutation.isError && (
              <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-md">
                {(rejectMutation.error as Error).message}
              </div>
            )}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowRejectDialog(false);
                  setComment('');
                }}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                disabled={!comment.trim() || rejectMutation.isPending}
                className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-md transition disabled:opacity-50"
              >
                {rejectMutation.isPending ? 'Rejecting...' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error messages */}
      {approveMutation.isError && (
        <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md">
          {(approveMutation.error as Error).message}
        </div>
      )}
    </div>
  );
}

export default PendingApprovalsPanel;
