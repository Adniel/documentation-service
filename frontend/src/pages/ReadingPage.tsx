/**
 * ReadingPage — read-only page viewer composing all Sprint I components.
 *
 * Route: /pages/:pageId
 *
 * Sprint I: Reader UI & Accessibility
 */

import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useRef, useState, useMemo, useCallback } from 'react';

import { contentApi } from '../lib/api';
import { useReaderPreferencesStore } from '../stores/readerPreferencesStore';
import { SkipLinks } from '../components/accessibility';
import { ReadingProgress, TableOfContents, ReaderToolbar, SpeedReader, FocusMode, RabbitHoleLink } from '../components/reading-aids';
import { ContextMenu, ShareDialog, MarkdownView, triggerPrint, useAiIntegrationActions } from '../components/context-menu';
import type { ContextMenuItem } from '../components/context-menu';

export default function ReadingPage() {
  const { pageId } = useParams<{ pageId: string }>();
  const navigate = useNavigate();
  const contentRef = useRef<HTMLDivElement>(null);

  // Preferences
  const theme = useReaderPreferencesStore((s) => s.theme);
  const fontSize = useReaderPreferencesStore((s) => s.fontSize);
  const highContrast = useReaderPreferencesStore((s) => s.highContrast);
  const dyslexicFont = useReaderPreferencesStore((s) => s.dyslexicFont);
  const focusMode = useReaderPreferencesStore((s) => s.focusMode);

  // Modals
  const [showSpeedReader, setShowSpeedReader] = useState(false);
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [showMarkdownView, setShowMarkdownView] = useState(false);

  // Fetch rendered page
  const {
    data: rendered,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['page-render', pageId],
    queryFn: () => contentApi.render(pageId!),
    enabled: !!pageId,
  });

  // Fetch page data for metadata
  const { data: page } = useQuery({
    queryKey: ['page', pageId],
    queryFn: () => contentApi.get(pageId!),
    enabled: !!pageId,
  });

  // Extract plain text for speed reader
  const plainText = useMemo(() => {
    if (!rendered?.content_html) return '';
    const div = document.createElement('div');
    div.innerHTML = rendered.content_html;
    return div.textContent || '';
  }, [rendered?.content_html]);

  // AI integration
  const selectedText = typeof window !== 'undefined' ? window.getSelection()?.toString() || '' : '';
  const { copyForChatGPT, copyForClaude, copyForMCP, toast: aiToast } = useAiIntegrationActions({
    selectedText,
    pageTitle: rendered?.title || '',
  });

  const handlePrint = useCallback(() => triggerPrint(), []);
  const handleShare = useCallback(() => setShowShareDialog(true), []);

  // Context menu items
  const contextMenuItems: ContextMenuItem[] = useMemo(() => [
    {
      label: 'Copy Selection',
      onClick: () => {
        const sel = window.getSelection()?.toString();
        if (sel) navigator.clipboard.writeText(sel);
      },
    },
    { label: '', onClick: () => {}, separator: true },
    { label: 'Share', onClick: () => setShowShareDialog(true) },
    { label: 'Print', onClick: handlePrint },
    { label: 'View as Markdown', onClick: () => setShowMarkdownView(true) },
    { label: '', onClick: () => {}, separator: true },
    { label: 'Speed Reader', onClick: () => setShowSpeedReader(true) },
    { label: 'Focus Mode', onClick: () => useReaderPreferencesStore.getState().toggleFocusMode() },
    { label: '', onClick: () => {}, separator: true },
    { label: 'Copy for ChatGPT', onClick: copyForChatGPT },
    { label: 'Copy for Claude', onClick: copyForClaude },
    { label: 'Copy for MCP', onClick: copyForMCP },
  ], [handlePrint, copyForChatGPT, copyForClaude, copyForMCP]);

  // Build CSS classes for content area
  const contentClasses = [
    'reader-content',
    theme === 'light' ? 'reader-light' : 'reader-dark',
    highContrast && 'high-contrast',
    dyslexicFont && 'dyslexic-font',
    focusMode && 'relative z-50',
  ].filter(Boolean).join(' ');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading page...</div>
      </div>
    );
  }

  if (error || !rendered) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded">
          Failed to load page. The document may have been deleted or you don't have access.
        </div>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 text-blue-400 hover:text-blue-300"
        >
          Go back
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <SkipLinks />
      <ReadingProgress />

      {/* Toolbar */}
      <div className="sticky top-1 z-30 px-4 py-2" data-print-hide>
        <div className="max-w-6xl mx-auto">
          <ReaderToolbar
            pageId={pageId!}
            pageTitle={rendered.title}
            onPrint={handlePrint}
            onShare={handleShare}
          />
        </div>
      </div>

      {/* Main content area */}
      <div className="max-w-6xl mx-auto px-4 py-6 flex gap-6">
        {/* TOC sidebar */}
        <aside className="hidden lg:block w-56 flex-shrink-0" data-print-hide>
          <TableOfContents toc={rendered.toc} />
        </aside>

        {/* Content */}
        <main className="flex-1 min-w-0" id="main-content">
          {/* Breadcrumb */}
          <nav className="mb-4 text-sm" data-print-hide>
            <ol className="flex items-center gap-2 text-slate-400">
              <li>
                <RouterLink to="/" className="hover:text-white transition-colors">
                  Dashboard
                </RouterLink>
              </li>
              <li className="text-slate-600">/</li>
              <li className="text-white font-medium truncate max-w-xs">{rendered.title}</li>
            </ol>
          </nav>

          {/* Document metadata */}
          {page && (
            <div className="mb-4 flex items-center gap-3 text-sm text-slate-400" data-print-hide>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                page.status === 'effective' ? 'bg-green-500/20 text-green-400' :
                page.status === 'draft' ? 'bg-yellow-500/20 text-yellow-400' :
                page.status === 'in_review' ? 'bg-blue-500/20 text-blue-400' :
                'bg-slate-500/20 text-slate-400'
              }`}>
                {page.status.replace('_', ' ')}
              </span>
              <span>v{page.version}</span>
              {page.document_number && (
                <span className="font-mono text-xs">{page.document_number}</span>
              )}
            </div>
          )}

          {/* Rendered content */}
          <article
            ref={contentRef}
            className={`${contentClasses} rounded-lg p-6 lg:p-8 prose prose-slate max-w-none`}
            style={{ fontSize: `${fontSize}px` }}
            dangerouslySetInnerHTML={{ __html: rendered.content_html }}
          />

          {/* Updated date */}
          {page && (
            <div className="mt-4 text-xs text-slate-500" data-print-hide>
              Last updated: {new Date(page.updated_at).toLocaleDateString()}
            </div>
          )}
        </main>
      </div>

      {/* Overlays & Modals */}
      <ContextMenu items={contextMenuItems} containerRef={contentRef} />
      <RabbitHoleLink containerRef={contentRef} />
      <FocusMode />

      {showSpeedReader && plainText && (
        <SpeedReader text={plainText} onClose={() => setShowSpeedReader(false)} />
      )}

      <ShareDialog
        isOpen={showShareDialog}
        onClose={() => setShowShareDialog(false)}
        pageTitle={rendered.title}
        pageUrl={window.location.href}
      />

      <MarkdownView
        isOpen={showMarkdownView}
        onClose={() => setShowMarkdownView(false)}
        pageId={pageId!}
        pageTitle={rendered.title}
      />

      {/* AI toast */}
      {aiToast && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-green-600 text-white text-sm px-4 py-2 rounded-lg shadow-lg z-[90]">
          {aiToast}
        </div>
      )}
    </div>
  );
}
