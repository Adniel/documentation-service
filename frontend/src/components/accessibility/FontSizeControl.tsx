/**
 * Font size control (14-24px in 2px steps).
 *
 * Sprint I: WCAG 2.1 AA
 */

import { useReaderPreferencesStore } from '../../stores/readerPreferencesStore';

export function FontSizeControl() {
  const fontSize = useReaderPreferencesStore((s) => s.fontSize);
  const increase = useReaderPreferencesStore((s) => s.increaseFontSize);
  const decrease = useReaderPreferencesStore((s) => s.decreaseFontSize);

  return (
    <div className="flex items-center gap-1">
      <button
        onClick={decrease}
        disabled={fontSize <= 14}
        aria-label="Decrease font size"
        className="p-2 rounded-md text-slate-300 hover:text-white hover:bg-slate-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        title="Decrease font size"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
        </svg>
      </button>
      <span className="text-xs text-slate-400 w-8 text-center tabular-nums" aria-label={`Font size: ${fontSize}px`}>
        {fontSize}
      </span>
      <button
        onClick={increase}
        disabled={fontSize >= 24}
        aria-label="Increase font size"
        className="p-2 rounded-md text-slate-300 hover:text-white hover:bg-slate-700 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        title="Increase font size"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </button>
    </div>
  );
}
