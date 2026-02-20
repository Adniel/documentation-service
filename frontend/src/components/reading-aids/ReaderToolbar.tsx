/**
 * Composable reader toolbar — accessibility controls + export + actions.
 *
 * Sprint I: Reading Aids
 */

import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ThemeToggle, HighContrastToggle, FontSizeControl, DyslexicFontToggle } from '../accessibility';
import { exportApi } from '../../lib/api';

interface ReaderToolbarProps {
  pageId: string;
  pageTitle: string;
  onPrint: () => void;
  onShare: () => void;
}

export function ReaderToolbar({ pageId, pageTitle, onPrint, onShare }: ReaderToolbarProps) {
  const [exportOpen, setExportOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setExportOpen(false);
      }
    };
    if (exportOpen) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [exportOpen]);

  const handleExport = async (format: 'pdf' | 'docx' | 'markdown') => {
    setExporting(true);
    try {
      const blob = await exportApi[format](pageId);
      const ext = format === 'markdown' ? 'md' : format;
      const slug = pageTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
      exportApi.download(blob, `${slug}.${ext}`);
    } finally {
      setExporting(false);
      setExportOpen(false);
    }
  };

  return (
    <div className="reader-toolbar flex items-center gap-1 p-2 bg-slate-800/80 backdrop-blur-sm rounded-lg border border-slate-700" data-print-hide>
      {/* Accessibility controls */}
      <ThemeToggle />
      <HighContrastToggle />
      <FontSizeControl />
      <DyslexicFontToggle />

      {/* Divider */}
      <div className="w-px h-6 bg-slate-600 mx-1" />

      {/* Share */}
      <button
        onClick={onShare}
        className="p-2 rounded-md text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
        aria-label="Share"
        title="Share"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
      </button>

      {/* Print */}
      <button
        onClick={onPrint}
        className="p-2 rounded-md text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
        aria-label="Print"
        title="Print"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
        </svg>
      </button>

      {/* Export dropdown */}
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setExportOpen(!exportOpen)}
          disabled={exporting}
          className="p-2 rounded-md text-slate-300 hover:text-white hover:bg-slate-700 transition-colors disabled:opacity-50"
          aria-label="Export"
          title="Export"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>
        {exportOpen && (
          <div className="absolute right-0 top-full mt-1 w-40 bg-slate-800 border border-slate-600 rounded-lg shadow-xl py-1 z-50">
            <button
              onClick={() => handleExport('pdf')}
              className="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white"
            >
              Export as PDF
            </button>
            <button
              onClick={() => handleExport('docx')}
              className="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white"
            >
              Export as DOCX
            </button>
            <button
              onClick={() => handleExport('markdown')}
              className="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-slate-700 hover:text-white"
            >
              Export as Markdown
            </button>
          </div>
        )}
      </div>

      {/* Divider */}
      <div className="w-px h-6 bg-slate-600 mx-1" />

      {/* Edit button */}
      <Link
        to={`/editor/${pageId}`}
        className="px-3 py-1.5 text-sm text-blue-400 hover:text-blue-300 hover:bg-slate-700 rounded-md transition-colors flex items-center gap-1.5"
        title="Edit page"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        Edit
      </Link>
    </div>
  );
}
