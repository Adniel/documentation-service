/**
 * Create Space Modal Component
 *
 * Modal dialog for creating a new space within a workspace.
 */

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { spaceApi } from '../lib/api';

interface CreateSpaceModalProps {
  isOpen: boolean;
  onClose: () => void;
  workspaceId: string;
  workspaceName: string;
}

const DIATAXIS_TYPES = [
  { value: 'tutorial', label: 'Tutorial', icon: '📚', description: 'Learning-oriented, step-by-step guides' },
  { value: 'how_to', label: 'How-to Guide', icon: '🔧', description: 'Task-oriented, practical steps' },
  { value: 'reference', label: 'Reference', icon: '📖', description: 'Information-oriented, technical details' },
  { value: 'explanation', label: 'Explanation', icon: '💡', description: 'Understanding-oriented, background info' },
];

export default function CreateSpaceModal({
  isOpen,
  onClose,
  workspaceId,
  workspaceName,
}: CreateSpaceModalProps) {
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [diataxisType, setDiataxisType] = useState('tutorial');
  const [error, setError] = useState('');

  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: { name: string; slug: string; workspace_id: string; description?: string; diataxis_type: string }) =>
      spaceApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-spaces', workspaceId] });
      queryClient.invalidateQueries({ queryKey: ['workspace-tree', workspaceId] });
      handleClose();
    },
    onError: (err: Error & { response?: { data?: { detail?: string } } }) => {
      setError(err.response?.data?.detail || err.message || 'Failed to create space');
    },
  });

  const handleClose = () => {
    setName('');
    setSlug('');
    setDescription('');
    setDiataxisType('tutorial');
    setError('');
    onClose();
  };

  const handleNameChange = (newName: string) => {
    setName(newName);
    // Auto-generate slug from name
    const generatedSlug = newName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
    setSlug(generatedSlug);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Name is required');
      return;
    }

    if (!slug.trim()) {
      setError('Slug is required');
      return;
    }

    createMutation.mutate({
      name: name.trim(),
      slug: slug.trim(),
      workspace_id: workspaceId,
      description: description.trim() || undefined,
      diataxis_type: diataxisType,
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-slate-800 rounded-lg shadow-xl w-full max-w-md mx-4 border border-slate-700">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-white mb-1">Create Space</h2>
          <p className="text-sm text-slate-400 mb-6">
            in {workspaceName}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-500/10 border border-red-500 text-red-400 px-3 py-2 rounded text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="space-name" className="block text-sm font-medium text-slate-300 mb-1">
                Name
              </label>
              <input
                id="space-name"
                type="text"
                value={name}
                onChange={(e) => handleNameChange(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Getting Started"
                autoFocus
              />
            </div>

            <div>
              <label htmlFor="space-slug" className="block text-sm font-medium text-slate-300 mb-1">
                Slug
              </label>
              <input
                id="space-slug"
                type="text"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="getting-started"
              />
              <p className="text-xs text-slate-500 mt-1">URL-friendly identifier</p>
            </div>

            <div>
              <label htmlFor="space-description" className="block text-sm font-medium text-slate-300 mb-1">
                Description
              </label>
              <textarea
                id="space-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="What is this space about?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Content Type (Diátaxis)
              </label>
              <div className="grid grid-cols-2 gap-2">
                {DIATAXIS_TYPES.map((type) => (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setDiataxisType(type.value)}
                    className={`p-3 rounded-md border text-left transition-colors ${
                      diataxisType === type.value
                        ? 'bg-blue-600/20 border-blue-500 text-white'
                        : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span>{type.icon}</span>
                      <span className="font-medium">{type.label}</span>
                    </div>
                    <p className="text-xs text-slate-400">{type.description}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={handleClose}
                className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Space'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
