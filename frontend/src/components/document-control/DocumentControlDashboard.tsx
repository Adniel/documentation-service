/**
 * DocumentControlDashboard - Admin dashboard for document lifecycle management.
 *
 * Shows document statistics by status and provides overview of document control.
 *
 * Sprint 9.5: Admin UI
 */

import { useState, useEffect, useCallback } from 'react';
import { contentApi, type DocumentControlDashboard as DashboardData, type PageStatus } from '../../lib/api';

interface DocumentControlDashboardProps {
  onViewDocuments?: (status: PageStatus) => void;
}

const STATUS_CONFIG: Record<PageStatus, { label: string; color: string; bgColor: string }> = {
  draft: { label: 'Draft', color: 'text-gray-700', bgColor: 'bg-gray-100' },
  in_review: { label: 'In Review', color: 'text-blue-700', bgColor: 'bg-blue-100' },
  approved: { label: 'Approved', color: 'text-purple-700', bgColor: 'bg-purple-100' },
  effective: { label: 'Effective', color: 'text-green-700', bgColor: 'bg-green-100' },
  obsolete: { label: 'Obsolete', color: 'text-orange-700', bgColor: 'bg-orange-100' },
  archived: { label: 'Archived', color: 'text-gray-500', bgColor: 'bg-gray-50' },
};

export function DocumentControlDashboard({ onViewDocuments }: DocumentControlDashboardProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DashboardData | null>(null);

  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const dashboardData = await contentApi.getControlDashboard();
      setData(dashboardData);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-700">{error}</p>
        <button
          onClick={loadDashboard}
          className="mt-2 text-sm text-red-600 hover:text-red-800"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!data) return null;

  const statusOrder: PageStatus[] = ['draft', 'in_review', 'approved', 'effective', 'obsolete', 'archived'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Document Control</h2>
          <p className="text-sm text-gray-500 mt-1">
            Overview of document lifecycle status across the platform
          </p>
        </div>
        <button
          onClick={loadDashboard}
          className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="text-3xl font-bold text-gray-900">{data.total_documents}</div>
          <div className="text-sm text-gray-500 mt-1">Total Documents</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="text-3xl font-bold text-green-600">{data.effective_documents}</div>
          <div className="text-sm text-gray-500 mt-1">Effective</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="text-3xl font-bold text-blue-600">{data.pending_reviews}</div>
          <div className="text-sm text-gray-500 mt-1">Pending Review</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="text-3xl font-bold text-gray-600">{data.draft_documents}</div>
          <div className="text-sm text-gray-500 mt-1">In Draft</div>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Documents by Status</h3>

        {/* Visual Bar Chart */}
        <div className="space-y-3">
          {statusOrder.map((status) => {
            const count = data.by_status[status] || 0;
            const percentage = data.total_documents > 0
              ? (count / data.total_documents) * 100
              : 0;
            const config = STATUS_CONFIG[status];

            return (
              <div key={status} className="flex items-center gap-4">
                <div className="w-24 text-sm font-medium text-gray-600">{config.label}</div>
                <div className="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      status === 'draft' ? 'bg-gray-400' :
                      status === 'in_review' ? 'bg-blue-500' :
                      status === 'approved' ? 'bg-purple-500' :
                      status === 'effective' ? 'bg-green-500' :
                      status === 'obsolete' ? 'bg-orange-500' :
                      'bg-gray-300'
                    }`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <div className="w-16 text-right">
                  <span className="text-sm font-semibold text-gray-900">{count}</span>
                  <span className="text-xs text-gray-500 ml-1">
                    ({percentage.toFixed(0)}%)
                  </span>
                </div>
                {onViewDocuments && count > 0 && (
                  <button
                    onClick={() => onViewDocuments(status)}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    View
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Lifecycle Flow Diagram */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Lifecycle Flow</h3>
        <div className="flex items-center justify-between text-sm">
          {statusOrder.map((status, index) => {
            const config = STATUS_CONFIG[status];
            const count = data.by_status[status] || 0;

            return (
              <div key={status} className="flex items-center">
                <div className="flex flex-col items-center">
                  <div
                    className={`w-16 h-16 rounded-lg flex items-center justify-center ${config.bgColor}`}
                  >
                    <span className={`text-lg font-bold ${config.color}`}>{count}</span>
                  </div>
                  <span className={`mt-2 text-xs font-medium ${config.color}`}>
                    {config.label}
                  </span>
                </div>
                {index < statusOrder.length - 1 && (
                  <div className="mx-2">
                    <svg className="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <p className="mt-4 text-xs text-gray-500 text-center">
          Documents progress through lifecycle states from Draft to Archived.
          Each transition is logged for compliance with ISO 9001 and 21 CFR Part 11.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-3 gap-4">
          {data.pending_reviews > 0 && (
            <button
              onClick={() => onViewDocuments?.('in_review')}
              className="p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors text-left"
            >
              <div className="text-2xl font-bold text-blue-600">{data.pending_reviews}</div>
              <div className="text-sm text-blue-700 mt-1">Documents awaiting review</div>
              <div className="text-xs text-blue-600 mt-2">Click to review</div>
            </button>
          )}
          {data.draft_documents > 0 && (
            <button
              onClick={() => onViewDocuments?.('draft')}
              className="p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors text-left"
            >
              <div className="text-2xl font-bold text-gray-600">{data.draft_documents}</div>
              <div className="text-sm text-gray-700 mt-1">Documents in draft</div>
              <div className="text-xs text-gray-600 mt-2">Click to view</div>
            </button>
          )}
          {(data.by_status['obsolete'] || 0) > 0 && (
            <button
              onClick={() => onViewDocuments?.('obsolete')}
              className="p-4 bg-orange-50 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors text-left"
            >
              <div className="text-2xl font-bold text-orange-600">{data.by_status['obsolete']}</div>
              <div className="text-sm text-orange-700 mt-1">Obsolete documents</div>
              <div className="text-xs text-orange-600 mt-2">Consider archiving</div>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default DocumentControlDashboard;
