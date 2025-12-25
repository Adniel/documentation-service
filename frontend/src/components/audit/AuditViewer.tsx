/**
 * AuditViewer - Admin component for viewing and exporting audit trail.
 *
 * 21 CFR §11.10(e) compliant audit trail viewer with:
 * - Filterable event list
 * - Hash chain verification
 * - Export to CSV/JSON
 */

import { useState, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';

interface AuditEvent {
  id: string;
  event_type: string;
  timestamp: string;
  actor_id: string | null;
  actor_email: string | null;
  actor_ip: string | null;
  resource_type: string | null;
  resource_id: string | null;
  resource_name: string | null;
  details: Record<string, unknown> | null;
  event_hash: string;
}

interface AuditStats {
  total_events: number;
  events_by_type: Record<string, number>;
  events_today: number;
  events_this_week: number;
  unique_actors: number;
  chain_head_hash: string | null;
  oldest_event: string | null;
  newest_event: string | null;
}

interface ChainVerification {
  is_valid: boolean;
  total_events: number;
  verified_events: number;
  first_invalid_event_id: string | null;
  first_invalid_reason: string | null;
  verification_timestamp: string;
  chain_head_hash: string | null;
  verification_duration_ms: number;
}

interface AuditFilters {
  event_type?: string;
  resource_type?: string;
  start_date?: string;
  end_date?: string;
}

const EVENT_TYPE_COLORS: Record<string, string> = {
  'content.created': 'bg-green-100 text-green-800',
  'content.updated': 'bg-blue-100 text-blue-800',
  'content.deleted': 'bg-red-100 text-red-800',
  'content.viewed': 'bg-gray-100 text-gray-800',
  'workflow.submitted': 'bg-yellow-100 text-yellow-800',
  'workflow.approved': 'bg-green-100 text-green-800',
  'workflow.rejected': 'bg-red-100 text-red-800',
  'workflow.published': 'bg-purple-100 text-purple-800',
  'access.granted': 'bg-teal-100 text-teal-800',
  'access.revoked': 'bg-orange-100 text-orange-800',
  'access.denied': 'bg-red-100 text-red-800',
  'auth.login': 'bg-blue-100 text-blue-800',
  'auth.logout': 'bg-gray-100 text-gray-800',
  'auth.failed': 'bg-red-100 text-red-800',
  'signature.created': 'bg-indigo-100 text-indigo-800',
  'signature.initiated': 'bg-indigo-100 text-indigo-800',
};

function formatTimestamp(ts: string): string {
  const date = new Date(ts);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export function AuditViewer() {
  const [filters, setFilters] = useState<AuditFilters>({});
  const [page, setPage] = useState(0);
  const limit = 25;

  // Fetch audit stats
  const { data: stats } = useQuery<AuditStats>({
    queryKey: ['audit-stats'],
    queryFn: async () => {
      const response = await fetch('/api/v1/audit/stats', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      if (!response.ok) throw new Error('Failed to fetch stats');
      return response.json();
    },
  });

  // Fetch audit events
  const { data: eventsData, isLoading } = useQuery({
    queryKey: ['audit-events', filters, page],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: String(limit),
        offset: String(page * limit),
      });
      if (filters.event_type) params.set('event_type', filters.event_type);
      if (filters.resource_type) params.set('resource_type', filters.resource_type);
      if (filters.start_date) params.set('start_date', filters.start_date);
      if (filters.end_date) params.set('end_date', filters.end_date);

      const response = await fetch(`/api/v1/audit/events?${params}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      if (!response.ok) throw new Error('Failed to fetch events');
      return response.json();
    },
  });

  // Verify chain mutation
  const verifyMutation = useMutation<ChainVerification>({
    mutationFn: async () => {
      const response = await fetch('/api/v1/audit/verify', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ max_events: 10000 }),
      });
      if (!response.ok) throw new Error('Verification failed');
      return response.json();
    },
  });

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: async (format: 'csv' | 'json') => {
      const now = new Date();
      const startDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const endDate = now;

      const response = await fetch('/api/v1/audit/export', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format,
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString(),
        }),
      });
      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_export.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  const handleFilterChange = useCallback((key: keyof AuditFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }));
    setPage(0);
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Trail</h1>
          <p className="text-sm text-gray-500">
            21 CFR Part 11 compliant audit log with hash chain verification
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => verifyMutation.mutate()}
            disabled={verifyMutation.isPending}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {verifyMutation.isPending ? 'Verifying...' : 'Verify Chain'}
          </button>
          <button
            onClick={() => exportMutation.mutate('csv')}
            disabled={exportMutation.isPending}
            className="px-4 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
          >
            Export CSV
          </button>
          <button
            onClick={() => exportMutation.mutate('json')}
            disabled={exportMutation.isPending}
            className="px-4 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
          >
            Export JSON
          </button>
        </div>
      </div>

      {/* Verification Result */}
      {verifyMutation.data && (
        <div
          className={`p-4 rounded-lg ${
            verifyMutation.data.is_valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {verifyMutation.data.is_valid ? (
              <>
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="font-medium text-green-800">Chain Verified</span>
              </>
            ) : (
              <>
                <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="font-medium text-red-800">Chain Integrity Issue</span>
              </>
            )}
          </div>
          <p className="mt-1 text-sm text-gray-600">
            Verified {verifyMutation.data.verified_events} of {verifyMutation.data.total_events} events
            in {verifyMutation.data.verification_duration_ms.toFixed(0)}ms
          </p>
          {verifyMutation.data.first_invalid_reason && (
            <p className="mt-1 text-sm text-red-600">{verifyMutation.data.first_invalid_reason}</p>
          )}
        </div>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="p-4 bg-white rounded-lg shadow">
            <div className="text-sm text-gray-500">Total Events</div>
            <div className="text-2xl font-bold">{stats.total_events.toLocaleString()}</div>
          </div>
          <div className="p-4 bg-white rounded-lg shadow">
            <div className="text-sm text-gray-500">Today</div>
            <div className="text-2xl font-bold">{stats.events_today}</div>
          </div>
          <div className="p-4 bg-white rounded-lg shadow">
            <div className="text-sm text-gray-500">This Week</div>
            <div className="text-2xl font-bold">{stats.events_this_week}</div>
          </div>
          <div className="p-4 bg-white rounded-lg shadow">
            <div className="text-sm text-gray-500">Unique Actors</div>
            <div className="text-2xl font-bold">{stats.unique_actors}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-4 p-4 bg-white rounded-lg shadow">
        <select
          value={filters.event_type || ''}
          onChange={(e) => handleFilterChange('event_type', e.target.value)}
          className="px-3 py-2 border rounded-md"
        >
          <option value="">All Event Types</option>
          {stats &&
            Object.keys(stats.events_by_type).map((type) => (
              <option key={type} value={type}>
                {type} ({stats.events_by_type[type]})
              </option>
            ))}
        </select>
        <select
          value={filters.resource_type || ''}
          onChange={(e) => handleFilterChange('resource_type', e.target.value)}
          className="px-3 py-2 border rounded-md"
        >
          <option value="">All Resource Types</option>
          <option value="page">Page</option>
          <option value="space">Space</option>
          <option value="change_request">Change Request</option>
          <option value="session">Session</option>
        </select>
      </div>

      {/* Events Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Timestamp
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Event Type
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Actor
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Resource
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Hash
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  Loading...
                </td>
              </tr>
            ) : eventsData?.events?.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No events found
                </td>
              </tr>
            ) : (
              eventsData?.events?.map((event: AuditEvent) => (
                <tr key={event.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {formatTimestamp(event.timestamp)}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        EVENT_TYPE_COLORS[event.event_type] || 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {event.event_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {event.actor_email || 'System'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {event.resource_name || event.resource_type || '-'}
                  </td>
                  <td className="px-4 py-3 text-xs font-mono text-gray-400">
                    {event.event_hash.slice(0, 12)}...
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {eventsData && (
          <div className="px-4 py-3 bg-gray-50 border-t flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Showing {page * limit + 1} to {Math.min((page + 1) * limit, eventsData.total)} of{' '}
              {eventsData.total} events
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!eventsData.has_more}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-100 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AuditViewer;
