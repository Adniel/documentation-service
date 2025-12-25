/**
 * DraftWorkflowActions - Context-sensitive action buttons for change request workflow.
 *
 * Displays available actions based on the current status and user role.
 */

import { useState } from 'react';
import type { ChangeRequest, ChangeRequestStatus } from '../../types';
import { changeRequestApi } from '../../lib/api';

interface DraftWorkflowActionsProps {
  draft: ChangeRequest;
  currentUserId: string;
  onUpdate: (updatedDraft: ChangeRequest) => void;
  onError: (error: string) => void;
}

type ActionButton = {
  label: string;
  action: () => Promise<void>;
  variant: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  requiresComment?: boolean;
};

export function DraftWorkflowActions({
  draft,
  currentUserId,
  onUpdate,
  onError,
}: DraftWorkflowActionsProps) {
  const [loading, setLoading] = useState(false);
  const [showCommentDialog, setShowCommentDialog] = useState(false);
  const [comment, setComment] = useState('');
  const [pendingAction, setPendingAction] = useState<(() => Promise<void>) | null>(null);

  const isAuthor = draft.author_id === currentUserId;
  const isReviewer = draft.reviewer_id === currentUserId;

  const executeAction = async (action: () => Promise<void>) => {
    setLoading(true);
    try {
      await action();
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Action failed');
    } finally {
      setLoading(false);
    }
  };

  const executeWithComment = (action: (comment: string) => Promise<void>) => {
    setPendingAction(() => async () => {
      await action(comment);
      setShowCommentDialog(false);
      setComment('');
      setPendingAction(null);
    });
    setShowCommentDialog(true);
  };

  // Build available actions based on status and role
  const getActions = (): ActionButton[] => {
    const actions: ActionButton[] = [];

    switch (draft.status as ChangeRequestStatus) {
      case 'draft':
        if (isAuthor) {
          actions.push({
            label: 'Submit for Review',
            variant: 'primary',
            action: async () => {
              const updated = await changeRequestApi.submit(draft.id);
              onUpdate(updated);
            },
          });
          actions.push({
            label: 'Cancel Draft',
            variant: 'danger',
            action: async () => {
              await changeRequestApi.cancel(draft.id);
              onUpdate({ ...draft, status: 'cancelled' });
            },
          });
        }
        break;

      case 'submitted':
      case 'in_review':
        if (!isAuthor) {
          actions.push({
            label: 'Approve',
            variant: 'success',
            action: async () => {
              const updated = await changeRequestApi.approve(draft.id, { comment });
              onUpdate(updated);
            },
          });
          actions.push({
            label: 'Request Changes',
            variant: 'warning',
            requiresComment: true,
            action: async () => {
              executeWithComment(async (c) => {
                const updated = await changeRequestApi.requestChanges(draft.id, { comment: c });
                onUpdate(updated);
              });
            },
          });
          actions.push({
            label: 'Reject',
            variant: 'danger',
            action: async () => {
              const updated = await changeRequestApi.reject(draft.id, { comment });
              onUpdate(updated);
            },
          });
        }
        if (isAuthor) {
          actions.push({
            label: 'Cancel',
            variant: 'secondary',
            action: async () => {
              await changeRequestApi.cancel(draft.id);
              onUpdate({ ...draft, status: 'cancelled' });
            },
          });
        }
        break;

      case 'changes_requested':
        if (isAuthor) {
          actions.push({
            label: 'Resubmit for Review',
            variant: 'primary',
            action: async () => {
              const updated = await changeRequestApi.submit(draft.id);
              onUpdate(updated);
            },
          });
          actions.push({
            label: 'Cancel Draft',
            variant: 'danger',
            action: async () => {
              await changeRequestApi.cancel(draft.id);
              onUpdate({ ...draft, status: 'cancelled' });
            },
          });
        }
        break;

      case 'approved':
        actions.push({
          label: 'Publish',
          variant: 'success',
          action: async () => {
            const updated = await changeRequestApi.publish(draft.id);
            onUpdate(updated);
          },
        });
        break;

      // published, rejected, cancelled - no actions available
      default:
        break;
    }

    return actions;
  };

  const actions = getActions();

  if (actions.length === 0) {
    return null;
  }

  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-700',
    success: 'bg-green-600 hover:bg-green-700 text-white',
    warning: 'bg-yellow-500 hover:bg-yellow-600 text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
  };

  return (
    <>
      <div className="flex items-center gap-2 flex-wrap">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={() => {
              if (action.requiresComment) {
                action.action();
              } else {
                executeAction(action.action);
              }
            }}
            disabled={loading}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              variantClasses[action.variant]
            }`}
          >
            {loading ? 'Processing...' : action.label}
          </button>
        ))}
      </div>

      {/* Comment dialog for actions requiring comment */}
      {showCommentDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Add Comment
            </h3>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Provide feedback on what changes are needed..."
              className="w-full h-32 px-3 py-2 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
            <div className="mt-4 flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowCommentDialog(false);
                  setComment('');
                  setPendingAction(null);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (pendingAction) {
                    executeAction(pendingAction);
                  }
                }}
                disabled={!comment.trim() || loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
              >
                {loading ? 'Submitting...' : 'Submit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default DraftWorkflowActions;
