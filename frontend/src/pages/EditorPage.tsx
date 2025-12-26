/**
 * Editor Page - Sprint 2 Enhanced Version
 *
 * Features:
 * - TipTap block editor with extensions
 * - Slash command menu
 * - Auto-save with debounce
 * - Markdown export
 * - Keyboard shortcuts
 */

import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import Link from '@tiptap/extension-link';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight';
import { useCallback, useEffect, useState } from 'react';

import { contentApi, spaceApi, learningApi } from '../lib/api';
import type { Assessment } from '../lib/api';
import { useAutoSave } from '../hooks/useAutoSave';
import { AssessmentBuilder } from '../components/learning';
import { useEditorShortcuts } from '../hooks/useEditorShortcuts';
import { EditorToolbar } from '../components/editor/EditorToolbar';
import { SaveStatusIndicator } from '../components/editor/SaveStatusIndicator';
import { SlashCommand } from '../components/editor/extensions/SlashCommand';
import { exportToMarkdown } from '../lib/markdown';
import type { EditorDocument } from '../types/editor';

// Status explanations for document lifecycle
const STATUS_INFO: Record<string, { label: string; description: string; isControlled: boolean }> = {
  draft: {
    label: 'Draft',
    description: 'This document is being written. You can edit it directly.',
    isControlled: false,
  },
  in_review: {
    label: 'In Review',
    description: 'This document is being reviewed. Direct editing is disabled.',
    isControlled: true,
  },
  approved: {
    label: 'Approved',
    description: 'This document is approved. Changes require a formal change request.',
    isControlled: true,
  },
  effective: {
    label: 'Effective',
    description: 'This is the official version. Changes require a formal change request.',
    isControlled: true,
  },
  obsolete: {
    label: 'Obsolete',
    description: 'This document has been replaced by a newer version.',
    isControlled: true,
  },
  archived: {
    label: 'Archived',
    description: 'This document is archived and read-only.',
    isControlled: true,
  },
};

// Create lowlight instance for syntax highlighting
const lowlight = createLowlight(common);

