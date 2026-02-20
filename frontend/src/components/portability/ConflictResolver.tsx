/**
 * ConflictResolver Component
 *
 * Sprint G: Metadata Portability
 *
 * Allows users to resolve conflicts found during import preview.
 */

import React from 'react';
import type { ImportItem, ImportConflictResolution } from '../../lib/api';
import { clsx } from 'clsx';

type ConflictAction = 'skip' | 'overwrite' | 'rename';

interface ConflictResolverProps {
  conflicts: ImportItem[];
  resolutions: ImportConflictResolution[];
  onResolve: (path: string, action: ConflictAction) => void;
  defaultAction: ConflictAction;
  onDefaultActionChange: (action: ConflictAction) => void;
}

const actionLabels: Record<ConflictAction, { label: string; description: string }> = {
  skip: { label: 'Skip', description: 'Keep existing, ignore imported' },
  overwrite: { label: 'Overwrite', description: 'Replace existing with imported' },
  rename: { label: 'Rename', description: 'Import with modified slug' },
};

export const ConflictResolver: React.FC<ConflictResolverProps> = ({
  conflicts,
  resolutions,
  onResolve,
  defaultAction,
  onDefaultActionChange,
}) => {
  const getResolution = (path: string): ConflictAction => {
    const found = resolutions.find((r) => r.path === path);
    return found?.action || defaultAction;
  };

  if (conflicts.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-yellow-400">
          {conflicts.length} conflict{conflicts.length !== 1 ? 's' : ''} found
        </h3>

        {/* Default action */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400">Default:</span>
          {(Object.keys(actionLabels) as ConflictAction[]).map((action) => (
            <button
              key={action}
              onClick={() => onDefaultActionChange(action)}
              className={clsx(
                'px-2 py-1 rounded border text-xs transition-colors',
                defaultAction === action
                  ? 'bg-blue-600/20 text-blue-400 border-blue-500/50'
                  : 'bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-600'
              )}
            >
              {actionLabels[action].label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        {conflicts.map((item) => {
          const current = getResolution(item.path);
          return (
            <div
              key={item.path}
              className="flex items-center justify-between bg-slate-800 rounded border border-slate-700 p-3"
            >
              <div className="flex-1 min-w-0 mr-4">
                <div className="text-sm text-white truncate">{item.title}</div>
                <div className="text-xs text-slate-500">{item.conflict_reason}</div>
              </div>
              <div className="flex gap-1">
                {(Object.keys(actionLabels) as ConflictAction[]).map((action) => (
                  <button
                    key={action}
                    onClick={() => onResolve(item.path, action)}
                    className={clsx(
                      'px-2 py-1 rounded text-xs transition-colors',
                      current === action
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                    )}
                    title={actionLabels[action].description}
                  >
                    {actionLabels[action].label}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ConflictResolver;
