/**
 * ImportWizard Component
 *
 * Sprint G: Metadata Portability
 *
 * Multi-step import wizard: Upload -> Preview -> Resolve conflicts -> Execute.
 */

import React, { useState } from 'react';
import {
  portabilityApi,
  type ImportPreviewResponse,
  type ImportConflictResolution,
  type ImportResult,
} from '../../lib/api';
import { ImportPreview } from './ImportPreview';
import { ConflictResolver } from './ConflictResolver';
import { ImportProgress } from './ImportProgress';

type ConflictAction = 'skip' | 'overwrite' | 'rename';

interface ImportWizardProps {
  targetWorkspaceId: string;
  targetSpaceId?: string;
  onClose: () => void;
  onComplete?: () => void;
}

type Step = 'upload' | 'preview' | 'executing' | 'done';

export const ImportWizard: React.FC<ImportWizardProps> = ({
  targetWorkspaceId,
  targetSpaceId,
  onClose,
  onComplete,
}) => {
  const [step, setStep] = useState<Step>('upload');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [defaultAction, setDefaultAction] = useState<ConflictAction>('skip');
  const [resolutions, setResolutions] = useState<ImportConflictResolution[]>([]);

  // Step 1: Upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const uploadResult = await portabilityApi.uploadImport(file);
      setSessionId(uploadResult.session_id);

      // Auto-preview
      const previewResult = await portabilityApi.previewImport(
        uploadResult.session_id,
        targetWorkspaceId,
        targetSpaceId,
      );
      setPreview(previewResult);
      setStep('preview');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Execute
  const handleExecute = async () => {
    if (!sessionId) return;

    setLoading(true);
    setError(null);
    setStep('executing');

    try {
      const importResult = await portabilityApi.executeImport(sessionId, {
        target_workspace_id: targetWorkspaceId,
        target_space_id: targetSpaceId,
        default_conflict_action: defaultAction,
        resolutions,
      });
      setResult(importResult);
      setStep('done');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Import failed');
      setStep('preview');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = (path: string, action: ConflictAction) => {
    setResolutions((prev) => {
      const filtered = prev.filter((r) => r.path !== path);
      return [...filtered, { path, action }];
    });
  };

  const handleClose = () => {
    if (sessionId && step !== 'done') {
      portabilityApi.cancelImport(sessionId).catch(() => {});
    }
    if (step === 'done') {
      onComplete?.();
    }
    onClose();
  };

  const conflicts = preview?.items.filter((i) => i.status === 'conflict') || [];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">
            Import Content
          </h2>
          <div className="flex gap-2 text-xs text-slate-500">
            <span className={step === 'upload' ? 'text-blue-400' : ''}>Upload</span>
            <span>{'>'}</span>
            <span className={step === 'preview' ? 'text-blue-400' : ''}>Preview</span>
            <span>{'>'}</span>
            <span className={step === 'done' ? 'text-blue-400' : ''}>Done</span>
          </div>
        </div>

        {error && (
          <div className="mb-4 text-sm text-red-400 bg-red-500/10 rounded p-2 border border-red-500/20">
            {error}
          </div>
        )}

        {/* Step: Upload */}
        {step === 'upload' && (
          <div className="space-y-4">
            <div className="text-sm text-slate-400">
              Upload a ZIP archive (exported from this platform, Confluence, or a folder of Markdown files).
            </div>

            <label className="flex flex-col items-center justify-center gap-2 p-8 border-2 border-dashed border-slate-600 rounded-lg hover:border-slate-500 cursor-pointer transition-colors">
              <div className="text-2xl text-slate-400">
                {loading ? '...' : '\u2191'}
              </div>
              <div className="text-sm text-slate-400">
                {loading ? 'Processing...' : 'Click to select file or drag and drop'}
              </div>
              <div className="text-xs text-slate-500">
                Supports: .zip (docservice, Confluence)
              </div>
              <input
                type="file"
                accept=".zip"
                onChange={handleFileUpload}
                disabled={loading}
                className="hidden"
              />
            </label>
          </div>
        )}

        {/* Step: Preview */}
        {step === 'preview' && preview && (
          <div className="space-y-4">
            <ImportPreview
              items={preview.items}
              statistics={preview.statistics}
              warnings={preview.warnings}
              formatDetected={preview.format_detected}
            />

            {conflicts.length > 0 && (
              <ConflictResolver
                conflicts={conflicts}
                resolutions={resolutions}
                onResolve={handleResolve}
                defaultAction={defaultAction}
                onDefaultActionChange={setDefaultAction}
              />
            )}
          </div>
        )}

        {/* Step: Executing */}
        {step === 'executing' && (
          <div className="py-8 text-center">
            <div className="text-slate-400 mb-2">Importing content...</div>
            <div className="w-32 h-1 bg-slate-700 rounded mx-auto overflow-hidden">
              <div className="h-full bg-blue-500 rounded animate-pulse w-2/3" />
            </div>
          </div>
        )}

        {/* Step: Done */}
        {step === 'done' && result && (
          <ImportProgress result={result} onClose={handleClose} />
        )}

        {/* Actions */}
        {step !== 'done' && (
          <div className="flex justify-end gap-3 mt-6">
            <button
              onClick={handleClose}
              disabled={loading}
              className="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            {step === 'preview' && (
              <button
                onClick={handleExecute}
                disabled={loading}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-500 disabled:opacity-50 transition-colors"
              >
                Execute Import
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ImportWizard;
