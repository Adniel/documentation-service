/**
 * Usage Statistics Component
 *
 * Sprint C: MCP Integration
 *
 * Displays usage statistics for a service account.
 */

import { useState, useEffect } from 'react';
import { serviceAccountApi, type ServiceAccount, type UsageStatsResponse } from '../../lib/api';

interface UsageStatsProps {
  account: ServiceAccount;
  onClose?: () => void;
}

export function UsageStats({ account, onClose }: UsageStatsProps) {
  const [stats, setStats] = useState<UsageStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await serviceAccountApi.getUsage(account.id, days);
        setStats(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load usage statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [account.id, days]);

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const getSuccessRate = () => {
    if (!stats || stats.total_requests === 0) return 0;
    return Math.round((stats.successful_requests / stats.total_requests) * 100);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading usage statistics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{account.name}</h2>
            <p className="text-sm text-gray-500">Usage Statistics</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="m-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {stats && (
          <div className="p-6 space-y-6">
            {/* Period Selector */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                Last used: {formatDate(stats.last_used_at)}
              </p>
              <select
                value={days}
                onChange={(e) => setDays(parseInt(e.target.value))}
                className="rounded-md border border-gray-300 px-3 py-1 text-sm"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
                <option value={365}>Last year</option>
              </select>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-500">Total Requests</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats.total_requests.toLocaleString()}
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-green-600">Successful</p>
                <p className="text-2xl font-semibold text-green-700">
                  {stats.successful_requests.toLocaleString()}
                </p>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <p className="text-sm text-red-600">Failed</p>
                <p className="text-2xl font-semibold text-red-700">
                  {stats.failed_requests.toLocaleString()}
                </p>
              </div>
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-600">Avg Response</p>
                <p className="text-2xl font-semibold text-blue-700">
                  {stats.avg_response_time_ms}ms
                </p>
              </div>
            </div>

            {/* Success Rate */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-gray-700">Success Rate</p>
                <p className="text-sm font-semibold text-gray-900">{getSuccessRate()}%</p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    getSuccessRate() >= 95
                      ? 'bg-green-500'
                      : getSuccessRate() >= 80
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                  }`}
                  style={{ width: `${getSuccessRate()}%` }}
                ></div>
              </div>
            </div>

            {/* Operations Breakdown */}
            {Object.keys(stats.operations).length > 0 && (
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-3">Operations Breakdown</h3>
                <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                          Operation
                        </th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                          Count
                        </th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                          % of Total
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(stats.operations)
                        .sort(([, a], [, b]) => b - a)
                        .map(([operation, count]) => (
                          <tr key={operation}>
                            <td className="px-4 py-2 text-sm font-medium text-gray-900">
                              {operation}
                            </td>
                            <td className="px-4 py-2 text-sm text-gray-500 text-right">
                              {count.toLocaleString()}
                            </td>
                            <td className="px-4 py-2 text-sm text-gray-500 text-right">
                              {stats.total_requests > 0
                                ? Math.round((count / stats.total_requests) * 100)
                                : 0}
                              %
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Daily Usage Chart (simplified) */}
            {stats.daily_usage.length > 0 && (
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-3">Daily Usage</h3>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-end gap-1 h-32">
                    {stats.daily_usage.map((day, index) => {
                      const maxRequests = Math.max(...stats.daily_usage.map((d) => d.requests));
                      const height = maxRequests > 0 ? (day.requests / maxRequests) * 100 : 0;
                      const errorHeight =
                        day.requests > 0 ? (day.errors / day.requests) * height : 0;

                      return (
                        <div
                          key={day.date}
                          className="flex-1 flex flex-col justify-end relative group"
                          title={`${day.date}: ${day.requests} requests, ${day.errors} errors`}
                        >
                          <div
                            className="bg-blue-500 rounded-t relative"
                            style={{ height: `${height}%`, minHeight: day.requests > 0 ? '2px' : '0' }}
                          >
                            {errorHeight > 0 && (
                              <div
                                className="absolute bottom-0 left-0 right-0 bg-red-500 rounded-t"
                                style={{ height: `${errorHeight}%` }}
                              ></div>
                            )}
                          </div>
                          {index === 0 || index === stats.daily_usage.length - 1 ? (
                            <span className="text-xs text-gray-500 mt-1 block text-center truncate">
                              {new Date(day.date).toLocaleDateString(undefined, {
                                month: 'short',
                                day: 'numeric',
                              })}
                            </span>
                          ) : null}
                          {/* Tooltip */}
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                            <div className="bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
                              <div>{new Date(day.date).toLocaleDateString()}</div>
                              <div>{day.requests} requests</div>
                              {day.errors > 0 && <div className="text-red-300">{day.errors} errors</div>}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="flex items-center justify-center gap-4 mt-4 text-xs">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-blue-500 rounded"></div>
                      <span className="text-gray-600">Requests</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 bg-red-500 rounded"></div>
                      <span className="text-gray-600">Errors</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
