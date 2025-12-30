/**
 * OrganizationSettingsPanel - Configure organization settings.
 *
 * Sprint B: Admin UI Completion
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { organizationApi } from '../../lib/api';

interface OrganizationSettingsPanelProps {
  organizationId: string;
}

const CLASSIFICATION_LEVELS = [
  { value: 0, label: 'Public', description: 'Visible to anyone' },
  { value: 1, label: 'Internal', description: 'Visible to authenticated users' },
  { value: 2, label: 'Confidential', description: 'Requires clearance level 2+' },
  { value: 3, label: 'Restricted', description: 'Requires clearance level 3' },
];

export function OrganizationSettingsPanel({ organizationId }: OrganizationSettingsPanelProps) {
  const queryClient = useQueryClient();

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [docNumberingEnabled, setDocNumberingEnabled] = useState(true);
  const [defaultClassification, setDefaultClassification] = useState(0);
  const [hasChanges, setHasChanges] = useState(false);

  // Fetch organization
  const { data: org, isLoading, error } = useQuery({
    queryKey: ['organization', organizationId],
    queryFn: () => organizationApi.get(organizationId),
  });

  // Initialize form when org loads
  useEffect(() => {
    if (org) {
      setName(org.name);
      setDescription(org.description || '');
      setLogoUrl(org.logo_url || '');
      // These fields might not exist yet on old orgs
      setDocNumberingEnabled((org as any).doc_numbering_enabled ?? true);
      setDefaultClassification((org as any).default_classification ?? 0);
      setHasChanges(false);
    }
  }, [org]);

  // Track changes
  useEffect(() => {
    if (org) {
      const changed =
        name !== org.name ||
        description !== (org.description || '') ||
        logoUrl !== (org.logo_url || '') ||
        docNumberingEnabled !== ((org as any).doc_numbering_enabled ?? true) ||
        defaultClassification !== ((org as any).default_classification ?? 0);
      setHasChanges(changed);
    }
  }, [name, description, logoUrl, docNumberingEnabled, defaultClassification, org]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: () =>
      organizationApi.updateSettings(organizationId, {
        name,
        description: description || undefined,
        logo_url: logoUrl || undefined,
        doc_numbering_enabled: docNumberingEnabled,
        default_classification: defaultClassification,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organization', organizationId] });
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate();
  };

  const handleReset = () => {
    if (org) {
      setName(org.name);
      setDescription(org.description || '');
      setLogoUrl(org.logo_url || '');
      setDocNumberingEnabled((org as any).doc_numbering_enabled ?? true);
      setDefaultClassification((org as any).default_classification ?? 0);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Failed to load organization settings. Please try again.
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* General Settings */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">General Settings</h3>
        <p className="text-sm text-gray-500">Basic information about your organization.</p>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Organization Name
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              required
            />
          </div>

          <div>
            <label htmlFor="logo" className="block text-sm font-medium text-gray-700">
              Logo URL
            </label>
            <input
              type="url"
              id="logo"
              value={logoUrl}
              onChange={(e) => setLogoUrl(e.target.value)}
              placeholder="https://example.com/logo.png"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
            />
          </div>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
          />
        </div>
      </div>

      {/* Document Control Settings */}
      <div className="space-y-4 pt-6 border-t border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Document Control</h3>
        <p className="text-sm text-gray-500">Configure how documents are numbered and classified.</p>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="docNumbering"
            checked={docNumberingEnabled}
            onChange={(e) => setDocNumberingEnabled(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="docNumbering" className="ml-3 text-sm text-gray-700">
            Enable automatic document numbering
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Default Classification Level
          </label>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {CLASSIFICATION_LEVELS.map((level) => (
              <label
                key={level.value}
                className={`flex items-center p-3 border rounded-lg cursor-pointer transition ${
                  defaultClassification === level.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="classification"
                  value={level.value}
                  checked={defaultClassification === level.value}
                  onChange={(e) => setDefaultClassification(parseInt(e.target.value))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500"
                />
                <div className="ml-2">
                  <div className="text-sm font-medium text-gray-900">{level.label}</div>
                  <div className="text-xs text-gray-500">{level.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {updateMutation.isSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-md p-3 text-sm text-green-700">
          Settings saved successfully.
        </div>
      )}

      {updateMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
          Failed to save settings. Please try again.
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={handleReset}
          disabled={!hasChanges}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Reset
        </button>
        <button
          type="submit"
          disabled={!hasChanges || updateMutation.isPending}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </form>
  );
}
