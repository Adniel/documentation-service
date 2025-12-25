/**
 * Editor Keyboard Shortcuts Hook
 *
 * Handles global keyboard shortcuts for the editor.
 */

import { useEffect, useCallback } from 'react';

interface UseEditorShortcutsOptions {
  onSave?: () => void;
  onExport?: () => void;
  onToggleSidebar?: () => void;
  enabled?: boolean;
}

export function useEditorShortcuts({
  onSave,
  onExport,
  onToggleSidebar,
  enabled = true,
}: UseEditorShortcutsOptions) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const isMod = event.metaKey || event.ctrlKey;

      // Cmd/Ctrl + S: Save
      if (isMod && event.key === 's') {
        event.preventDefault();
        onSave?.();
        return;
      }

      // Cmd/Ctrl + Shift + E: Export
      if (isMod && event.shiftKey && event.key === 'e') {
        event.preventDefault();
        onExport?.();
        return;
      }

      // Cmd/Ctrl + B: Toggle sidebar (when outside editor)
      if (isMod && event.key === 'b' && event.shiftKey) {
        event.preventDefault();
        onToggleSidebar?.();
        return;
      }
    },
    [enabled, onSave, onExport, onToggleSidebar]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
}

export default useEditorShortcuts;
