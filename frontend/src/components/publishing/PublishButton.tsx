/**
 * PublishButton - Button component for publishing/unpublishing sites.
 *
 * Handles the publish workflow with confirmation and status display.
 *
 * Sprint A: Publishing
 */

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { publishingApi, type PublishedSite, type PublishResult } from '../../lib/api';

interface PublishButtonProps {
  site: PublishedSite;
  onPublished?: (result: PublishResult) => void;
  onUnpublished?: (site: PublishedSite) => void;
  size?: 'sm' | 'md' | 'lg';
}

export function PublishButton({ site, onPublished, onUnpublished, size = 'md' }: PublishButtonProps) {
  const queryClient = useQueryClient();
  const [showConfirm, setShowConfirm] = useState(false);
  const [commitMessage, setCommitMessage] = useState('');

  const isPublished = site.status === 'published';

  const publishMutation = useMutation({
    mutationFn: () => publishingApi.publishSite(site.id, commitMessage || undefined),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['sites'] });
      setShowConfirm(false);
      setCommitMessage('');
      onPublished?.(result);
    },
  });

  const unpublishMutation = useMutation({
    mutationFn: () => publishingApi.unpublishSite(site.id),
    onSuccess: (updatedSite) => {
      queryClient.invalidateQueries({ queryKey: ['sites'] });
      setShowConfirm(false);
      onUnpublished?.(updatedSite);
    },
  });

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  const handleClick = () => {
    setShowConfirm(true);
  };

  const handleConfirm = () => {
    if (isPublished) {
      unpublishMutation.mutate();
    } else {
      publishMutation.mutate();
    }
  };

  const isLoading = publishMutation.isPending || unpublishMutation.isPending;

  return (
    <>
      <button
        onClick={handleClick}
        disabled={isLoading}
        className={`${sizeClasses[size]} font-medium rounded-md transition flex items-center gap-2 ${
          isPublished
            ? 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300'
            : 'bg-green-600 text-white hover:bg-green-700'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        {isLoading ? (
          <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : isPublished ? (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
        ) : (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
        )}
        {isPublished ? 'Unpublish' : 'Publish'}
      </button>

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {isPublished ? 'Unpublish Site' : 'Publish Site'}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              {isPublished
                ? `Are you sure you want to unpublish "${site.site_title}"? The site will no longer be accessible to visitors.`
                : `Publish "${site.site_title}" to make it accessible at ${site.public_url || `/s/${site.slug}`}`}
            </p>

            {!isPublished && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Publish Message (optional)
                </label>
                <input
                  type="text"
                  value={commitMessage}
                  onChange={(e) => setCommitMessage(e.target.value)}
                  placeholder="Describe what changed..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            )}

            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowConfirm(false);
                  setCommitMessage('');
                }}
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={isLoading}
                className={`px-4 py-2 text-sm font-medium text-white rounded-md transition disabled:opacity-50 ${
                  isPublished
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {isLoading ? 'Processing...' : isPublished ? 'Unpublish' : 'Publish'}
              </button>
            </div>

            {(publishMutation.isError || unpublishMutation.isError) && (
              <p className="mt-3 text-sm text-red-600">
                Error: {((publishMutation.error || unpublishMutation.error) as Error).message}
              </p>
            )}
          </div>
        </div>
      )}
    </>
  );
}

// Site status badge component
interface SiteStatusBadgeProps {
  status: PublishedSite['status'];
}

export function SiteStatusBadge({ status }: SiteStatusBadgeProps) {
  const statusConfig = {
    draft: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Draft' },
    published: { bg: 'bg-green-100', text: 'text-green-700', label: 'Published' },
    maintenance: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Maintenance' },
    archived: { bg: 'bg-red-100', text: 'text-red-700', label: 'Archived' },
  };

  const config = statusConfig[status];

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
      {config.label}
    </span>
  );
}

export default PublishButton;
