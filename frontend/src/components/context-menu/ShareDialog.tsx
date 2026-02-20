/**
 * Share dialog modal — copy link, copy as Markdown, email.
 *
 * Sprint I: Context Menu
 */

import { useState } from 'react';

interface ShareDialogProps {
  isOpen: boolean;
  onClose: () => void;
  pageTitle: string;
  pageUrl: string;
  markdownContent?: string;
}

export function ShareDialog({ isOpen, onClose, pageTitle, pageUrl, markdownContent }: ShareDialogProps) {
  const [toast, setToast] = useState('');

  if (!isOpen) return null;

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 2000);
  };

  const copyLink = async () => {
    await navigator.clipboard.writeText(pageUrl);
    showToast('Link copied!');
  };

  const copyMarkdown = async () => {
    if (markdownContent) {
      await navigator.clipboard.writeText(markdownContent);
      showToast('Markdown copied!');
    }
  };

  const emailShare = () => {
    const subject = encodeURIComponent(pageTitle);
    const body = encodeURIComponent(`Check out this document: ${pageTitle}\n\n${pageUrl}`);
    window.open(`mailto:?subject=${subject}&body=${body}`);
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-[80] flex items-center justify-center" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-600 rounded-lg shadow-2xl p-6 w-96" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-lg font-medium text-white mb-4">Share</h3>

        <div className="space-y-3">
          <button
            onClick={copyLink}
            className="w-full text-left px-4 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-slate-200 transition-colors flex items-center gap-3"
          >
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Copy link
          </button>

          {markdownContent && (
            <button
              onClick={copyMarkdown}
              className="w-full text-left px-4 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-slate-200 transition-colors flex items-center gap-3"
            >
              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Copy as Markdown
            </button>
          )}

          <button
            onClick={emailShare}
            className="w-full text-left px-4 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-slate-200 transition-colors flex items-center gap-3"
          >
            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Share via email
          </button>
        </div>

        {toast && (
          <div className="mt-3 text-center text-sm text-green-400">{toast}</div>
        )}

        <button
          onClick={onClose}
          className="mt-4 w-full py-2 text-sm text-slate-400 hover:text-white transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
}
