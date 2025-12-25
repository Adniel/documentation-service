/**
 * CreateDraftDialog - Modal for creating a new change request (draft).
 */

import { useState } from 'react';
import type { ChangeRequest } from '../../types';
import { changeRequestApi } from '../../lib/api';

interface CreateDraftDialogProps {
  pageId: string;
  pageTitle: string;
  isOpen: boolean;
  onClose: () => void;
  onCreated: (draft: ChangeRequest) => void;
}

export function CreateDraftDialog({
  pageId,
  pageTitle,
  isOpen,
  onClose,
  onCreated,
}: CreateDraftDialogProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const draft = await changeRequestApi.create(pageId, {
        title: title.trim(),
        description: description.trim() || undefined,
      });

      onCreated(draft);
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create draft');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setTitle('');
    setDescription('');
    setError(null);
    onClose();
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
        {/* Header */}
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Create New Draft</h2>
          <p className="text-sm text-gray-500 mt-1">
            Start editing &ldquo;{pageTitle}&rdquo;
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="px-6 py-4 space-y-4">
            {error && (
              <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md">
                {error}
              </div>
            )}

            <div>
              <label
                htmlFor="draft-title"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Draft Title <span className="text-red-500">*</span>
              </label>
              <input
                id="draft-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Update installation instructions"
                className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
                maxLength={500}
              />
              <p className="mt-1 text-xs text-gray-500">
                Briefly describe what you plan to change
              </p>
            </div>

            <div>
              <label
                htmlFor="draft-description"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Description (optional)
              </label>
              <textarea
                id="draft-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Provide more details about the changes..."
                className="w-full px-3 py-2 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 h-24"
              />
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3 rounded-b-lg">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !title.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create Draft'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateDraftDialog;
