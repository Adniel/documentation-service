/**
 * SyncStatusBadge - Display Git sync status as a badge.
 *
 * Sprint 13: Git Remote Support
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { gitApi } from '../../lib/api';

interface SyncStatusBadgeProps {
  organizationId: string;
  showSyncButton?: boolean;
  compact?: boolean;
}

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  synced: { bg: 'bg-green-100', text: 'text-green-700', label: 'Synced' },
  pending: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Pending' },
  error: { bg: 'bg-red-100', text: 'text-red-700', label: 'Error' },
  conflict: { bg: 'bg-orange-100', text: 'text-orange-700', label: 'Conflict' },
  not_configured: { bg: 'bg-gray-100', text: 'text-gray-500', label: 'Not Configured' },
};

export function SyncStatusBadge({
  organizationId,
  showSyncButton = false,
  compact = false,
}: SyncStatusBadgeProps) {
  const queryClient = useQueryClient();

  const { data: status, isLoading } = useQuery({
    queryKey: ['git-sync-status', organizationId],
    queryFn: () => gitApi.getSyncStatus(organizationId),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const syncMutation = useMutation({
    mutationFn: () => gitApi.triggerSync(organizationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['git-sync-status', organizationId] });
      queryClient.invalidateQueries({ queryKey: ['git-sync-history', organizationId] });
    },
  });

  if (isLoading) {
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-500">
        Loading...
      </span>
    );
  }

  if (!status) {
    return null;
  }

  const syncStatus = status.sync_status || 'not_configured';
  const style = STATUS_STYLES[syncStatus] || STATUS_STYLES.not_configured;

  if (compact) {
    return (
      <span
        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${style.bg} ${style.text}`}
        title={`Git sync: ${style.label}`}
      >
        {syncStatus === 'synced' && (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        )}
        {syncStatus === 'pending' && (
          <svg className="w-3 h-3 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {syncStatus === 'error' && (
          <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        )}
        Git
      </span>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2">
        <span
          className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${style.bg} ${style.text}`}
        >
          {style.label}
        </span>
        {status.divergence && status.divergence.remote_exists && (
          <span className="text-xs text-gray-500">
            {status.divergence.ahead > 0 && `${status.divergence.ahead} ahead`}
            {status.divergence.ahead > 0 && status.divergence.behind > 0 && ', '}
            {status.divergence.behind > 0 && `${status.divergence.behind} behind`}
          </span>
        )}
      </div>

      {showSyncButton && status.sync_enabled && (
        <button
          onClick={() => syncMutation.mutate()}
          disabled={syncMutation.isPending || syncStatus === 'pending'}
          className="inline-flex items-center px-3 py-1 text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-md disabled:opacity-50"
        >
          {syncMutation.isPending ? (
            <>
              <svg className="w-3 h-3 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Syncing...
            </>
          ) : (
            <>
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Sync Now
            </>
          )}
        </button>
      )}

      {status.last_sync_at && (
        <span className="text-xs text-gray-400">
          Last sync: {new Date(status.last_sync_at).toLocaleString()}
        </span>
      )}
    </div>
  );
}

export default SyncStatusBadge;
