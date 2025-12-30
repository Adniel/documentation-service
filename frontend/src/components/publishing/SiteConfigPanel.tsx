/**
 * SiteConfigPanel - Configuration panel for published documentation sites.
 *
 * Allows managing site settings including slug, visibility, features, and theme.
 *
 * Sprint A: Publishing
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  publishingApi,
  spaceApi,
  type PublishedSite,
  type SiteCreate,
  type SiteUpdate,
  type SiteVisibility,
  type Theme,
} from '../../lib/api';

interface SiteConfigPanelProps {
  organizationId: string;
  onSiteCreated?: (site: PublishedSite) => void;
}

export function SiteConfigPanel({ organizationId, onSiteCreated }: SiteConfigPanelProps) {
  const queryClient = useQueryClient();
  const [selectedSpaceId, setSelectedSpaceId] = useState<string>('');
  const [isCreating, setIsCreating] = useState(false);

  // Form state
  const [slug, setSlug] = useState('');
  const [siteTitle, setSiteTitle] = useState('');
  const [siteDescription, setSiteDescription] = useState('');
  const [visibility, setVisibility] = useState<SiteVisibility>('public');
  const [themeId, setThemeId] = useState<string>('');
  const [searchEnabled, setSearchEnabled] = useState(true);
  const [tocEnabled, setTocEnabled] = useState(true);
  const [feedbackEnabled, setFeedbackEnabled] = useState(false);
  const [analyticsId, setAnalyticsId] = useState('');
  const [allowedDomains, setAllowedDomains] = useState('');

  // Fetch sites
  const { data: sites = [], isLoading: loadingSites } = useQuery({
    queryKey: ['sites', organizationId],
    queryFn: () => publishingApi.listSites({ organization_id: organizationId }),
  });

  // Fetch themes
  const { data: themes = [] } = useQuery({
    queryKey: ['themes', organizationId],
    queryFn: () => publishingApi.listThemes({ organization_id: organizationId, include_system: true }),
  });

  // Fetch spaces (to allow creating new sites)
  const { data: workspaces = [] } = useQuery({
    queryKey: ['workspaces', organizationId],
    queryFn: async () => {
      // We need to get workspaces and then spaces
      const { workspaceApi } = await import('../../lib/api');
      return workspaceApi.listByOrg(organizationId);
    },
  });

  // Get spaces for all workspaces
  const { data: allSpaces = [] } = useQuery({
    queryKey: ['allSpaces', workspaces.map(w => w.id)],
    queryFn: async () => {
      const spaces = await Promise.all(
        workspaces.map(w => spaceApi.listByWorkspace(w.id))
      );
      return spaces.flat();
    },
    enabled: workspaces.length > 0,
  });

  // Filter spaces that don't have sites yet
  const availableSpaces = allSpaces.filter(
    space => !sites.some(site => site.space_id === space.id)
  );

  // Create site mutation
  const createMutation = useMutation({
    mutationFn: (data: SiteCreate) => publishingApi.createSite(data),
    onSuccess: (site) => {
      queryClient.invalidateQueries({ queryKey: ['sites'] });
      setIsCreating(false);
      resetForm();
      onSiteCreated?.(site);
    },
  });

  // Update site mutation
  const updateMutation = useMutation({
    mutationFn: ({ siteId, data }: { siteId: string; data: SiteUpdate }) =>
      publishingApi.updateSite(siteId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] });
    },
  });

  // Delete site mutation
  const deleteMutation = useMutation({
    mutationFn: (siteId: string) => publishingApi.deleteSite(siteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sites'] });
    },
  });

  const resetForm = () => {
    setSlug('');
    setSiteTitle('');
    setSiteDescription('');
    setVisibility('public');
    setThemeId('');
    setSearchEnabled(true);
    setTocEnabled(true);
    setFeedbackEnabled(false);
    setAnalyticsId('');
    setAllowedDomains('');
    setSelectedSpaceId('');
  };

  const handleCreate = () => {
    if (!selectedSpaceId || !slug || !siteTitle) return;

    createMutation.mutate({
      space_id: selectedSpaceId,
      slug,
      site_title: siteTitle,
      site_description: siteDescription || undefined,
      theme_id: themeId || undefined,
      visibility,
      allowed_email_domains: allowedDomains ? allowedDomains.split(',').map(d => d.trim()) : undefined,
      search_enabled: searchEnabled,
      toc_enabled: tocEnabled,
      feedback_enabled: feedbackEnabled,
      analytics_id: analyticsId || undefined,
    });
  };

  const handleDelete = (siteId: string, siteName: string) => {
    if (window.confirm(`Are you sure you want to delete the site "${siteName}"? This cannot be undone.`)) {
      deleteMutation.mutate(siteId);
    }
  };

  if (loadingSites) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Existing Sites */}
      {sites.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-gray-700">Published Sites</h3>
          <div className="grid gap-4">
            {sites.map((site) => (
              <SiteCard
                key={site.id}
                site={site}
                themes={themes}
                onUpdate={(data) => updateMutation.mutate({ siteId: site.id, data })}
                onDelete={() => handleDelete(site.id, site.site_title)}
                isUpdating={updateMutation.isPending}
              />
            ))}
          </div>
        </div>
      )}

      {/* Create New Site */}
      {!isCreating && availableSpaces.length > 0 && (
        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create New Site
        </button>
      )}

      {isCreating && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Create New Site</h3>

          <div className="grid grid-cols-2 gap-4">
            {/* Space Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Space *
              </label>
              <select
                value={selectedSpaceId}
                onChange={(e) => {
                  setSelectedSpaceId(e.target.value);
                  const space = allSpaces.find(s => s.id === e.target.value);
                  if (space) {
                    setSiteTitle(space.name);
                    setSlug(space.slug);
                  }
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              >
                <option value="">Select a space...</option>
                {availableSpaces.map((space) => (
                  <option key={space.id} value={space.id}>
                    {space.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Theme Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Theme
              </label>
              <select
                value={themeId}
                onChange={(e) => setThemeId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              >
                <option value="">Default Theme</option>
                {themes.map((theme) => (
                  <option key={theme.id} value={theme.id}>
                    {theme.name} {theme.is_default ? '(Default)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Site Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Site Title *
              </label>
              <input
                type="text"
                value={siteTitle}
                onChange={(e) => setSiteTitle(e.target.value)}
                placeholder="My Documentation"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              />
            </div>

            {/* Slug */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                URL Slug *
              </label>
              <div className="flex">
                <span className="inline-flex items-center px-3 border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm rounded-l-md">
                  /s/
                </span>
                <input
                  type="text"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                  placeholder="my-docs"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-r-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                />
              </div>
            </div>

            {/* Description */}
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={siteDescription}
                onChange={(e) => setSiteDescription(e.target.value)}
                rows={2}
                placeholder="A brief description of your documentation site..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              />
            </div>

            {/* Visibility */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Visibility
              </label>
              <select
                value={visibility}
                onChange={(e) => setVisibility(e.target.value as SiteVisibility)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              >
                <option value="public">Public</option>
                <option value="authenticated">Authenticated Users Only</option>
                <option value="restricted">Restricted (Email Domains)</option>
              </select>
            </div>

            {/* Allowed Domains (for restricted) */}
            {visibility === 'restricted' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Allowed Email Domains
                </label>
                <input
                  type="text"
                  value={allowedDomains}
                  onChange={(e) => setAllowedDomains(e.target.value)}
                  placeholder="example.com, company.org"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                />
              </div>
            )}

            {/* Analytics ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Analytics ID
              </label>
              <input
                type="text"
                value={analyticsId}
                onChange={(e) => setAnalyticsId(e.target.value)}
                placeholder="G-XXXXXXXXXX"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              />
            </div>
          </div>

          {/* Feature Toggles */}
          <div className="flex flex-wrap gap-6 pt-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={searchEnabled}
                onChange={(e) => setSearchEnabled(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Enable Search</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={tocEnabled}
                onChange={(e) => setTocEnabled(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Show Table of Contents</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={feedbackEnabled}
                onChange={(e) => setFeedbackEnabled(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Enable Feedback</span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              onClick={handleCreate}
              disabled={!selectedSpaceId || !slug || !siteTitle || createMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Site'}
            </button>
            <button
              onClick={() => {
                setIsCreating(false);
                resetForm();
              }}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md transition"
            >
              Cancel
            </button>
          </div>

          {createMutation.isError && (
            <p className="text-sm text-red-600">
              Error: {(createMutation.error as Error).message}
            </p>
          )}
        </div>
      )}

      {sites.length === 0 && !isCreating && availableSpaces.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No spaces available to publish.</p>
          <p className="text-sm">Create a space first to set up a published site.</p>
        </div>
      )}
    </div>
  );
}

// Site card component for displaying/editing individual sites
interface SiteCardProps {
  site: PublishedSite;
  themes: Theme[];
  onUpdate: (data: SiteUpdate) => void;
  onDelete: () => void;
  isUpdating: boolean;
}

function SiteCard({ site, themes, onUpdate, onDelete, isUpdating }: SiteCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<SiteUpdate>({});

  const statusColors = {
    draft: 'bg-gray-100 text-gray-700',
    published: 'bg-green-100 text-green-700',
    maintenance: 'bg-yellow-100 text-yellow-700',
    archived: 'bg-red-100 text-red-700',
  };

  const handleSave = () => {
    onUpdate(editData);
    setIsEditing(false);
    setEditData({});
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h4 className="text-lg font-medium text-gray-900">{site.site_title}</h4>
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${statusColors[site.status]}`}>
              {site.status}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            <a
              href={site.public_url || `/s/${site.slug}`}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-blue-600"
            >
              /s/{site.slug}
            </a>
          </p>
          {site.site_description && (
            <p className="text-sm text-gray-600 mt-2">{site.site_description}</p>
          )}
          <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
            <span>Visibility: {site.visibility}</span>
            {site.last_published_at && (
              <span>Last published: {new Date(site.last_published_at).toLocaleDateString()}</span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="p-2 text-gray-400 hover:text-gray-600"
            title="Edit"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={onDelete}
            className="p-2 text-gray-400 hover:text-red-600"
            title="Delete"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {isEditing && (
        <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Site Title</label>
              <input
                type="text"
                defaultValue={site.site_title}
                onChange={(e) => setEditData({ ...editData, site_title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white text-gray-900"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
              <select
                defaultValue={site.theme_id || ''}
                onChange={(e) => setEditData({ ...editData, theme_id: e.target.value || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white text-gray-900"
              >
                <option value="">Default Theme</option>
                {themes.map((theme) => (
                  <option key={theme.id} value={theme.id}>
                    {theme.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleSave}
              disabled={isUpdating}
              className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
            >
              {isUpdating ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={() => {
                setIsEditing(false);
                setEditData({});
              }}
              className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-md"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SiteConfigPanel;
