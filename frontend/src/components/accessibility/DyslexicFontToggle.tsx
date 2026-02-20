/**
 * OpenDyslexic font toggle.
 *
 * Sprint I: WCAG 2.1 AA
 */

import { useReaderPreferencesStore } from '../../stores/readerPreferencesStore';

export function DyslexicFontToggle() {
  const dyslexicFont = useReaderPreferencesStore((s) => s.dyslexicFont);
  const toggle = useReaderPreferencesStore((s) => s.toggleDyslexicFont);

  return (
    <button
      onClick={toggle}
      aria-label="Toggle dyslexia-friendly font"
      aria-pressed={dyslexicFont}
      className={`p-2 rounded-md transition-colors ${
        dyslexicFont
          ? 'bg-purple-500/20 text-purple-400'
          : 'text-slate-300 hover:text-white hover:bg-slate-700'
      }`}
      title="Dyslexia-friendly font"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h8m-8 6h16" />
      </svg>
    </button>
  );
}
