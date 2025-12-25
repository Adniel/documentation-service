/**
 * Page History Page - Sprint 4 Version Control UI
 *
 * Features:
 * - View document version history
 * - Manage drafts (change requests)
 * - View diffs between versions
 * - Workflow actions (submit, approve, publish)
 */

import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useState, useCallback } from 'react';

import { contentApi } from '../lib/api';
import { useAuthStore } from '../stores/authStore';
import type { ChangeRequest } from '../types';
import {
  HistoryTimeline,
  DraftListPanel,
  DraftDetailPanel,
  CreateDraftDialog,
  DiffViewer,
} from '../components/version-control';
import { changeRequestApi } from '../lib/api';

type ViewMode = 'timeline' | 'drafts';

/**
 * Get the appropriate button label based on page status.
 * - EFFECTIVE/APPROVED pages need formal change requests
 * - DRAFT pages can be submitted for review
 */
function getActionButtonLabel(pageStatus: string): string {
  switch (pageStatus) {
    case 'effective':
    case 'approved':
      return 'Propose Changes';
    case 'in_review':
      return 'View Change Requests';
    case 'draft':
      return 'Create Change Request';
    default:
      return 'Create Change Request';
  }
}

export default function PageHistoryPage() {
  const { pageId } = useParams<{ pageId: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const [viewMode, setViewMode] = useState<ViewMode>('timeline');
  const [selectedDraft, setSelectedDraft] = useState<ChangeRequest | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedVersions, setSelectedVersions] = useState<{
    from: string | null;
    to: string | null;
  }>({ from: null, to: null });

  // Fetch page data
  const {
    data: page,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['page', pageId],
    queryFn: () => contentApi.get(pageId!),
    enabled: !!pageId,
  });

  // Fetch diff when two versions are selected
  const {
    data: versionDiff,
    isLoading: loadingDiff,
  } = useQuery({
    queryKey: ['pageDiff', pageId, selectedVersions.from, selectedVersions.to],
    queryFn: () =>
      changeRequestApi.getPageDiff(
        pageId!,
        selectedVersions.from!,
        selectedVersions.to!
      ),
    enabled: !!pageId && !!selectedVersions.from && !!selectedVersions.to,
  });

  const handleVersionSelect = useCallback(
    (sha: string) => {
      if (!selectedVersions.from) {
        setSelectedVersions({ from: sha, to: null });
      } else if (!selectedVersions.to) {
        // Ensure from is older than to
        setSelectedVersions((prev) => ({
          from: prev.from,
          to: sha,
        }));
      } else {
        // Reset and start new selection
        setSelectedVersions({ from: sha, to: null });
      }
    },
    [selectedVersions]
  );

  const handleClearVersionSelection = useCallback(() => {
    setSelectedVersions({ from: null, to: null });
  }, []);

  const handleDraftSelect = useCallback((draft: ChangeRequest) => {
    setSelectedDraft(draft);
  }, []);

  const handleDraftUpdate = useCallback((updatedDraft: ChangeRequest) => {
    setSelectedDraft(updatedDraft);
  }, []);

  const handleDraftCreated = useCallback((draft: ChangeRequest) => {
    setSelectedDraft(draft);
    setViewMode('drafts');
  }, []);

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }

  // Error state
  if (error || !page) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded">
          Failed to load page history.
        </div>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 text-blue-400 hover:text-blue-300"
        >
          ← Go back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 text-sm text-slate-400 mb-2">
          <button
            onClick={() => navigate(`/editor/${pageId}`)}
            className="hover:text-slate-300"
          >
            {page.title}
          </button>
          <span>/</span>
          <span className="text-slate-300">History</span>
        </div>
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">Version History</h1>
          <button
            onClick={() => setShowCreateDialog(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition text-sm font-medium"
          >
            {getActionButtonLabel(page.status)}
          </button>
        </div>
      </div>

      {/* View mode tabs */}
      <div className="border-b border-slate-700 mb-6">
        <nav className="flex gap-4">
          <button
            onClick={() => {
              setViewMode('timeline');
              setSelectedDraft(null);
            }}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              viewMode === 'timeline'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-300'
            }`}
          >
            Timeline
          </button>
          <button
            onClick={() => setViewMode('drafts')}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              viewMode === 'drafts'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-300'
            }`}
          >
            Change Requests
          </button>
        </nav>
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left panel - Timeline or Draft List */}
        <div className="lg:col-span-1 bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
          {viewMode === 'timeline' ? (
            <HistoryTimeline
              pageId={pageId!}
              onVersionSelect={handleVersionSelect}
              onDraftSelect={(draft) => {
                setSelectedDraft(draft);
                setViewMode('drafts');
              }}
            />
          ) : (
            <DraftListPanel
              pageId={pageId!}
              onDraftSelect={handleDraftSelect}
              onCreateDraft={() => setShowCreateDialog(true)}
            />
          )}
        </div>

        {/* Right panel - Diff Viewer or Draft Detail */}
        <div className="lg:col-span-2 bg-slate-800 rounded-lg border border-slate-700 overflow-hidden min-h-[400px]">
          {viewMode === 'timeline' ? (
            selectedVersions.from && selectedVersions.to ? (
              loadingDiff ? (
                <div className="flex items-center justify-center h-64">
                  <div className="text-slate-400">Loading diff...</div>
                </div>
              ) : versionDiff ? (
                <div className="p-4">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-sm font-medium text-slate-300">
                      Comparing versions
                    </h3>
                    <button
                      onClick={handleClearVersionSelection}
                      className="text-xs text-slate-400 hover:text-slate-300"
                    >
                      Clear selection
                    </button>
                  </div>
                  <DiffViewer diff={versionDiff} />
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-slate-400">
                  No changes between versions
                </div>
              )
            ) : (
              <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                <svg
                  className="w-12 h-12 mb-4 text-slate-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                  />
                </svg>
                <p className="text-sm">
                  {selectedVersions.from
                    ? 'Select a second version to compare'
                    : 'Select two versions from the timeline to compare'}
                </p>
              </div>
            )
          ) : selectedDraft ? (
            <DraftDetailPanel
              draft={selectedDraft}
              currentUserId={user?.id || ''}
              onClose={() => setSelectedDraft(null)}
              onUpdate={handleDraftUpdate}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-slate-400">
              <svg
                className="w-12 h-12 mb-4 text-slate-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-sm">Select a change request to view details</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Draft Dialog */}
      <CreateDraftDialog
        pageId={pageId!}
        pageTitle={page.title}
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onCreated={handleDraftCreated}
      />
    </div>
  );
}
