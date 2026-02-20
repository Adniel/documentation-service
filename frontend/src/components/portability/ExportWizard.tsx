/**
 * ExportWizard Component
 *
 * Sprint G: Metadata Portability
 *
 * UI for exporting workspaces/spaces/organizations to ZIP archives.
 */

import React, { useState } from 'react';
import { portabilityApi } from '../../lib/api';

interface ExportWizardProps {
  scope: 'organization' | 'workspace' | 'space';
  resourceId: string;
  resourceName: string;
  onClose: () => void;
}

export const ExportWizard: React.FC<ExportWizardProps> = ({
  scope,
  resourceId,
  resourceName,
  onClose,
}) => {
  const [includeContent, setIncludeContent] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setExporting(true);
    setError(null);

    try {
      const blob = await portabilityApi.exportContent(scope, resourceId, includeContent);

      // Trigger download
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `export-${scope}-${Date.now()}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Export failed');
    } finally {
      setExporting(false);
    }
  };

  const scopeLabels = {
    organization: 'Organization',
    workspace: 'Workspace',
    space: 'Space',
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          Export {scopeLabels[scope]}
        </h2>

        <div className="space-y-4">
          <div className="bg-slate-900 rounded p-3 border border-slate-700">
            <div className="text-sm text-slate-400">Exporting</div>
            <div className="text-white font-medium">{resourceName}</div>
            <div className="text-xs text-slate-500 mt-1">
              Scope: {scopeLabels[scope]}
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={includeContent}
              onChange={(e) => setIncludeContent(e.target.checked)}
              className="rounded border-slate-600 bg-slate-700"
            />
            Include page content (JSON)
          </label>

          <div className="text-xs text-slate-500">
            The export will contain YAML metadata files and optionally JSON content
            for all pages, spaces, and workspaces in the selected scope.
          </div>

          {error && (
            <div className="text-sm text-red-400 bg-red-500/10 rounded p-2">
              {error}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onClose}
            disabled={exporting}
            className="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleExport}
            disabled={exporting}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 transition-colors"
          >
            {exporting ? 'Exporting...' : 'Export ZIP'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportWizard;
