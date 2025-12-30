/**
 * AssignTrainingDialog - Assign training to users for a document.
 *
 * Allows admins to:
 * - Select users to assign training
 * - Set due dates
 * - Send bulk assignments
 *
 * Sprint 9.5: Admin UI
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { learningApi, documentControlApi } from '../../lib/api';

interface AssignTrainingDialogProps {
  pageId: string;
  pageTitle: string;
  isOpen: boolean;
  onClose: () => void;
  onAssigned?: () => void;
}

export function AssignTrainingDialog({
  pageId,
  pageTitle,
  isOpen,
  onClose,
  onAssigned,
}: AssignTrainingDialogProps) {
  const queryClient = useQueryClient();
  const [selectedUserIds, setSelectedUserIds] = useState<Set<string>>(new Set());
  const [dueDate, setDueDate] = useState('');
  const [notes, setNotes] = useState('');
  const [selectAll, setSelectAll] = useState(false);

  // Fetch users
  const { data: users = [], isLoading: loadingUsers } = useQuery({
    queryKey: ['users'],
    queryFn: documentControlApi.listUsers,
    enabled: isOpen,
  });

  // Fetch existing assignments
  const { data: existingAssignments } = useQuery({
    queryKey: ['assignments', pageId],
    queryFn: () => learningApi.listAssignments({ page_id: pageId, limit: 100 }),
    enabled: isOpen,
  });

  const assignedUserIds = new Set(
    existingAssignments?.assignments.map((a) => a.user_id) || []
  );

  // Filter out already assigned users
  const availableUsers = users.filter((u) => !assignedUserIds.has(u.id) && u.is_active);

  // Bulk assign mutation
  const assignMutation = useMutation({
    mutationFn: async () => {
      if (selectedUserIds.size === 0) {
        throw new Error('Please select at least one user');
      }

      await learningApi.createBulkAssignments({
        page_id: pageId,
        user_ids: Array.from(selectedUserIds),
        due_date: dueDate || undefined,
        notes: notes || undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments', pageId] });
      onAssigned?.();
      onClose();
      // Reset form
      setSelectedUserIds(new Set());
      setDueDate('');
      setNotes('');
      setSelectAll(false);
    },
  });

  const toggleUser = (userId: string) => {
    setSelectedUserIds((prev) => {
      const next = new Set(prev);
      if (next.has(userId)) {
        next.delete(userId);
      } else {
        next.add(userId);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedUserIds(new Set());
    } else {
      setSelectedUserIds(new Set(availableUsers.map((u) => u.id)));
    }
    setSelectAll(!selectAll);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    assignMutation.mutate();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Dialog */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-lg font-semibold text-gray-900">
            Assign Training
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Assign users to complete training for "{pageTitle}"
          </p>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* User Selection */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">
                Select Users ({selectedUserIds.size} selected)
              </label>
              <button
                type="button"
                onClick={handleSelectAll}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                {selectAll ? 'Deselect All' : 'Select All'}
              </button>
            </div>

            {loadingUsers ? (
              <div className="p-4 text-center text-gray-500">Loading users...</div>
            ) : availableUsers.length === 0 ? (
              <div className="p-4 text-center text-gray-500 bg-gray-50 rounded-md">
                All users are already assigned to this training
              </div>
            ) : (
              <div className="border border-gray-300 rounded-md max-h-64 overflow-y-auto">
                {availableUsers.map((user) => (
                  <label
                    key={user.id}
                    className={`flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 border-b last:border-b-0 ${
                      selectedUserIds.has(user.id) ? 'bg-blue-50' : ''
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedUserIds.has(user.id)}
                      onChange={() => toggleUser(user.id)}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900">
                        {user.full_name}
                      </div>
                      <div className="text-xs text-gray-500">{user.email}</div>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Due Date (optional)
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500">
              Leave empty for no deadline
            </p>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any notes for the assignees..."
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Error */}
          {assignMutation.isError && (
            <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md">
              {(assignMutation.error as Error).message}
            </div>
          )}

          {/* Summary */}
          {selectedUserIds.size > 0 && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-700">
              <strong>{selectedUserIds.size}</strong> user(s) will be assigned
              to complete training
              {dueDate && ` by ${new Date(dueDate).toLocaleDateString()}`}.
            </div>
          )}
        </form>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3 flex-shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={selectedUserIds.size === 0 || assignMutation.isPending}
            className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md transition disabled:opacity-50"
          >
            {assignMutation.isPending ? 'Assigning...' : `Assign ${selectedUserIds.size} User(s)`}
          </button>
        </div>
      </div>
    </div>
  );
}

export default AssignTrainingDialog;
