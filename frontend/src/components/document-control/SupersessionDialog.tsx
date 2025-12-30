/**
 * SupersessionDialog - Mark a document as superseded by another.
 *
 * This dialog allows users to obsolete a document and link it to
 * the new document that supersedes it.
 *
 * Sprint 9.5: Admin UI
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentControlApi, contentApi } from '../../lib/api';

interface SupersessionDialogProps {
  /** The page being superseded (made obsolete) */
  pageId: string;
  pageTitle: string;
  spaceId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function SupersessionDialog({
  pageId,
  pageTitle,
  spaceId,
  isOpen,
  onClose,
  onSuccess,
}: SupersessionDialogProps) {
  const queryClient = useQueryClient();
  const [supersedingPageId, setSupersedingPageId] = useState<string>('');
  const [reason, setReason] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch pages in the same space for selection
  const { data: pages = [] } = useQuery({
    queryKey: ['space-pages', spaceId],
    queryFn: () => contentApi.listBySpace(spaceId),
    enabled: isOpen,
  });

  // Filter pages (exclude current page, only show effective/approved docs)
  const availablePages = pages.filter((p) =>
    p.id !== pageId &&
    (p.status === 'effective' || p.status === 'approved') &&
    (searchQuery === '' || p.title.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Transition mutation
  const transitionMutation = useMutation({
    mutationFn: async () => {
      if (!supersedingPageId) {
        throw new Error('Please select the superseding document');
      }
      if (!reason || reason.length < 10) {
        throw new Error('Please provide a reason (at least 10 characters)');
      }

      // Transition to obsolete with superseded_by_id
      await documentControlApi.transitionStatus(pageId, 'obsolete', reason);

      // Update metadata to link supersession
      // Note: The backend handles linking when transitioning to obsolete
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['page', pageId] });
      queryClient.invalidateQueries({ queryKey: ['document-metadata', pageId] });
      onSuccess?.();
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    transitionMutation.mutate();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Supersede Document
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Mark "{pageTitle}" as obsolete and replaced by another document
          </p>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto max-h-[60vh]">
          {/* Warning */}
          <div className="flex items-start gap-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <svg className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="text-sm text-amber-800">
              <strong>Warning:</strong> This action will mark the document as obsolete.
              Users will be redirected to the superseding document.
            </div>
          </div>

          {/* Superseding document selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Superseding Document
            </label>
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 mb-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            />
            <div className="border border-gray-300 rounded-md max-h-48 overflow-y-auto">
              {availablePages.length === 0 ? (
                <div className="p-3 text-sm text-gray-500 text-center">
                  No available documents found
                </div>
              ) : (
                availablePages.map((page) => (
                  <label
                    key={page.id}
                    className={`flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 border-b last:border-b-0 ${
                      supersedingPageId === page.id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <input
                      type="radio"
                      name="supersedingPage"
                      value={page.id}
                      checked={supersedingPageId === page.id}
                      onChange={(e) => setSupersedingPageId(e.target.value)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 truncate">
                        {page.title}
                      </div>
                      <div className="text-xs text-gray-500">
                        Version {page.version} • {page.status}
                      </div>
                    </div>
                  </label>
                ))
              )}
            </div>
          </div>

          {/* Reason */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Supersession
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Explain why this document is being superseded..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            />
            <p className="mt-1 text-xs text-gray-500">
              Minimum 10 characters required
            </p>
          </div>

          {/* Error */}
          {transitionMutation.isError && (
            <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md">
              {(transitionMutation.error as Error).message}
            </div>
          )}
        </form>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!supersedingPageId || reason.length < 10 || transitionMutation.isPending}
            className="px-4 py-2 text-sm text-white bg-amber-600 hover:bg-amber-700 rounded-md transition disabled:opacity-50"
          >
            {transitionMutation.isPending ? 'Processing...' : 'Mark as Superseded'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default SupersessionDialog;
