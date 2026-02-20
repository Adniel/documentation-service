/**
 * WritingAssistantPanel — AI-powered writing suggestions.
 *
 * Shows original text, loading state, then diff-style before/after.
 * Accept replaces text in editor, reject dismisses.
 *
 * Sprint K: AI Features
 */

import { useState, useEffect } from 'react';
import { aiApi, type WritingAction, type WritingAssistResponse } from '../../lib/api';

interface WritingAssistantPanelProps {
  selectedText: string;
  action: WritingAction;
  onAccept: (text: string) => void;
  onClose: () => void;
}

const ACTION_LABELS: Record<WritingAction, string> = {
  improve: 'Improve Writing',
  summarize: 'Summarize',
  expand: 'Expand',
  simplify: 'Simplify',
  formalize: 'Formalize',
  fix_grammar: 'Fix Grammar',
  translate: 'Translate',
};

export function WritingAssistantPanel({
  selectedText,
  action,
  onAccept,
  onClose,
}: WritingAssistantPanelProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WritingAssistResponse | null>(null);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await aiApi.writingAssist({
          text: selectedText,
          action,
        });
        if (!cancelled) {
          setResult(response);
        }
      } catch (err) {
        if (!cancelled) {
          const error = err as { response?: { data?: { detail?: string } } };
          setError(error.response?.data?.detail || 'Failed to get AI suggestion');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    run();
    return () => { cancelled = true; };
  }, [selectedText, action]);

  return (
    <div className="fixed bottom-4 right-4 w-[480px] max-h-[70vh] bg-slate-800 rounded-lg border border-slate-600 shadow-2xl z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span className="text-sm font-medium text-white">
            AI: {ACTION_LABELS[action]}
          </span>
        </div>
        <button onClick={onClose} className="text-slate-400 hover:text-white">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading && (
          <div className="flex items-center gap-3 text-slate-400 py-8 justify-center">
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span className="text-sm">Generating suggestion...</span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-sm text-red-400">
            {error}
          </div>
        )}

        {result && (
          <>
            {/* Original */}
            <div>
              <label className="text-xs font-medium text-slate-500 uppercase tracking-wide">Original</label>
              <div className="mt-1 p-3 bg-slate-900 rounded text-sm text-slate-300 whitespace-pre-wrap max-h-32 overflow-y-auto">
                {result.original_text}
              </div>
            </div>

            {/* Suggested */}
            <div>
              <label className="text-xs font-medium text-green-400 uppercase tracking-wide">Suggested</label>
              <div className="mt-1 p-3 bg-green-500/5 border border-green-500/20 rounded text-sm text-slate-200 whitespace-pre-wrap max-h-48 overflow-y-auto">
                {result.suggested_text}
              </div>
            </div>

            {/* Summary */}
            {result.changes_summary && (
              <p className="text-xs text-slate-400 italic">{result.changes_summary}</p>
            )}
          </>
        )}
      </div>

      {/* Actions */}
      {result && (
        <div className="flex gap-2 px-4 py-3 border-t border-slate-700">
          <button
            onClick={onClose}
            className="flex-1 px-3 py-2 text-sm text-slate-300 border border-slate-600 rounded-md hover:bg-slate-700"
          >
            Reject
          </button>
          <button
            onClick={() => onAccept(result.suggested_text)}
            className="flex-1 px-3 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700 font-medium"
          >
            Accept
          </button>
        </div>
      )}
    </div>
  );
}

export default WritingAssistantPanel;
