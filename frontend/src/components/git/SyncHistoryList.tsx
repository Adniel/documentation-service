/**
 * SyncHistoryList - Display Git sync event history.
 *
 * Sprint 13: Git Remote Support
 */

import { useQuery } from '@tanstack/react-query';
import { gitApi, type SyncEvent } from '../../lib/api';

interface SyncHistoryListProps {
  organizationId: string;
  limit?: number;
}

const EVENT_TYPE_LABELS: Record<string, string> = {
  push: 'Push',
  pull: 'Pull',
  fetch: 'Fetch',
  clone: 'Clone',
  conflict: 'Conflict',
  error: 'Error',
};

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  success: { bg: 'bg-green-100', text: 'text-green-700' },
  failed: { bg: 'bg-red-100', text: 'text-red-700' },
  conflict: { bg: 'bg-orange-100', text: 'text-orange-700' },
  in_progress: { bg: 'bg-blue-100', text: 'text-blue-700' },
};

const DIRECTION_ICONS: Record<string, string> = {
  outbound: '\u2191', // Up arrow
  inbound: '\u2193', // Down arrow
};

function formatDuration(seconds: number): string {
  if (seconds < 1) return '<1s';
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
}

function SyncEventRow({ event }: { event: SyncEvent }) {
  const statusStyle = STATUS_STYLES[event.status] || STATUS_STYLES.failed;

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-4 py-3 whitespace-nowrap">
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusStyle.bg} ${statusStyle.text}`}
          >
            {event.status}
          </span>
          <span className="text-gray-500">
            {DIRECTION_ICONS[event.direction]}
          </span>
        </div>
      </td>
      <td className="px-4 py-3 whitespace-nowrap">
        <span className="text-sm text-gray-900">
          {EVENT_TYPE_LABELS[event.event_type] || event.event_type}
        </span>
      </td>
      <td className="px-4 py-3 whitespace-nowrap">
        <span className="text-sm font-mono text-gray-600">
          {event.branch_name}
        </span>
      </td>
      <td className="px-4 py-3 whitespace-nowrap">
        {event.commit_sha_after ? (
          <span className="text-xs font-mono text-gray-500">
            {event.commit_sha_after.substring(0, 7)}
          </span>
        ) : (
          <span className="text-gray-400">-</span>
        )}
      </td>
      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
        {event.trigger_source || '-'}
      </td>
      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
        {event.duration_seconds !== undefined && event.duration_seconds !== null
          ? formatDuration(event.duration_seconds)
          : '-'}
      </td>
      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
        {new Date(event.created_at).toLocaleString()}
      </td>
      <td className="px-4 py-3">
        {event.error_message && (
          <span
            className="text-xs text-red-600 truncate max-w-xs block"
            title={event.error_message}
          >
            {event.error_message}
          </span>
        )}
      </td>
    </tr>
  );
}

export function SyncHistoryList({
  organizationId,
  limit = 20,
}: SyncHistoryListProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['git-sync-history', organizationId, limit],
    queryFn: () => gitApi.getSyncHistory(organizationId, limit),
  });

  if (isLoading) {
    return (
      <div className="p-8 text-center text-gray-500">
        Loading sync history...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-500">
        Failed to load sync history
      </div>
    );
  }

  if (!data || data.events.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <svg
          className="w-12 h-12 mx-auto text-gray-300 mb-3"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        <p>No sync events yet</p>
        <p className="text-sm mt-1">Sync operations will appear here</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="text-sm font-medium text-gray-900">
          Sync History ({data.total} total)
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Type
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Branch
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Commit
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Trigger
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Duration
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Time
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                Error
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.events.map((event) => (
              <SyncEventRow key={event.id} event={event} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default SyncHistoryList;
