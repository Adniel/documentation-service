/**
 * ImportPreview Component
 *
 * Sprint G: Metadata Portability
 *
 * Shows what an import will do before executing.
 */

import React from 'react';
import type { ImportItem } from '../../lib/api';
import { clsx } from 'clsx';

interface ImportPreviewProps {
  items: ImportItem[];
  statistics: Record<string, number>;
  warnings: string[];
  formatDetected: string;
}

const statusConfig: Record<string, { label: string; color: string; icon: string }> = {
  create: { label: 'Create', color: 'text-green-400 bg-green-500/10', icon: '+' },
  update: { label: 'Update', color: 'text-blue-400 bg-blue-500/10', icon: '~' },
  conflict: { label: 'Conflict', color: 'text-yellow-400 bg-yellow-500/10', icon: '!' },
  skip: { label: 'Skip', color: 'text-slate-400 bg-slate-500/10', icon: '-' },
  error: { label: 'Error', color: 'text-red-400 bg-red-500/10', icon: 'x' },
};

export const ImportPreview: React.FC<ImportPreviewProps> = ({
  items,
  statistics,
  warnings,
  formatDetected,
}) => {
  return (
    <div className="space-y-4">
      {/* Format and stats */}
      <div className="flex items-center gap-4 text-sm">
        <span className="text-slate-400">
          Format: <span className="text-white">{formatDetected}</span>
        </span>
        <span className="text-slate-400">
          Total: <span className="text-white">{statistics.total || 0}</span>
        </span>
      </div>

      {/* Statistics badges */}
      <div className="flex gap-2">
        {Object.entries(statistics).map(([key, count]) => {
          if (key === 'total' || count === 0) return null;
          const cfg = statusConfig[key];
          if (!cfg) return null;
          return (
            <span
              key={key}
              className={clsx('text-xs px-2 py-1 rounded', cfg.color)}
            >
              {cfg.label}: {count}
            </span>
          );
        })}
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded p-3">
          {warnings.map((w, i) => (
            <div key={i} className="text-sm text-yellow-400">{w}</div>
          ))}
        </div>
      )}

      {/* Items list */}
      <div className="border border-slate-700 rounded overflow-hidden max-h-96 overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-800 sticky top-0">
            <tr>
              <th className="text-left px-3 py-2 text-slate-400 font-medium">Status</th>
              <th className="text-left px-3 py-2 text-slate-400 font-medium">Title</th>
              <th className="text-left px-3 py-2 text-slate-400 font-medium">Type</th>
              <th className="text-left px-3 py-2 text-slate-400 font-medium">Path</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, idx) => {
              const cfg = statusConfig[item.status] || statusConfig.error;
              return (
                <tr
                  key={idx}
                  className="border-t border-slate-700/50 hover:bg-slate-800/50"
                >
                  <td className="px-3 py-2">
                    <span className={clsx('text-xs px-1.5 py-0.5 rounded', cfg.color)}>
                      {cfg.icon} {cfg.label}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-white">{item.title}</td>
                  <td className="px-3 py-2 text-slate-400">{item.item_type}</td>
                  <td className="px-3 py-2 text-slate-500 font-mono text-xs truncate max-w-[200px]">
                    {item.path}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ImportPreview;
