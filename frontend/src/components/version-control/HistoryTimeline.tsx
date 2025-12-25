/**
 * HistoryTimeline - Visual timeline of document version history and change requests.
 *
 * Displays commits, drafts, and workflow events in a chronological timeline.
 */

import { useState, useEffect } from 'react';
import type { VersionHistoryEntry, ChangeRequest, ChangeRequestStatus } from '../../types';
import { contentApi, changeRequestApi } from '../../lib/api';

interface HistoryTimelineProps {
  pageId: string;
  onVersionSelect?: (sha: string) => void;
  onDraftSelect?: (draft: ChangeRequest) => void;
}

interface TimelineItem {
  type: 'commit' | 'draft';
  timestamp: string;
  data: VersionHistoryEntry | ChangeRequest;
}

const statusColors: Record<ChangeRequestStatus, string> = {
  draft: 'bg-slate-600 text-slate-200',
  submitted: 'bg-blue-600/30 text-blue-300',
  in_review: 'bg-yellow-600/30 text-yellow-300',
  changes_requested: 'bg-orange-600/30 text-orange-300',
  approved: 'bg-green-600/30 text-green-300',
  published: 'bg-emerald-600/30 text-emerald-300',
  rejected: 'bg-red-600/30 text-red-300',
  cancelled: 'bg-slate-600 text-slate-400',
};

const statusLabels: Record<ChangeRequestStatus, string> = {
  draft: 'Draft',
  submitted: 'Submitted',
  in_review: 'In Review',
  changes_requested: 'Changes Requested',
  approved: 'Approved',
  published: 'Published',
  rejected: 'Rejected',
  cancelled: 'Cancelled',
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function shortenSha(sha: string): string {
  return sha.substring(0, 7);
}

export function HistoryTimeline({
  pageId,
  onVersionSelect,
  onDraftSelect,
}: HistoryTimelineProps) {
  const [history, setHistory] = useState<VersionHistoryEntry[]>([]);
  const [drafts, setDrafts] = useState<ChangeRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSha, setSelectedSha] = useState<string | null>(null);
  const [showDrafts, setShowDrafts] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const [historyData, draftsData] = await Promise.all([
          contentApi.getHistory(pageId),
          changeRequestApi.list(pageId),
        ]);

        setHistory(historyData);
        setDrafts(draftsData.items);
      } catch (err) {
        setError('Failed to load history');
        console.error('Error loading history:', err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [pageId]);

  // Merge and sort timeline items
  const timelineItems: TimelineItem[] = [
    ...history.map((h) => ({
      type: 'commit' as const,
      timestamp: h.timestamp,
      data: h,
    })),
    ...(showDrafts
      ? drafts.map((d) => ({
          type: 'draft' as const,
          timestamp: d.created_at,
          data: d,
        }))
      : []),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  const handleVersionClick = (sha: string) => {
    setSelectedSha(sha);
    onVersionSelect?.(sha);
  };

  const handleDraftClick = (draft: ChangeRequest) => {
    onDraftSelect?.(draft);
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-4">
              <div className="w-3 h-3 bg-slate-600 rounded-full" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-slate-600 rounded w-3/4" />
                <div className="h-3 bg-slate-600 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-400 bg-red-500/10 rounded-md border border-red-500/30">
        {error}
      </div>
    );
  }

  return (
    <div className="p-4" data-testid="history-timeline">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-200">Version History</h3>
        <label className="flex items-center gap-2 text-sm text-slate-400">
          <input
            type="checkbox"
            checked={showDrafts}
            onChange={(e) => setShowDrafts(e.target.checked)}
            className="rounded border-slate-500 bg-slate-700"
          />
          Show drafts
        </label>
      </div>

      {timelineItems.length === 0 ? (
        <p className="text-sm text-slate-500">No history available</p>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-[5px] top-2 bottom-2 w-0.5 bg-slate-600" />

          <ul className="space-y-4">
            {timelineItems.map((item, index) => {
              if (item.type === 'commit') {
                const commit = item.data as VersionHistoryEntry;
                const isSelected = selectedSha === commit.sha;

                return (
                  <li key={commit.sha} className="relative pl-6">
                    {/* Timeline dot */}
                    <div
                      className={`absolute left-0 top-1.5 w-3 h-3 rounded-full border-2 ${
                        isSelected
                          ? 'bg-blue-500 border-blue-500'
                          : 'bg-slate-700 border-slate-500'
                      }`}
                    />

                    <button
                      onClick={() => handleVersionClick(commit.sha)}
                      className={`w-full text-left p-2 rounded-md transition-colors ${
                        isSelected
                          ? 'bg-blue-600/20 border border-blue-500/50'
                          : 'hover:bg-slate-700/50'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <code className="text-xs px-1.5 py-0.5 bg-slate-600 text-slate-200 rounded font-mono">
                          {shortenSha(commit.sha)}
                        </code>
                        {index === 0 && (
                          <span className="text-xs px-1.5 py-0.5 bg-green-600/30 text-green-300 rounded">
                            Latest
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-slate-200 line-clamp-2">
                        {commit.message}
                      </p>
                      <p className="mt-1 text-xs text-slate-400">
                        {commit.author_name} &middot; {formatDate(commit.timestamp)}
                      </p>
                    </button>
                  </li>
                );
              } else {
                const draft = item.data as ChangeRequest;

                return (
                  <li key={draft.id} className="relative pl-6">
                    {/* Timeline dot (diamond for drafts) */}
                    <div className="absolute left-0 top-1.5 w-3 h-3 bg-blue-500 rotate-45 border-2 border-blue-500" />

                    <button
                      onClick={() => handleDraftClick(draft)}
                      className="w-full text-left p-2 rounded-md border border-dashed border-blue-500/50 hover:bg-blue-600/10 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-blue-400">
                          CR-{draft.number.toString().padStart(4, '0')}
                        </span>
                        <span
                          className={`text-xs px-1.5 py-0.5 rounded ${
                            statusColors[draft.status]
                          }`}
                        >
                          {statusLabels[draft.status]}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-slate-200 line-clamp-1">
                        {draft.title}
                      </p>
                      <p className="mt-1 text-xs text-slate-400">
                        {draft.author_name || 'Unknown'} &middot;{' '}
                        {formatDate(draft.created_at)}
                      </p>
                    </button>
                  </li>
                );
              }
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

export default HistoryTimeline;
