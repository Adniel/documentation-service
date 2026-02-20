/**
 * Focus mode overlay — dims everything except the content area.
 * Hides toolbar and TOC for distraction-free reading.
 *
 * Sprint I: Reading Aids
 */

import { useEffect } from 'react';
import { useReaderPreferencesStore } from '../../stores/readerPreferencesStore';

export function FocusMode() {
  const focusMode = useReaderPreferencesStore((s) => s.focusMode);
  const toggleFocusMode = useReaderPreferencesStore((s) => s.toggleFocusMode);

  useEffect(() => {
    if (!focusMode) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') toggleFocusMode();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [focusMode, toggleFocusMode]);

  if (!focusMode) return null;

  return (
    <>
      {/* Overlay behind content */}
      <div className="focus-mode-overlay fixed inset-0 bg-black/60 z-40" />

      {/* Exit button */}
      <button
        onClick={toggleFocusMode}
        className="fixed bottom-4 right-4 z-[60] px-3 py-2 bg-slate-800 text-slate-300 text-sm rounded-lg border border-slate-600 hover:bg-slate-700 hover:text-white transition-colors shadow-lg"
        title="Exit focus mode (Escape)"
      >
        Exit Focus Mode
      </button>
    </>
  );
}
