/**
 * Sticky table of contents sidebar with active section highlighting.
 * Uses IntersectionObserver for scroll-aware highlighting.
 *
 * Sprint I: Reading Aids
 */

import { useEffect, useState, useCallback } from 'react';
import { useReaderPreferencesStore } from '../../stores/readerPreferencesStore';

interface TocEntry {
  id: string;
  text: string;
  level: number;
}

interface TableOfContentsProps {
  toc: TocEntry[];
}

export function TableOfContents({ toc }: TableOfContentsProps) {
  const [activeId, setActiveId] = useState<string>('');
  const tocCollapsed = useReaderPreferencesStore((s) => s.tocCollapsed);
  const toggleTocCollapsed = useReaderPreferencesStore((s) => s.toggleTocCollapsed);

  useEffect(() => {
    if (!toc.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        }
      },
      { rootMargin: '-80px 0px -60% 0px', threshold: 0.1 }
    );

    for (const item of toc) {
      const el = document.getElementById(item.id);
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, [toc]);

  const handleClick = useCallback((id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, []);

  if (!toc.length) return null;

  return (
    <nav
      className="reader-toc-sidebar sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto"
      aria-label="Table of contents"
      id="main-nav"
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {tocCollapsed ? '' : 'On this page'}
        </h3>
        <button
          onClick={toggleTocCollapsed}
          aria-label={tocCollapsed ? 'Expand table of contents' : 'Collapse table of contents'}
          className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {tocCollapsed ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            )}
          </svg>
        </button>
      </div>
      {!tocCollapsed && (
        <ul className="space-y-1">
          {toc.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => handleClick(item.id)}
                className={`block w-full text-left text-sm py-1 transition-colors rounded px-2 ${
                  activeId === item.id
                    ? 'text-blue-400 bg-blue-500/10 font-medium'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                style={{ paddingLeft: `${(item.level - 1) * 0.75 + 0.5}rem` }}
              >
                {item.text}
              </button>
            </li>
          ))}
        </ul>
      )}
    </nav>
  );
}
