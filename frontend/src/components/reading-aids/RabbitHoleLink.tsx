/**
 * Rabbit hole link previews — hover over internal links to see a floating
 * summary card without navigating away.
 *
 * Sprint I: Reading Aids
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { contentApi } from '../../lib/api';

interface PreviewData {
  title: string;
  summary?: string;
  status: string;
}

interface CardPosition {
  top: number;
  left: number;
}

interface RabbitHoleLinkProps {
  containerRef: React.RefObject<HTMLElement | null>;
}

export function RabbitHoleLink({ containerRef }: RabbitHoleLinkProps) {
  const [preview, setPreview] = useState<PreviewData | null>(null);
  const [position, setPosition] = useState<CardPosition>({ top: 0, left: 0 });
  const [visible, setVisible] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();
  const cacheRef = useRef<Map<string, PreviewData>>(new Map());

  const fetchPreview = useCallback(async (pageId: string) => {
    if (cacheRef.current.has(pageId)) {
      setPreview(cacheRef.current.get(pageId)!);
      setVisible(true);
      return;
    }
    try {
      const page = await contentApi.get(pageId);
      const data: PreviewData = {
        title: page.title,
        summary: page.summary || undefined,
        status: page.status,
      };
      cacheRef.current.set(pageId, data);
      setPreview(data);
      setVisible(true);
    } catch {
      // Silently fail for invalid links
    }
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleMouseEnter = (e: Event) => {
      const target = e.target as HTMLAnchorElement;
      const href = target.getAttribute('href') || '';

      // Only handle internal page links
      const match = href.match(/\/pages\/([a-f0-9-]+)/);
      if (!match) return;

      const pageId = match[1];
      const rect = target.getBoundingClientRect();

      timerRef.current = setTimeout(() => {
        setPosition({
          top: rect.bottom + window.scrollY + 8,
          left: rect.left + window.scrollX,
        });
        fetchPreview(pageId);
      }, 300);
    };

    const handleMouseLeave = () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      setVisible(false);
    };

    // Attach to all <a> tags within the container
    const links = container.querySelectorAll('a');
    links.forEach((link) => {
      link.addEventListener('mouseenter', handleMouseEnter);
      link.addEventListener('mouseleave', handleMouseLeave);
    });

    return () => {
      links.forEach((link) => {
        link.removeEventListener('mouseenter', handleMouseEnter);
        link.removeEventListener('mouseleave', handleMouseLeave);
      });
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [containerRef, fetchPreview]);

  if (!visible || !preview) return null;

  return createPortal(
    <div
      className="fixed z-50 w-72 bg-slate-800 border border-slate-600 rounded-lg shadow-xl p-3 pointer-events-none"
      style={{ top: position.top, left: position.left }}
    >
      <h4 className="text-sm font-medium text-white mb-1">{preview.title}</h4>
      {preview.summary && (
        <p className="text-xs text-slate-400 line-clamp-2">{preview.summary}</p>
      )}
      <span className={`inline-block mt-2 text-xs px-1.5 py-0.5 rounded ${
        preview.status === 'effective'
          ? 'bg-green-500/20 text-green-400'
          : preview.status === 'draft'
          ? 'bg-yellow-500/20 text-yellow-400'
          : 'bg-slate-500/20 text-slate-400'
      }`}>
        {preview.status}
      </span>
    </div>,
    document.body
  );
}
