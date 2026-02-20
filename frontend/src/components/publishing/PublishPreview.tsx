/**
 * Publish Preview Component
 *
 * Sprint D: Integrated Access Control
 *
 * Shows pre-publish report with audience breakdown:
 * - Pages visible to each clearance level
 * - Classification distribution
 * - Warnings about visibility issues
 */

import React, { useState, useEffect } from 'react';
import {
  Eye,
  EyeOff,
  Shield,
  AlertTriangle,
  Info,
  AlertCircle,
  Users,
  FileText,
  Lock,
  Unlock,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  CheckCircle,
  XCircle,
} from 'lucide-react';

interface AudienceBreakdown {
  audience_name: string;
  clearance_level: number;
  page_count: number;
  page_ids: string[];
}

interface PublishWarning {
  level: 'info' | 'warning' | 'error';
  page_id: string | null;
  page_title: string | null;
  message: string;
}

interface PublishReport {
  site_id: string;
  site_slug: string;
  site_visibility: string;
  generated_at: string;
  total_pages: number;
  publishable_pages: number;
  audiences: AudienceBreakdown[];
  classification_counts: Record<string, number>;
  warnings: PublishWarning[];
  acl_restricted_pages: string[];
}

interface PublishPreviewProps {
  siteId: string;
  siteSlug: string;
  onPublish?: () => void;
  onClose?: () => void;
}

const VISIBILITY_LABELS: Record<string, string> = {
  public: 'Public',
  authenticated: 'Authenticated',
  restricted: 'Restricted',
};

const WARNING_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  info: Info,
  warning: AlertTriangle,
  error: AlertCircle,
};

const WARNING_COLORS: Record<string, string> = {
  info: 'text-blue-500 bg-blue-50 border-blue-200',
  warning: 'text-amber-500 bg-amber-50 border-amber-200',
  error: 'text-red-500 bg-red-50 border-red-200',
};

export function PublishPreview({
  siteId,
  siteSlug,
  onPublish,
  onClose,
}: PublishPreviewProps) {
  const [report, setReport] = useState<PublishReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedAudiences, setExpandedAudiences] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadReport();
  }, [siteId]);

  async function loadReport() {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/s/${siteSlug}/publish-report`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to load publish report');

      const data = await response.json();
      setReport(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load report');
    } finally {
      setLoading(false);
    }
  }

  function toggleAudienceExpand(clearance: number) {
    setExpandedAudiences((prev) => {
      const next = new Set(prev);
      if (next.has(clearance)) {
        next.delete(clearance);
      } else {
        next.add(clearance);
      }
      return next;
    });
  }

  function getVisibilityIcon(visibility: string) {
    switch (visibility) {
      case 'public':
        return <Unlock className="w-5 h-5 text-green-500" />;
      case 'authenticated':
        return <Users className="w-5 h-5 text-blue-500" />;
      case 'restricted':
        return <Lock className="w-5 h-5 text-amber-500" />;
      default:
        return <Shield className="w-5 h-5 text-gray-500" />;
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 flex items-center justify-center">
        <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-red-600">
          <AlertCircle className="w-8 h-8 mx-auto mb-2" />
          <p>{error}</p>
          <button
            onClick={loadReport}
            className="mt-4 px-4 py-2 bg-gray-100 rounded hover:bg-gray-200"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!report) return null;

  const hasErrors = report.warnings.some((w) => w.level === 'error');
  const hasWarnings = report.warnings.some((w) => w.level === 'warning');

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Eye className="w-5 h-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">
              Pre-Publish Report
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {getVisibilityIcon(report.site_visibility)}
            <span className="text-sm font-medium">
              {VISIBILITY_LABELS[report.site_visibility] || report.site_visibility}
            </span>
          </div>
        </div>
        <p className="mt-1 text-sm text-gray-500">
          Review what different audiences will see when this site is published
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <FileText className="w-4 h-4" />
              Total Pages
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {report.total_pages}
            </p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-green-600 text-sm mb-1">
              <CheckCircle className="w-4 h-4" />
              Publishable
            </div>
            <p className="text-2xl font-bold text-green-700">
              {report.publishable_pages}
            </p>
          </div>
          <div className="bg-amber-50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-amber-600 text-sm mb-1">
              <Lock className="w-4 h-4" />
              ACL Restricted
            </div>
            <p className="text-2xl font-bold text-amber-700">
              {report.acl_restricted_pages.length}
            </p>
          </div>
        </div>

        {/* Classification Distribution */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Classification Distribution
          </h3>
          <div className="space-y-2">
            {Object.entries(report.classification_counts).map(([name, count]) => (
              <div key={name} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-24 capitalize">
                  {name}
                </span>
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all"
                    style={{
                      width: `${(count / report.publishable_pages) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-900 w-12 text-right">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Audience Breakdown */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
            <Users className="w-4 h-4" />
            Audience Breakdown
          </h3>
          <div className="space-y-2">
            {report.audiences.map((audience) => (
              <div
                key={audience.clearance_level}
                className="border border-gray-200 rounded-lg"
              >
                <button
                  onClick={() => toggleAudienceExpand(audience.clearance_level)}
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    {expandedAudiences.has(audience.clearance_level) ? (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                    <span className="font-medium text-gray-900">
                      {audience.audience_name}
                    </span>
                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                      Clearance {audience.clearance_level}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {audience.clearance_level === 0 &&
                      report.site_visibility === 'public' && (
                        <Eye className="w-4 h-4 text-green-500" />
                      )}
                    <span className="text-sm font-medium text-gray-700">
                      {audience.page_count} pages
                    </span>
                  </div>
                </button>
                {expandedAudiences.has(audience.clearance_level) && (
                  <div className="px-4 pb-3 pt-1 border-t border-gray-100">
                    {audience.page_ids.length === 0 ? (
                      <p className="text-sm text-gray-500 italic">
                        No pages visible to this audience
                      </p>
                    ) : (
                      <ul className="text-sm text-gray-600 space-y-1">
                        {audience.page_ids.slice(0, 10).map((id) => (
                          <li key={id} className="truncate">
                            {id}
                          </li>
                        ))}
                        {audience.page_ids.length > 10 && (
                          <li className="text-gray-400">
                            ... and {audience.page_ids.length - 10} more
                          </li>
                        )}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Warnings */}
        {report.warnings.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Warnings & Notes ({report.warnings.length})
            </h3>
            <div className="space-y-2">
              {report.warnings.map((warning, idx) => {
                const Icon = WARNING_ICONS[warning.level] || Info;
                const colors = WARNING_COLORS[warning.level] || WARNING_COLORS.info;
                return (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border flex items-start gap-3 ${colors}`}
                  >
                    <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div>
                      {warning.page_title && (
                        <p className="font-medium text-gray-900">
                          {warning.page_title}
                        </p>
                      )}
                      <p className="text-sm">{warning.message}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          {hasErrors ? (
            <>
              <XCircle className="w-4 h-4 text-red-500" />
              <span className="text-red-600">
                Resolve errors before publishing
              </span>
            </>
          ) : hasWarnings ? (
            <>
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <span className="text-amber-600">
                Review warnings before publishing
              </span>
            </>
          ) : (
            <>
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-green-600">Ready to publish</span>
            </>
          )}
        </div>
        <div className="flex items-center gap-3">
          {onClose && (
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-md"
            >
              Cancel
            </button>
          )}
          {onPublish && (
            <button
              onClick={onPublish}
              disabled={hasErrors}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Eye className="w-4 h-4" />
              Publish Site
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default PublishPreview;
