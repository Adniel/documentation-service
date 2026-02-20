/**
 * ImportProgress Component
 *
 * Sprint G: Metadata Portability
 *
 * Shows the result of an import execution.
 */

import React from 'react';
import type { ImportResult } from '../../lib/api';
import { clsx } from 'clsx';

interface ImportProgressProps {
  result: ImportResult;
  onClose: () => void;
}

export const ImportProgress: React.FC<ImportProgressProps> = ({ result, onClose }) => {
  const statusColors: Record<string, string> = {
    created: 'text-green-400',
    updated: 'text-blue-400',
    skipped: 'text-slate-400',
    error: 'text-red-400',
  };

  const hasErrors = result.errors > 0;

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className={clsx(
        'rounded p-4 border',
        hasErrors
          ? 'bg-yellow-500/10 border-yellow-500/20'
          : 'bg-green-500/10 border-green-500/20'
      )}>
        <h3 className={clsx(
          'text-sm font-medium mb-2',
          hasErrors ? 'text-yellow-400' : 'text-green-400'
        )}>
          {hasErrors ? 'Import completed with errors' : 'Import completed successfully'}
        </h3>
        <div className="flex gap-4 text-sm">
          <span className="text-green-400">{result.created} created</span>
          <span className="text-blue-400">{result.updated} updated</span>
          <span className="text-slate-400">{result.skipped} skipped</span>
          {result.errors > 0 && (
            <span className="text-red-400">{result.errors} errors</span>
          )}
        </div>
      </div>

      {/* Items */}
      <div className="border border-slate-700 rounded overflow-hidden max-h-64 overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-800 sticky top-0">
            <tr>
              <th className="text-left px-3 py-2 text-slate-400 font-medium">Status</th>
              <th className="text-left px-3 py-2 text-slate-400 font-medium">Title</th>
              <th className="text-left px-3 py-2 text-slate-400 font-medium">Details</th>
            </tr>
          </thead>
          <tbody>
            {result.items.map((item, idx) => (
              <tr
                key={idx}
                className="border-t border-slate-700/50"
              >
                <td className="px-3 py-2">
                  <span className={statusColors[item.status] || 'text-slate-400'}>
                    {item.status}
                  </span>
                </td>
                <td className="px-3 py-2 text-white">{item.title}</td>
                <td className="px-3 py-2 text-xs text-slate-500">
                  {item.error || item.resource_id || ''}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-end">
        <button
          onClick={onClose}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-500 transition-colors"
        >
          Done
        </button>
      </div>
    </div>
  );
};

export default ImportProgress;
