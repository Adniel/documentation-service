/**
 * Save Status Indicator Component
 *
 * Shows the current save status with animations.
 */

import type { SaveStatus } from '../../types/editor';

interface SaveStatusIndicatorProps {
  status: SaveStatus;
  lastSavedAt: Date | null;
  error: string | null;
}

export function SaveStatusIndicator({
  status,
  lastSavedAt,
  error,
}: SaveStatusIndicatorProps) {
  const getStatusDisplay = () => {
    switch (status) {
      case 'saving':
        return (
          <span className="flex items-center gap-2 text-blue-400">
            <span className="animate-spin">⟳</span>
            Saving...
          </span>
        );
      case 'saved':
        return (
          <span className="flex items-center gap-2 text-green-400">
            <span>✓</span>
            Saved
          </span>
        );
      case 'error':
        return (
          <span className="flex items-center gap-2 text-red-400" title={error || undefined}>
            <span>✗</span>
            Error saving
          </span>
        );
      case 'idle':
      default:
        if (lastSavedAt) {
          return (
            <span className="text-slate-500">
              Last saved {formatRelativeTime(lastSavedAt)}
            </span>
          );
        }
        return <span className="text-slate-500">Not saved yet</span>;
    }
  };

  return (
    <div className="text-sm transition-all duration-200">{getStatusDisplay()}</div>
  );
}

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);

  if (diffSec < 5) {
    return 'just now';
  }
  if (diffSec < 60) {
    return `${diffSec}s ago`;
  }
  if (diffMin < 60) {
    return `${diffMin}m ago`;
  }
  if (diffHour < 24) {
    return `${diffHour}h ago`;
  }
  return date.toLocaleDateString();
}

export default SaveStatusIndicator;
