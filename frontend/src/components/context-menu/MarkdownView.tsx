/**
 * Markdown view modal — shows page as readonly Markdown with copy/download.
 *
 * Sprint I: Context Menu
 */

import { useState, useEffect } from 'react';
import { exportApi } from '../../lib/api';

interface MarkdownViewProps {
  isOpen: boolean;
  onClose: () => void;
  pageId: string;
  pageTitle: string;
}

export function MarkdownView({ isOpen, onClose, pageId, pageTitle }: MarkdownViewProps) {
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState('');

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    exportApi
      .markdown(pageId)
      .then((blob) => blob.text())
      .then((text) => setMarkdown(text))
      .catch(() => setMarkdown('Failed to load markdown'))
      .finally(() => setLoading(false));
  }, [isOpen, pageId]);

  if (!isOpen) return null;

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 2000);
  };

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(markdown);
    showToast('Copied to clipboard!');
  };

  const downloadMd = () => {
    const blob = new Blob([markdown], { type: 'text/markdown' });
    exportApi.download(blob, `${pageTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.md`);
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-[80] flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-600 rounded-lg shadow-2xl w-full max-w-3xl max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
          <h3 className="text-sm font-medium text-white">Markdown View</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={copyToClipboard}
              className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Copy
            </button>
            <button
              onClick={downloadMd}
              className="px-3 py-1.5 text-xs bg-slate-700 text-slate-300 rounded hover:bg-slate-600 hover:text-white transition-colors"
            >
              Download .md
            </button>
            <button onClick={onClose} className="text-slate-400 hover:text-white p-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="text-slate-400 text-center py-8">Loading...</div>
          ) : (
            <pre className="text-sm text-slate-300 whitespace-pre-wrap font-mono leading-relaxed">{markdown}</pre>
          )}
        </div>
        {toast && (
          <div className="px-4 py-2 text-center text-sm text-green-400 border-t border-slate-700">{toast}</div>
        )}
      </div>
    </div>
  );
}
