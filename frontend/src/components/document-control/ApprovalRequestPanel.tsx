/**
 * ApprovalRequestPanel - Request approval for a document change.
 *
 * This panel allows users to:
 * - Select an approval matrix
 * - Submit a change request for approval
 * - View current approval status
 *
 * Sprint 9.5: Admin UI
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentControlApi, changeRequestApi } from '../../lib/api';

interface ApprovalRequestPanelProps {
  pageId: string;
  pageTitle: string;
  changeRequestId?: string;
  onClose?: () => void;
  onSubmitted?: () => void;
}

export function ApprovalRequestPanel({
  pageId,
  pageTitle,
  changeRequestId,
  onClose,
  onSubmitted,
}: ApprovalRequestPanelProps) {
  const queryClient = useQueryClient();
  const [selectedMatrixId, setSelectedMatrixId] = useState<string>('');
  const [comment, setComment] = useState('');

  // Fetch available approval matrices
  const { data: matricesResponse, isLoading: loadingMatrices } = useQuery({
    queryKey: ['approval-matrices'],
    queryFn: () => documentControlApi.listApprovalMatrices(),
  });

  const matrices = matricesResponse?.matrices || [];

  // Submit for approval mutation
  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!changeRequestId) {
        throw new Error('No change request to submit');
      }
      // Submit change request for approval
      await changeRequestApi.submit(changeRequestId, {
        approval_matrix_id: selectedMatrixId || undefined,
        comment: comment || undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['change-request', changeRequestId] });
      queryClient.invalidateQueries({ queryKey: ['page', pageId] });
      onSubmitted?.();
      onClose?.();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitMutation.mutate();
  };

  const selectedMatrix = matrices.find((m) => m.id === selectedMatrixId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-medium text-gray-900">Request Approval</h3>
        <p className="mt-1 text-sm text-gray-500">
          Submit "{pageTitle}" for approval review
        </p>
      </div>

      {/* Matrix Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Approval Workflow
        </label>
        {loadingMatrices ? (
          <div className="text-sm text-gray-500">Loading workflows...</div>
        ) : matrices.length === 0 ? (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-md text-sm text-amber-700">
            No approval matrices configured. Contact an administrator.
          </div>
        ) : (
          <select
            value={selectedMatrixId}
            onChange={(e) => setSelectedMatrixId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
          >
            <option value="">Auto-select based on document type</option>
            {matrices.map((matrix) => (
              <option key={matrix.id} value={matrix.id}>
                {matrix.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Selected Matrix Details */}
      {selectedMatrix && (
        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            {selectedMatrix.name}
          </h4>
          {selectedMatrix.description && (
            <p className="text-sm text-gray-500 mb-3">{selectedMatrix.description}</p>
          )}
          <div className="space-y-2">
            <div className="text-xs text-gray-500 uppercase tracking-wide">
              Approval Steps
            </div>
            <div className="flex flex-wrap gap-2">
              {selectedMatrix.steps.map((step, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-full"
                >
                  <span className="w-5 h-5 flex items-center justify-center bg-blue-100 text-blue-700 text-xs rounded-full">
                    {step.step_order}
                  </span>
                  <span className="text-sm text-gray-700">{step.name}</span>
                </div>
              ))}
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {selectedMatrix.require_sequential
                ? 'Sequential approval required'
                : 'Parallel approval allowed'}
            </div>
          </div>
        </div>
      )}

      {/* Comment */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Comment (optional)
        </label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Add any notes for the approvers..."
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
        />
      </div>

      {/* Error */}
      {submitMutation.isError && (
        <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md">
          {(submitMutation.error as Error).message}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition"
          >
            Cancel
          </button>
        )}
        <button
          onClick={handleSubmit}
          disabled={submitMutation.isPending || !changeRequestId}
          className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md transition disabled:opacity-50"
        >
          {submitMutation.isPending ? 'Submitting...' : 'Submit for Approval'}
        </button>
      </div>
    </div>
  );
}

export default ApprovalRequestPanel;
