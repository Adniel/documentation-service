/**
 * RSVP (Rapid Serial Visual Presentation) speed reader overlay.
 * Displays one word at a time with ORP highlighting.
 *
 * Sprint I: Reading Aids
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { useReaderPreferencesStore } from '../../stores/readerPreferencesStore';

interface SpeedReaderProps {
  text: string;
  onClose: () => void;
}

export function SpeedReader({ text, onClose }: SpeedReaderProps) {
  const wpm = useReaderPreferencesStore((s) => s.speedReaderWpm);
  const setWpm = useReaderPreferencesStore((s) => s.setSpeedReaderWpm);

  const words = text.split(/\s+/).filter(Boolean);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const currentWord = words[index] || '';

  // Find ORP position (optimal recognition point — roughly 1/3 of the word)
  const orpIndex = Math.max(0, Math.floor(currentWord.length / 3) - 1);
  const before = currentWord.slice(0, orpIndex);
  const orp = currentWord[orpIndex] || '';
  const after = currentWord.slice(orpIndex + 1);

  const tick = useCallback(() => {
    setIndex((i) => {
      if (i >= words.length - 1) {
        setPlaying(false);
        return i;
      }
      return i + 1;
    });
  }, [words.length]);

  useEffect(() => {
    if (playing) {
      const ms = 60000 / wpm;
      intervalRef.current = setInterval(tick, ms);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [playing, wpm, tick]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      else if (e.key === ' ') {
        e.preventDefault();
        setPlaying((p) => !p);
      } else if (e.key === 'ArrowLeft') setWpm(Math.max(200, wpm - 50));
      else if (e.key === 'ArrowRight') setWpm(Math.min(800, wpm + 50));
      else if (e.key === 'r') {
        setIndex(0);
        setPlaying(false);
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose, wpm, setWpm]);

  return (
    <div className="speed-reader-overlay fixed inset-0 bg-black/90 z-[60] flex flex-col items-center justify-center">
      {/* Word display */}
      <div className="text-center mb-8 min-h-[80px] flex items-center justify-center">
        <span className="font-mono text-4xl tracking-wider">
          <span className="text-slate-400">{before}</span>
          <span className="text-red-400 font-bold">{orp}</span>
          <span className="text-slate-400">{after}</span>
        </span>
      </div>

      {/* Progress */}
      <div className="w-64 h-1 bg-slate-700 rounded-full mb-6">
        <div
          className="h-full bg-blue-500 rounded-full transition-[width] duration-75"
          style={{ width: `${words.length > 0 ? (index / words.length) * 100 : 0}%` }}
        />
      </div>

      {/* Controls */}
      <div className="flex items-center gap-6 text-slate-300">
        <button
          onClick={() => { setIndex(0); setPlaying(false); }}
          className="px-3 py-2 hover:text-white transition-colors text-sm"
          title="Restart (R)"
        >
          Restart
        </button>
        <button
          onClick={() => setWpm(Math.max(200, wpm - 50))}
          className="px-3 py-2 hover:text-white transition-colors"
          title="Slower (Left arrow)"
        >
          -
        </button>
        <button
          onClick={() => setPlaying(!playing)}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          title="Play/Pause (Space)"
        >
          {playing ? 'Pause' : 'Play'}
        </button>
        <button
          onClick={() => setWpm(Math.min(800, wpm + 50))}
          className="px-3 py-2 hover:text-white transition-colors"
          title="Faster (Right arrow)"
        >
          +
        </button>
        <span className="text-sm text-slate-500 w-20 text-center">{wpm} WPM</span>
      </div>

      {/* Close */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 text-slate-400 hover:text-white p-2"
        title="Close (Escape)"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      {/* Keyboard hints */}
      <div className="absolute bottom-4 text-xs text-slate-600 flex gap-4">
        <span><kbd className="bg-slate-800 px-1 rounded">Space</kbd> Play/Pause</span>
        <span><kbd className="bg-slate-800 px-1 rounded">Left/Right</kbd> Speed</span>
        <span><kbd className="bg-slate-800 px-1 rounded">R</kbd> Restart</span>
        <span><kbd className="bg-slate-800 px-1 rounded">Esc</kbd> Close</span>
      </div>
    </div>
  );
}
