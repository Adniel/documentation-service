/**
 * DraftListPanel - List of change requests (drafts) for a page.
 *
 * Shows all drafts with filtering and allows navigation to draft detail.
 */

import { useState, useEffect } from 'react';
import type { ChangeRequest, ChangeRequestStatus } from '../../types';
import { changeRequestApi } from '../../lib/api';
import { DraftStatusBadge } from './DraftStatusBadge';

interface DraftListPanelProps {
  pageId: string;
  onDraftSelect: (draft: ChangeRequest) => void;
  onCreateDraft: () => void;
}

const statusFilters: { value: ChangeRequestStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'in_review', label: 'In Review' },
  { value: 'changes_requested', label: 'Changes Requested' },
  { value: 'approved', label: 'Approved' },
  { value: 'published', label: 'Published' },
];

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

export function DraftListPanel({
  pageId,
  onDraftSelect,
  onCreateDraft,
}: DraftListPanelProps) {
  const [drafts, setDrafts] = useState<ChangeRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<ChangeRequestStatus | 'all'>('all');

  useEffect(() => {
    async function loadDrafts() {
      setLoading(true);
      setError(null);

      try {
        const params = statusFilter !== 'all' ? { status: statusFilter } : undefined;
        const response = await changeRequestApi.list(pageId, params);
        setDrafts(response.items);
      } catch (err) {
        setError('Failed to load change requests');
        console.error('Error loading change requests:', err);
      } finally {
        setLoading(false);
      }
    }

    loadDrafts();
  }, [pageId, statusFilter]);

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-md" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-600 bg-red-50 rounded-md">
        {error}
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-900">Change Requests</h3>
        <button
          onClick={onCreateDraft}
          className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
        >
          New
        </button>
      </div>

      {/* Filter */}
      <div className="p-4 border-b">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ChangeRequestStatus | 'all')}
          className="w-full px-3 py-1.5 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {statusFilters.map((filter) => (
            <option key={filter.value} value={filter.value}>
              {filter.label}
            </option>
          ))}
        </select>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {drafts.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <p className="text-sm">No change requests found</p>
            <p className="text-xs mt-1">
              {statusFilter !== 'all'
                ? 'Try changing the filter'
                : 'Create a new change request to propose edits'}
            </p>
          </div>
        ) : (
          <ul className="divide-y">
            {drafts.map((draft) => (
              <li key={draft.id}>
                <button
                  onClick={() => onDraftSelect(draft)}
                  className="w-full text-left p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-gray-500">
                          CR-{draft.number.toString().padStart(4, '0')}
                        </span>
                        <DraftStatusBadge status={draft.status} />
                      </div>
                      <p className="mt-1 text-sm font-medium text-gray-900 truncate">
                        {draft.title}
                      </p>
                      {draft.description && (
                        <p className="mt-0.5 text-xs text-gray-500 line-clamp-2">
                          {draft.description}
                        </p>
                      )}
                    </div>
                    <span className="text-xs text-gray-400 whitespace-nowrap">
                      {formatRelativeTime(draft.updated_at)}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                    <span>{draft.author_name || 'Unknown'}</span>
                    {draft.reviewer_name && (
                      <>
                        <span>&middot;</span>
                        <span>Reviewer: {draft.reviewer_name}</span>
                      </>
                    )}
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default DraftListPanel;
