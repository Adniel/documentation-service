/**
 * DraftDetailPanel - Detailed view of a change request with diff and comments.
 */

import { useState, useEffect } from 'react';
import type { ChangeRequest, ChangeRequestComment, DiffResult } from '../../types';
import { changeRequestApi } from '../../lib/api';
import { DraftStatusBadge } from './DraftStatusBadge';
import { DraftWorkflowActions } from './DraftWorkflowActions';
import { DiffViewer } from './DiffViewer';

interface DraftDetailPanelProps {
  draft: ChangeRequest;
  currentUserId: string;
  onClose: () => void;
  onUpdate: (draft: ChangeRequest) => void;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function DraftDetailPanel({
  draft,
  currentUserId,
  onClose,
  onUpdate,
}: DraftDetailPanelProps) {
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [comments, setComments] = useState<ChangeRequestComment[]>([]);
  const [loadingDiff, setLoadingDiff] = useState(true);
  const [loadingComments, setLoadingComments] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'changes' | 'comments'>('changes');
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);

  useEffect(() => {
    async function loadDiff() {
      setLoadingDiff(true);
      try {
        const diffData = await changeRequestApi.getDiff(draft.id);
        setDiff(diffData);
      } catch (err) {
        console.error('Error loading diff:', err);
        setError('Failed to load changes');
      } finally {
        setLoadingDiff(false);
      }
    }

    async function loadComments() {
      setLoadingComments(true);
      try {
        const commentsData = await changeRequestApi.listComments(draft.id);
        setComments(commentsData);
      } catch (err) {
        console.error('Error loading comments:', err);
      } finally {
        setLoadingComments(false);
      }
    }

    loadDiff();
    loadComments();
  }, [draft.id]);

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    setSubmittingComment(true);
    try {
      const comment = await changeRequestApi.createComment(draft.id, {
        content: newComment.trim(),
      });
      setComments([...comments, comment]);
      setNewComment('');
    } catch (err) {
      console.error('Error adding comment:', err);
    } finally {
      setSubmittingComment(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="px-6 py-4 border-b flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-mono text-gray-500">
              CR-{draft.number.toString().padStart(4, '0')}
            </span>
            <DraftStatusBadge status={draft.status} size="md" />
          </div>
          <h2 className="text-lg font-semibold text-gray-900 truncate">
            {draft.title}
          </h2>
          {draft.description && (
            <p className="mt-1 text-sm text-gray-600">{draft.description}</p>
          )}
        </div>
        <button
          onClick={onClose}
          className="p-2 text-gray-400 hover:text-gray-600 rounded-md"
          aria-label="Close"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* Metadata */}
      <div className="px-6 py-3 border-b bg-gray-50 text-sm">
        <div className="flex flex-wrap gap-x-6 gap-y-1">
          <div>
            <span className="text-gray-500">Author:</span>{' '}
            <span className="text-gray-900">{draft.author_name || 'Unknown'}</span>
          </div>
          <div>
            <span className="text-gray-500">Created:</span>{' '}
            <span className="text-gray-900">{formatDate(draft.created_at)}</span>
          </div>
          {draft.reviewer_name && (
            <div>
              <span className="text-gray-500">Reviewer:</span>{' '}
              <span className="text-gray-900">{draft.reviewer_name}</span>
            </div>
          )}
          {draft.reviewed_at && (
            <div>
              <span className="text-gray-500">Reviewed:</span>{' '}
              <span className="text-gray-900">{formatDate(draft.reviewed_at)}</span>
            </div>
          )}
          {draft.published_at && (
            <div>
              <span className="text-gray-500">Published:</span>{' '}
              <span className="text-gray-900">{formatDate(draft.published_at)}</span>
            </div>
          )}
        </div>
        {draft.review_comment && (
          <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
            <span className="font-medium text-yellow-800">Review comment:</span>{' '}
            <span className="text-yellow-900">{draft.review_comment}</span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-6 py-3 border-b">
        <DraftWorkflowActions
          draft={draft}
          currentUserId={currentUserId}
          onUpdate={onUpdate}
          onError={(err) => setError(err)}
        />
        {error && (
          <div className="mt-2 p-2 bg-red-50 text-red-700 text-sm rounded">
            {error}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="flex px-6">
          <button
            onClick={() => setActiveTab('changes')}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              activeTab === 'changes'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Changes
            {diff && (
              <span className="ml-1.5 text-xs">
                <span className="text-green-600">+{diff.additions}</span>
                {' / '}
                <span className="text-red-600">-{diff.deletions}</span>
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('comments')}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              activeTab === 'comments'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Comments
            {comments.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 text-xs bg-gray-200 rounded-full">
                {comments.length}
              </span>
            )}
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'changes' ? (
          <div className="p-6">
            {loadingDiff ? (
              <div className="animate-pulse space-y-2">
                <div className="h-4 bg-gray-200 rounded w-1/4" />
                <div className="h-64 bg-gray-100 rounded" />
              </div>
            ) : diff ? (
              <DiffViewer
                diff={diff}
                title={`Changes in ${draft.title}`}
              />
            ) : (
              <div className="text-center text-gray-500 py-8">
                No changes to display
              </div>
            )}
          </div>
        ) : (
          <div className="p-6">
            {/* Comments list */}
            {loadingComments ? (
              <div className="animate-pulse space-y-4">
                {[1, 2].map((i) => (
                  <div key={i} className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-1/4" />
                    <div className="h-16 bg-gray-100 rounded" />
                  </div>
                ))}
              </div>
            ) : comments.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                No comments yet
              </div>
            ) : (
              <ul className="space-y-4 mb-6">
                {comments.map((comment) => (
                  <li key={comment.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">
                        {comment.author_name || 'Unknown'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDate(comment.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      {comment.content}
                    </p>
                    {comment.file_path && (
                      <div className="mt-2 text-xs text-gray-500">
                        <code className="px-1 py-0.5 bg-gray-200 rounded">
                          {comment.file_path}
                          {comment.line_number && `:${comment.line_number}`}
                        </code>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}

            {/* Add comment */}
            <div className="mt-4">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                className="w-full h-24 px-3 py-2 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="mt-2 flex justify-end">
                <button
                  onClick={handleAddComment}
                  disabled={!newComment.trim() || submittingComment}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submittingComment ? 'Adding...' : 'Add Comment'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DraftDetailPanel;
