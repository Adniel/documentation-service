/**
 * Auto-save Hook for Editor
 *
 * Provides debounced auto-save functionality with status tracking.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type { SaveStatus } from '../types/editor';

interface UseAutoSaveOptions {
  /** Debounce delay in milliseconds */
  debounceMs?: number;
  /** Callback to execute on save */
  onSave: (content: unknown) => Promise<void>;
  /** Whether auto-save is enabled */
  enabled?: boolean;
}

interface UseAutoSaveReturn {
  /** Current save status */
  status: SaveStatus;
  /** Trigger a save (will be debounced) */
  triggerSave: (content: unknown) => void;
  /** Force an immediate save */
  saveNow: (content: unknown) => Promise<void>;
  /** Time since last save */
  lastSavedAt: Date | null;
  /** Error message if save failed */
  error: string | null;
}

export function useAutoSave({
  debounceMs = 2000,
  onSave,
  enabled = true,
}: UseAutoSaveOptions): UseAutoSaveReturn {
  const [status, setStatus] = useState<SaveStatus>('idle');
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingContentRef = useRef<unknown>(null);
  const isSavingRef = useRef(false);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const performSave = useCallback(
    async (content: unknown) => {
      if (isSavingRef.current) {
        // Queue the content for after current save completes
        pendingContentRef.current = content;
        return;
      }

      isSavingRef.current = true;
      setStatus('saving');
      setError(null);

      try {
        await onSave(content);
        setStatus('saved');
        setLastSavedAt(new Date());

        // Reset to idle after a short delay
        setTimeout(() => {
          setStatus((current) => (current === 'saved' ? 'idle' : current));
        }, 2000);
      } catch (err) {
        setStatus('error');
        setError(err instanceof Error ? err.message : 'Save failed');
      } finally {
        isSavingRef.current = false;

        // If there's pending content, save it
        if (pendingContentRef.current !== null) {
          const pending = pendingContentRef.current;
          pendingContentRef.current = null;
          performSave(pending);
        }
      }
    },
    [onSave]
  );

  const triggerSave = useCallback(
    (content: unknown) => {
      if (!enabled) return;

      // Clear existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      // Set new timeout
      timeoutRef.current = setTimeout(() => {
        performSave(content);
      }, debounceMs);
    },
    [enabled, debounceMs, performSave]
  );

  const saveNow = useCallback(
    async (content: unknown) => {
      // Clear any pending debounced save
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      await performSave(content);
    },
    [performSave]
  );

  return {
    status,
    triggerSave,
    saveNow,
    lastSavedAt,
    error,
  };
}

export default useAutoSave;
