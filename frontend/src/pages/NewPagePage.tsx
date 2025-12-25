/**
 * New Page Creation Page
 *
 * Creates a new page in a space and redirects to the editor.
 */

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { contentApi } from '../lib/api';

export default function NewPagePage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const spaceId = searchParams.get('space');

  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [error, setError] = useState('');

  // Auto-generate slug from title
  useEffect(() => {
    const generatedSlug = title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
    setSlug(generatedSlug);
  }, [title]);

  const createMutation = useMutation({
    mutationFn: (data: { title: string; slug: string; space_id: string }) =>
      contentApi.create(data),
    onSuccess: (page) => {
      // Redirect to editor with the new page
      navigate(`/editor/${page.id}`, { replace: true });
    },
    onError: (err: Error & { response?: { data?: { detail?: string } } }) => {
      setError(err.response?.data?.detail || err.message || 'Failed to create page');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (!slug.trim()) {
      setError('Slug is required');
      return;
    }

    if (!spaceId) {
      setError('Space ID is required');
      return;
    }

    createMutation.mutate({
      title: title.trim(),
      slug: slug.trim(),
      space_id: spaceId,
    });
  };

  if (!spaceId) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-xl font-semibold text-white mb-4">No Space Selected</h1>
          <p className="text-slate-400 mb-6">Please select a space to create a new page.</p>
          <Link
            to="/"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-lg shadow-xl w-full max-w-md border border-slate-700">
        <div className="p-6">
          <h1 className="text-xl font-semibold text-white mb-6">Create New Page</h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-500/10 border border-red-500 text-red-400 px-3 py-2 rounded text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="page-title" className="block text-sm font-medium text-slate-300 mb-1">
                Page Title
              </label>
              <input
                id="page-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Getting Started Guide"
                autoFocus
              />
            </div>

            <div>
              <label htmlFor="page-slug" className="block text-sm font-medium text-slate-300 mb-1">
                URL Slug
              </label>
              <input
                id="page-slug"
                type="text"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="getting-started-guide"
              />
              <p className="text-xs text-slate-500 mt-1">URL-friendly identifier</p>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={() => navigate(-1)}
                className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Page'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