export default function EditorPage() {
  const { pageId } = useParams<{ pageId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [wordCount, setWordCount] = useState(0);
  const [showAssessmentBuilder, setShowAssessmentBuilder] = useState(false);

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

  // Fetch space details for navigation
  const { data: space } = useQuery({
    queryKey: ['space', page?.space_id],
    queryFn: () => spaceApi.get(page!.space_id),
    enabled: !!page?.space_id,
  });

  // Fetch assessment for this page (if any)
  const { data: assessment, refetch: refetchAssessment } = useQuery({
    queryKey: ['page-assessment', pageId],
    queryFn: () => learningApi.getPageAssessment(pageId!),
    enabled: !!pageId,
    retry: false, // Don't retry on 404
  });

  // Create assessment mutation
  const createAssessmentMutation = useMutation({
    mutationFn: (data: { title: string; description?: string; passing_score?: number }) =>
      learningApi.createAssessment({
        page_id: pageId!,
        title: data.title,
        description: data.description,
        passing_score: data.passing_score || 80,
      }),
    onSuccess: () => {
      refetchAssessment();
      setShowAssessmentBuilder(true);
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (content: Record<string, unknown>) =>
      contentApi.update(pageId!, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['page', pageId] });
    },
  });

  // Auto-save hook
  const { status: saveStatus, triggerSave, saveNow, lastSavedAt, error: saveError } = useAutoSave({
    debounceMs: 2000,
    onSave: async (content) => {
      await updateMutation.mutateAsync(content as Record<string, unknown>);
    },
    enabled: true,
  });

  // Initialize TipTap editor with extensions
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4, 5, 6],
        },
        codeBlock: false, // Use CodeBlockLowlight instead
      }),
      Placeholder.configure({
        placeholder: 'Type "/" for commands, or start writing...',
      }),
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableCell,
      TableHeader,
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-400 hover:text-blue-300 underline',
        },
      }),
      CodeBlockLowlight.configure({
        lowlight,
        defaultLanguage: 'plaintext',
      }),
      SlashCommand,
    ],
    content: '',
    editorProps: {
      attributes: {
        class:
          'prose prose-invert prose-slate max-w-none focus:outline-none min-h-[400px]',
      },
    },
    onUpdate: ({ editor }) => {
      // Trigger auto-save
      const content = {
        type: 'doc',
        content: editor.getJSON().content,
      };
      triggerSave(content);

      // Update word count
      const text = editor.getText();
      const words = text.trim().split(/\s+/).filter(Boolean).length;
      setWordCount(words);
    },
  });

  // Load content when page data arrives
  useEffect(() => {
    if (editor && page?.content) {
      const contentData = page.content as { content?: unknown };
      if (contentData.content) {
        editor.commands.setContent(
          contentData.content as Parameters<typeof editor.commands.setContent>[0]
        );
      } else if (contentData) {
        // Try setting the whole content object
        editor.commands.setContent(
          page.content as Parameters<typeof editor.commands.setContent>[0]
        );
      }

      // Calculate initial word count
      const text = editor.getText();
      const words = text.trim().split(/\s+/).filter(Boolean).length;
      setWordCount(words);
    }
  }, [editor, page]);

  // Manual save handler
  const handleSave = useCallback(() => {
    if (editor) {
      const content = {
        type: 'doc',
        content: editor.getJSON().content,
      };
      saveNow(content);
    }
  }, [editor, saveNow]);

  // Export to Markdown
  const handleExport = useCallback(() => {
    if (!editor || !page) return;

    const doc = editor.getJSON() as EditorDocument;
    const markdown = exportToMarkdown(doc, {
      includeMetadata: true,
      title: page.title,
    });

    // Download as file
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${page.slug}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, [editor, page]);

  // Keyboard shortcuts
  useEditorShortcuts({
    onSave: handleSave,
    onExport: handleExport,
    enabled: true,
  });

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading editor...</div>
      </div>
    );
  }

  // Error state
  if (error || !page) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded">
          Failed to load page. The document may have been deleted or you don't
          have access.
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
    <div className="max-w-4xl mx-auto px-4 py-6">
      {/* Breadcrumb navigation */}
      <nav className="mb-4 text-sm">
        <ol className="flex items-center gap-2 text-slate-400">
          <li>
            <RouterLink to="/" className="hover:text-white transition-colors">
              Dashboard
            </RouterLink>
          </li>
          {space && (
            <>
              <li className="text-slate-600">/</li>
              <li>
                <RouterLink
                  to={`/workspace/${space.workspace_id}?space=${space.id}`}
                  className="hover:text-white transition-colors"
                >
                  {space.name}
                </RouterLink>
              </li>
            </>
          )}
          <li className="text-slate-600">/</li>
          <li className="text-white font-medium truncate max-w-xs">{page.title}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-white">{page.title}</h1>
            <div className="flex items-center gap-4 mt-2">
              <span className="text-sm text-slate-400">
                Version {page.version}
              </span>
              <span
                className={`text-xs px-2 py-1 rounded font-medium cursor-help ${
                  page.status === 'draft'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : page.status === 'effective'
                    ? 'bg-green-500/20 text-green-400'
                    : page.status === 'in_review'
                    ? 'bg-blue-500/20 text-blue-400'
                    : page.status === 'approved'
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-slate-500/20 text-slate-400'
                }`}
                title={STATUS_INFO[page.status]?.description || page.status}
              >
                {STATUS_INFO[page.status]?.label || page.status.replace('_', ' ')}
              </span>
              {page.document_number && (
                <span className="text-xs text-slate-500 font-mono">
                  {page.document_number}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <SaveStatusIndicator
              status={saveStatus}
              lastSavedAt={lastSavedAt}
              error={saveError}
            />
            <div className="flex gap-2">
              <button
                onClick={() => {
                  if (assessment) {
                    setShowAssessmentBuilder(true);
                  } else {
                    createAssessmentMutation.mutate({
                      title: `Assessment: ${page.title}`,
                      description: `Quiz for ${page.title}`,
                    });
                  }
                }}
                disabled={createAssessmentMutation.isPending}
                className={`px-3 py-2 rounded-md transition text-sm flex items-center gap-1.5 ${
                  assessment
                    ? 'text-green-400 hover:text-green-300 hover:bg-slate-700'
                    : 'text-slate-300 hover:text-white hover:bg-slate-700'
                }`}
                title={assessment ? 'Edit Assessment' : 'Add Assessment'}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                {createAssessmentMutation.isPending
                  ? 'Creating...'
                  : assessment
                  ? 'Assessment'
                  : 'Add Assessment'}
              </button>
              <button
                onClick={handleExport}
                className="px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-700 rounded-md transition text-sm"
                title="Export as Markdown (Cmd+Shift+E)"
              >
                Export
              </button>
              <button
                onClick={handleSave}
                disabled={saveStatus === 'saving'}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50 text-sm font-medium"
                title="Save (Cmd+S)"
              >
                {saveStatus === 'saving' ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Controlled Document Banner - shown for EFFECTIVE/IN_REVIEW/APPROVED pages */}
      {STATUS_INFO[page.status]?.isControlled && (
        <div className="mb-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-blue-400">
                Controlled Document
              </h3>
              <p className="mt-1 text-sm text-slate-300">
                {STATUS_INFO[page.status]?.description} To propose changes:
              </p>
              <ol className="mt-2 text-sm text-slate-400 list-decimal list-inside space-y-1">
                <li>Click "Propose Changes" to create a change request</li>
                <li>Make your edits in the draft version</li>
                <li>Submit for review when ready</li>
              </ol>
              <button
                onClick={() => navigate(`/pages/${pageId}/history`)}
                className="mt-3 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Propose Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toolbar */}
      <EditorToolbar editor={editor} />

      {/* Editor */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 min-h-[500px]">
        <EditorContent editor={editor} />
      </div>

      {/* Status bar */}
      <div className="mt-4 flex justify-between items-center text-sm text-slate-500">
        <div className="flex items-center gap-4">
          <span>{wordCount} words</span>
          {page.git_commit_sha && (
            <span className="font-mono text-xs">
              commit: {page.git_commit_sha.slice(0, 7)}
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <span>
            Updated: {new Date(page.updated_at).toLocaleString()}
          </span>
          <button
            onClick={() => navigate(`/pages/${pageId}/history`)}
            className="text-blue-400 hover:text-blue-300"
          >
            View history
          </button>
        </div>
      </div>

      {/* Keyboard shortcuts help */}
      <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
        <h3 className="text-sm font-medium text-slate-300 mb-2">
          Keyboard shortcuts
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-slate-400">
          <span>
            <kbd className="bg-slate-700 px-1 rounded">Cmd+S</kbd> Save
          </span>
          <span>
            <kbd className="bg-slate-700 px-1 rounded">Cmd+B</kbd> Bold
          </span>
          <span>
            <kbd className="bg-slate-700 px-1 rounded">Cmd+I</kbd> Italic
          </span>
          <span>
            <kbd className="bg-slate-700 px-1 rounded">/</kbd> Commands
          </span>
          <span>
            <kbd className="bg-slate-700 px-1 rounded">#</kbd> Heading
          </span>
          <span>
            <kbd className="bg-slate-700 px-1 rounded">-</kbd> List
          </span>
          <span>
            <kbd className="bg-slate-700 px-1 rounded">```</kbd> Code
          </span>
          <span>
            <kbd className="bg-slate-700 px-1 rounded">&gt;</kbd> Quote
          </span>
        </div>
      </div>

      {/* Assessment Builder Modal */}
      {showAssessmentBuilder && assessment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <AssessmentBuilder
              assessmentId={assessment.id}
              onCancel={() => setShowAssessmentBuilder(false)}
              onSave={() => {
                setShowAssessmentBuilder(false);
                refetchAssessment();
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
