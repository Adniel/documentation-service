/**
 * AuditLogPanel - View and export audit trail for an organization.
 *
 * Sprint B: Admin UI Completion
 */

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { auditApi } from '../../lib/api';
import type { AuditEvent, AuditQueryParams } from '../../types';

interface AuditLogPanelProps {
  organizationId: string;
}

const EVENT_TYPE_LABELS: Record<string, string> = {
  'auth.login': 'Login',
  'auth.logout': 'Logout',
  'auth.failed': 'Failed Login',
  'auth.password_changed': 'Password Changed',
  'content.created': 'Content Created',
  'content.updated': 'Content Updated',
  'content.deleted': 'Content Deleted',
  'content.viewed': 'Content Viewed',
  'access.granted': 'Access Granted',
  'access.revoked': 'Access Revoked',
  'access.denied': 'Access Denied',
  'workflow.submitted': 'Submitted for Review',
  'workflow.approved': 'Approved',
  'workflow.rejected': 'Rejected',
  'workflow.published': 'Published',
  'signature.created': 'Signature Created',
  'signature.verified': 'Signature Verified',
};

const EVENT_TYPE_COLORS: Record<string, string> = {
  'auth.login': 'bg-green-100 text-green-700',
  'auth.logout': 'bg-gray-100 text-gray-700',
  'auth.failed': 'bg-red-100 text-red-700',
  'content.created': 'bg-blue-100 text-blue-700',
  'content.updated': 'bg-yellow-100 text-yellow-700',
  'content.deleted': 'bg-red-100 text-red-700',
  'access.granted': 'bg-green-100 text-green-700',
  'access.revoked': 'bg-orange-100 text-orange-700',
  'access.denied': 'bg-red-100 text-red-700',
  'workflow.approved': 'bg-green-100 text-green-700',
  'workflow.rejected': 'bg-red-100 text-red-700',
  'signature.created': 'bg-purple-100 text-purple-700',
};

function formatEventType(type: string): string {
  return EVENT_TYPE_LABELS[type] || type.replace(/[._]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function getEventTypeColor(type: string): string {
  return EVENT_TYPE_COLORS[type] || 'bg-gray-100 text-gray-700';
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString();
}

export function AuditLogPanel({ organizationId }: AuditLogPanelProps) {
  // Filter state
  const [eventType, setEventType] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [page, setPage] = useState(0);
  const [expandedEvent, setExpandedEvent] = useState<string | null>(null);
  const pageSize = 50;

  // Build query params
  const queryParams: AuditQueryParams = {
    limit: pageSize,
    offset: page * pageSize,
  };
  if (eventType) queryParams.event_type = eventType;
  if (startDate) queryParams.start_date = new Date(startDate).toISOString();
  if (endDate) queryParams.end_date = new Date(endDate).toISOString();

  // Fetch events
  const { data: eventsData, isLoading, error } = useQuery({
    queryKey: ['audit-events', organizationId, queryParams],
    queryFn: () => auditApi.listOrgEvents(organizationId, queryParams),
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['audit-stats', organizationId],
    queryFn: () => auditApi.getOrgStats(organizationId),
  });

  // Verify chain mutation
  const verifyMutation = useMutation({
    mutationFn: () => auditApi.verifyOrgChain(organizationId),
  });

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: (format: 'csv' | 'json') => {
      const params = {
        format,
        start_date: startDate ? new Date(startDate).toISOString() : new Date(0).toISOString(),
        end_date: endDate ? new Date(endDate).toISOString() : new Date().toISOString(),
        include_details: true,
      };
      return auditApi.exportOrgAudit(organizationId, params);
    },
    onSuccess: (blob, format) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-export-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
  });

  const handleExport = (format: 'csv' | 'json') => {
    exportMutation.mutate(format);
  };

  const toggleEventDetails = (eventId: string) => {
    setExpandedEvent(expandedEvent === eventId ? null : eventId);
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Failed to load audit events. Please try again.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-2xl font-bold text-gray-900">{stats?.total_events || 0}</div>
          <div className="text-sm text-gray-500">Total Events</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-2xl font-bold text-gray-900">{stats?.events_today || 0}</div>
          <div className="text-sm text-gray-500">Events Today</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-2xl font-bold text-gray-900">{stats?.unique_actors || 0}</div>
          <div className="text-sm text-gray-500">Unique Actors</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900">Chain Status</div>
              {verifyMutation.data ? (
                <div className={`text-sm ${verifyMutation.data.is_valid ? 'text-green-600' : 'text-red-600'}`}>
                  {verifyMutation.data.is_valid ? 'Valid' : 'Invalid'}
                </div>
              ) : (
                <div className="text-sm text-gray-500">Not verified</div>
              )}
            </div>
            <button
              onClick={() => verifyMutation.mutate()}
              disabled={verifyMutation.isPending}
              className="px-3 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100 disabled:opacity-50"
            >
              {verifyMutation.isPending ? 'Verifying...' : 'Verify'}
            </button>
          </div>
        </div>
      </div>

      {/* Filters and Export */}
      <div className="flex flex-wrap items-center gap-4 bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Event Type</label>
          <select
            value={eventType}
            onChange={(e) => { setEventType(e.target.value); setPage(0); }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-sm"
          >
            <option value="">All Types</option>
            {Object.entries(EVENT_TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
        <div className="min-w-[180px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => { setStartDate(e.target.value); setPage(0); }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
        <div className="min-w-[180px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => { setEndDate(e.target.value); setPage(0); }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
        <div className="flex items-end gap-2">
          <button
            onClick={() => handleExport('csv')}
            disabled={exportMutation.isPending}
            className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Export CSV
          </button>
          <button
            onClick={() => handleExport('json')}
            disabled={exportMutation.isPending}
            className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Export JSON
          </button>
        </div>
      </div>

      {/* Events Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : eventsData?.events.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No audit events found for the selected filters.
          </div>
        ) : (
          <>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Event
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Resource
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {eventsData?.events.map((event: AuditEvent) => (
                  <>
                    <tr key={event.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(event.timestamp)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getEventTypeColor(event.event_type)}`}>
                          {formatEventType(event.event_type)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{event.actor_email || 'System'}</div>
                        {event.actor_ip && (
                          <div className="text-xs text-gray-500">{event.actor_ip}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {event.resource_type && (
                          <>
                            <div className="text-sm text-gray-900">
                              {event.resource_name || event.resource_id?.slice(0, 8)}
                            </div>
                            <div className="text-xs text-gray-500">{event.resource_type}</div>
                          </>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        {event.details && Object.keys(event.details).length > 0 && (
                          <button
                            onClick={() => toggleEventDetails(event.id)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            {expandedEvent === event.id ? 'Hide' : 'Show'}
                          </button>
                        )}
                      </td>
                    </tr>
                    {expandedEvent === event.id && event.details && (
                      <tr key={`${event.id}-details`}>
                        <td colSpan={5} className="px-6 py-4 bg-gray-50">
                          <pre className="text-xs text-gray-700 overflow-auto max-h-48">
                            {JSON.stringify(event.details, null, 2)}
                          </pre>
                          <div className="mt-2 text-xs text-gray-400">
                            Hash: {event.event_hash.slice(0, 16)}...
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="bg-gray-50 px-6 py-3 flex items-center justify-between border-t border-gray-200">
              <div className="text-sm text-gray-500">
                Showing {page * pageSize + 1} to {Math.min((page + 1) * pageSize, eventsData?.total || 0)} of {eventsData?.total || 0} events
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={!eventsData?.has_more}
                  className="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
