/**
 * MaskingPanel — AI-powered sensitive content detection.
 *
 * Shows detected sensitive matches with category badges,
 * confidence bars, and a "Copy Masked Version" button.
 *
 * Sprint K: AI Features
 */

import { useState, useEffect } from 'react';
import { aiApi, type MaskResponse, type SensitiveCategory } from '../../lib/api';

interface MaskingPanelProps {
  pageId: string;
  onClose: () => void;
}

const CATEGORY_COLORS: Record<SensitiveCategory, { bg: string; text: string }> = {
  pii: { bg: 'bg-orange-100', text: 'text-orange-700' },
  financial: { bg: 'bg-green-100', text: 'text-green-700' },
  medical: { bg: 'bg-red-100', text: 'text-red-700' },
  credentials: { bg: 'bg-purple-100', text: 'text-purple-700' },
  proprietary: { bg: 'bg-blue-100', text: 'text-blue-700' },
};

const CATEGORY_LABELS: Record<SensitiveCategory, string> = {
  pii: 'PII',
  financial: 'Financial',
  medical: 'Medical',
  credentials: 'Credentials',
  proprietary: 'Proprietary',
};

export function MaskingPanel({ pageId, onClose }: MaskingPanelProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MaskResponse | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await aiApi.detectSensitive({ page_id: pageId });
        if (!cancelled) setResult(response);
      } catch (err) {
        if (!cancelled) {
          const error = err as { response?: { data?: { detail?: string } } };
          setError(error.response?.data?.detail || 'Failed to scan for sensitive content');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    run();
    return () => { cancelled = true; };
  }, [pageId]);

  const handleCopyMasked = async () => {
    if (!result?.masked_text) return;
    await navigator.clipboard.writeText(result.masked_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          Sensitive Content Scan
        </h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {loading && (
        <div className="flex items-center gap-3 py-8 justify-center text-gray-500">
          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span className="text-sm">Scanning for sensitive content...</span>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          {error}
        </div>
      )}

      {result && (
        <>
          {/* Summary */}
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <div>
              <span className="text-2xl font-bold text-gray-900">{result.total_found}</span>
              <span className="text-sm text-gray-500 ml-1">
                match{result.total_found !== 1 ? 'es' : ''} found
              </span>
            </div>
            {result.categories_found.length > 0 && (
              <div className="flex gap-1 flex-wrap">
                {result.categories_found.map((cat) => {
                  const colors = CATEGORY_COLORS[cat];
                  return (
                    <span
                      key={cat}
                      className={`px-2 py-0.5 text-xs font-medium rounded ${colors.bg} ${colors.text}`}
                    >
                      {CATEGORY_LABELS[cat]}
                    </span>
                  );
                })}
              </div>
            )}
          </div>

          {/* Matches */}
          {result.matches.length > 0 ? (
            <div className="max-h-64 overflow-y-auto space-y-2">
              {result.matches.map((match, i) => {
                const colors = CATEGORY_COLORS[match.category];
                return (
                  <div key={i} className="p-3 border border-gray-200 rounded">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-1.5 py-0.5 text-xs font-medium rounded ${colors.bg} ${colors.text}`}>
                        {CATEGORY_LABELS[match.category]}
                      </span>
                      <div className="flex-1 h-1.5 bg-gray-200 rounded-full">
                        <div
                          className={`h-1.5 rounded-full ${
                            match.confidence >= 0.8
                              ? 'bg-red-500'
                              : match.confidence >= 0.5
                              ? 'bg-yellow-500'
                              : 'bg-gray-400'
                          }`}
                          style={{ width: `${match.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400">
                        {Math.round(match.confidence * 100)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-900 font-mono bg-red-50 px-2 py-1 rounded">
                      {match.text}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Replacement: <code className="bg-gray-100 px-1 rounded">{match.suggested_replacement}</code>
                    </p>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500">
              <svg className="mx-auto h-10 w-10 text-green-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm">No sensitive content detected</p>
            </div>
          )}

          {/* Actions */}
          {result.masked_text && (
            <button
              onClick={handleCopyMasked}
              className="w-full px-4 py-2 text-sm font-medium border border-gray-300 rounded-md hover:bg-gray-50 flex items-center justify-center gap-2 text-gray-700"
            >
              {copied ? (
                <>
                  <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Copied!
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy Masked Version
                </>
              )}
            </button>
          )}
        </>
      )}
    </div>
  );
}

export default MaskingPanel;
