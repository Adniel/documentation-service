/**
 * CompletionReport - Admin training completion dashboard.
 *
 * Shows completion rates, overdue assignments, and allows drilling
 * into user/page-specific training reports. Includes export functionality.
 *
 * Sprint 9: Learning Module Basics
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  learningApi,
  type CompletionReportItem,
  type OverdueReport,
  type UserTrainingHistory,
  type PageTrainingReport,
} from '../../lib/api';

interface CompletionReportProps {
  onViewPage?: (pageId: string) => void;
  onViewUser?: (userId: string) => void;
}

type ReportTab = 'completion' | 'overdue' | 'user' | 'page';

export function CompletionReport({ onViewPage, onViewUser }: CompletionReportProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<ReportTab>('completion');
  const [exporting, setExporting] = useState(false);

  // Data states
  const [completionData, setCompletionData] = useState<CompletionReportItem[]>([]);
  const [overdueData, setOverdueData] = useState<OverdueReport | null>(null);
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [selectedPageId, setSelectedPageId] = useState<string>('');
  const [userHistory, setUserHistory] = useState<UserTrainingHistory | null>(null);
  const [pageReport, setPageReport] = useState<PageTrainingReport | null>(null);

  // Load completion data
  const loadCompletionData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await learningApi.getCompletionReport();
      setCompletionData(data);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load completion report.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Load overdue data
  const loadOverdueData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await learningApi.getOverdueReport();
      setOverdueData(data);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load overdue report.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Load user training history
  const loadUserHistory = useCallback(async () => {
    if (!selectedUserId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await learningApi.getUserTrainingHistory(selectedUserId);
      setUserHistory(data);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load user training history.');
    } finally {
      setLoading(false);
    }
  }, [selectedUserId]);

  // Load page training report
  const loadPageReport = useCallback(async () => {
    if (!selectedPageId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await learningApi.getPageTrainingReport(selectedPageId);
      setPageReport(data);
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to load page training report.');
    } finally {
      setLoading(false);
    }
  }, [selectedPageId]);

  // Load data based on active tab
  useEffect(() => {
    if (activeTab === 'completion') {
      loadCompletionData();
    } else if (activeTab === 'overdue') {
      loadOverdueData();
    }
  }, [activeTab, loadCompletionData, loadOverdueData]);

  // Note: User history and page reports are loaded manually via the "Load" button
  // to avoid triggering API calls on every keystroke

  // Handle export
  const handleExport = useCallback(
    async (format: 'json' | 'csv') => {
      setExporting(true);
      try {
        const request = {
          report_type: activeTab as 'completion' | 'overdue' | 'user' | 'page',
          format,
          ...(activeTab === 'user' && selectedUserId ? { user_id: selectedUserId } : {}),
          ...(activeTab === 'page' && selectedPageId ? { page_id: selectedPageId } : {}),
        };

        const result = await learningApi.exportReport(request);

        if (format === 'csv' && result instanceof Blob) {
          // Download CSV
          const url = URL.createObjectURL(result);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${activeTab}_report.csv`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        } else if (format === 'json') {
          // Download JSON
          const blob = new Blob([JSON.stringify(result, null, 2)], {
            type: 'application/json',
          });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${activeTab}_report.json`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        }
      } catch (err) {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || 'Failed to export report.');
      } finally {
        setExporting(false);
      }
    },
    [activeTab, selectedUserId, selectedPageId]
  );

  // Summary stats from completion data
  const summaryStats = useMemo(() => {
    if (!completionData.length) return null;
    const totalAssigned = completionData.reduce((sum, item) => sum + item.total_assigned, 0);
    const totalCompleted = completionData.reduce((sum, item) => sum + item.completed, 0);
    const totalOverdue = completionData.reduce((sum, item) => sum + item.overdue, 0);
    const avgCompletionRate =
      completionData.reduce((sum, item) => sum + item.completion_rate, 0) / completionData.length;

    return { totalAssigned, totalCompleted, totalOverdue, avgCompletionRate };
  }, [completionData]);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getStatusStyle = (status: string) => {
    const styles: Record<string, { bg: string; text: string }> = {
      assigned: { bg: 'bg-blue-100', text: 'text-blue-700' },
      in_progress: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
      completed: { bg: 'bg-green-100', text: 'text-green-700' },
      overdue: { bg: 'bg-red-100', text: 'text-red-700' },
      cancelled: { bg: 'bg-gray-100', text: 'text-gray-700' },
    };
    return styles[status] || styles.assigned;
  };

  // Render tabs
  const renderTabs = () => (
    <div className="border-b border-gray-200 mb-6">
      <nav className="-mb-px flex space-x-8">
        {[
          { id: 'completion', label: 'Completion Rates' },
          { id: 'overdue', label: 'Overdue' },
          { id: 'user', label: 'By User' },
          { id: 'page', label: 'By Page' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as ReportTab)}
            className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );

  // Render export buttons
  const renderExportButtons = () => (
    <div className="flex gap-2 mb-4">
      <button
        onClick={() => handleExport('json')}
        disabled={exporting}
        className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 transition-colors"
      >
        {exporting ? 'Exporting...' : 'Export JSON'}
      </button>
      <button
        onClick={() => handleExport('csv')}
        disabled={exporting}
        className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 transition-colors"
      >
        {exporting ? 'Exporting...' : 'Export CSV'}
      </button>
    </div>
  );

  // Render completion tab
  const renderCompletionTab = () => (
    <div>
      {summaryStats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-3xl font-bold text-gray-900">{summaryStats.totalAssigned}</div>
            <div className="text-sm text-gray-500">Total Assigned</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-3xl font-bold text-green-600">{summaryStats.totalCompleted}</div>
            <div className="text-sm text-gray-500">Completed</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-3xl font-bold text-red-600">{summaryStats.totalOverdue}</div>
            <div className="text-sm text-gray-500">Overdue</div>
          </div>
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-3xl font-bold text-blue-600">
              {summaryStats.avgCompletionRate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">Avg Completion Rate</div>
          </div>
        </div>
      )}

      {renderExportButtons()}

      {completionData.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No training data</h3>
          <p className="mt-1 text-sm text-gray-500">
            No learning assignments have been created yet.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Completed
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  In Progress
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Overdue
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Completion Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {completionData.map((item) => (
                <tr
                  key={item.page_id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => {
                    setSelectedPageId(item.page_id);
                    setActiveTab('page');
                  }}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{item.page_title}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                    {item.total_assigned}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-green-600 font-medium">
                    {item.completed}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-yellow-600">
                    {item.in_progress}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-red-600">
                    {item.overdue}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${item.completion_rate}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900">
                        {item.completion_rate.toFixed(1)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  // Render overdue tab
  const renderOverdueTab = () => (
    <div>
      {renderExportButtons()}

      {!overdueData || overdueData.total_overdue === 0 ? (
        <div className="text-center py-12 bg-green-50 rounded-lg border border-green-200">
          <svg
            className="mx-auto h-12 w-12 text-green-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-green-900">No overdue assignments</h3>
          <p className="mt-1 text-sm text-green-700">
            All assignments are on track. Great job!
          </p>
        </div>
      ) : (
        <>
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-3">
              <svg
                className="w-8 h-8 text-red-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <div>
                <div className="text-2xl font-bold text-red-800">{overdueData.total_overdue}</div>
                <div className="text-sm text-red-700">Overdue Assignments</div>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {overdueData.assignments.map((assignment) => (
              <div
                key={assignment.id}
                className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200"
              >
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">
                    {assignment.page?.title || 'Untitled Document'}
                  </div>
                  <div className="text-sm text-gray-500">
                    Assigned to: {assignment.user?.email || 'Unknown user'}
                  </div>
                  <div className="text-xs text-red-600">
                    Due: {assignment.due_date ? formatDate(assignment.due_date) : 'Not set'}
                  </div>
                </div>
                <div className="flex gap-2">
                  {onViewUser && assignment.user && (
                    <button
                      onClick={() => {
                        setSelectedUserId(assignment.user_id);
                        setActiveTab('user');
                      }}
                      className="px-3 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                    >
                      View User
                    </button>
                  )}
                  {onViewPage && (
                    <button
                      onClick={() => onViewPage(assignment.page_id)}
                      className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                    >
                      View Page
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );

  // Render user tab
  const renderUserTab = () => (
    <div>
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Enter user email or ID to view training history
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(e.target.value)}
            placeholder="e.g., user@example.com or UUID"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={loadUserHistory}
            disabled={!selectedUserId || loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Load
          </button>
        </div>
      </div>

      {userHistory && (
        <>
          {renderExportButtons()}

          <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-lg font-semibold text-blue-600">
                  {userHistory.user_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <div className="text-lg font-semibold text-gray-900">{userHistory.user_name}</div>
                <div className="text-sm text-gray-500">{userHistory.user_email}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">
                  {userHistory.total_assignments}
                </div>
                <div className="text-xs text-gray-500">Total</div>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{userHistory.completed}</div>
                <div className="text-xs text-gray-500">Completed</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">{userHistory.in_progress}</div>
                <div className="text-xs text-gray-500">In Progress</div>
              </div>
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">{userHistory.overdue}</div>
                <div className="text-xs text-gray-500">Overdue</div>
              </div>
            </div>
          </div>

          {userHistory.acknowledgments.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Acknowledgments</h3>
              <div className="space-y-3">
                {userHistory.acknowledgments.map((ack) => (
                  <div
                    key={ack.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="text-sm font-medium text-gray-900">{ack.page_version}</div>
                      <div className="text-xs text-gray-500">
                        Acknowledged: {formatDate(ack.acknowledged_at)}
                      </div>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        ack.is_valid ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {ack.is_valid ? 'Valid' : 'Expired'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );

  // Render page tab
  const renderPageTab = () => (
    <div>
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Enter page title, slug, or ID to view training report
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={selectedPageId}
            onChange={(e) => setSelectedPageId(e.target.value)}
            placeholder="e.g., First Page or UUID"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={loadPageReport}
            disabled={!selectedPageId || loading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Load
          </button>
        </div>
      </div>

      {pageReport && (
        <>
          {renderExportButtons()}

          <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">{pageReport.page_title}</h2>

            <div className="flex gap-4 mb-4">
              {pageReport.requires_training && (
                <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                  Training Required
                </span>
              )}
              {pageReport.has_assessment && (
                <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded">
                  Has Assessment
                </span>
              )}
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-3xl font-bold text-gray-900">{pageReport.total_assigned}</div>
                <div className="text-sm text-gray-500">Total Assigned</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-3xl font-bold text-green-600">{pageReport.completed}</div>
                <div className="text-sm text-gray-500">Completed</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-3xl font-bold text-blue-600">
                  {pageReport.completion_rate.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500">Completion Rate</div>
              </div>
            </div>
          </div>

          {pageReport.assignments.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Assigned
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pageReport.assignments.map((assignment) => {
                    const statusStyle = getStatusStyle(assignment.status);
                    return (
                      <tr key={assignment.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {assignment.user?.email || 'Unknown'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded ${statusStyle.bg} ${statusStyle.text}`}
                          >
                            {assignment.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {assignment.due_date ? formatDate(assignment.due_date) : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(assignment.assigned_at)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );

  // Loading state
  if (loading && !completionData.length && !overdueData && !userHistory && !pageReport) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Loading report...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-red-600 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <h3 className="font-medium text-red-800">Error</h3>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        </div>
        <button
          onClick={() => {
            setError(null);
            if (activeTab === 'completion') loadCompletionData();
            else if (activeTab === 'overdue') loadOverdueData();
            else if (activeTab === 'user') loadUserHistory();
            else if (activeTab === 'page') loadPageReport();
          }}
          className="mt-4 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 rounded-md transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Training Reports</h1>
      </div>

      {renderTabs()}

      {activeTab === 'completion' && renderCompletionTab()}
      {activeTab === 'overdue' && renderOverdueTab()}
      {activeTab === 'user' && renderUserTab()}
      {activeTab === 'page' && renderPageTab()}
    </div>
  );
}

export default CompletionReport;
