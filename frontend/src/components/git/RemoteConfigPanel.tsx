/**
 * RemoteConfigPanel - Configure Git remote sync for an organization.
 *
 * Sprint 13: Git Remote Support
 */

import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  gitApi,
  type RemoteConfigCreate,
  type GitProvider,
  type SyncStrategy,
  type CredentialType,
} from '../../lib/api';

interface RemoteConfigPanelProps {
  organizationId: string;
}

const PROVIDERS: { value: GitProvider; label: string; urlHint: string }[] = [
  { value: 'github', label: 'GitHub', urlHint: 'git@github.com:owner/repo.git' },
  { value: 'gitlab', label: 'GitLab', urlHint: 'git@gitlab.com:owner/repo.git' },
  { value: 'gitea', label: 'Gitea', urlHint: 'git@gitea.example.com:owner/repo.git' },
  { value: 'custom', label: 'Custom', urlHint: 'git@your-server.com:repo.git' },
];

const SYNC_STRATEGIES: { value: SyncStrategy; label: string; description: string }[] = [
  { value: 'push_only', label: 'Push Only', description: 'Local changes push to remote (backup mode)' },
  { value: 'pull_only', label: 'Pull Only', description: 'Pull changes from remote (read-only mode)' },
  { value: 'bidirectional', label: 'Bidirectional', description: 'Sync both ways (requires conflict handling)' },
];

const CREDENTIAL_TYPES: { value: CredentialType; label: string }[] = [
  { value: 'https_token', label: 'Personal Access Token (HTTPS)' },
  { value: 'ssh_key', label: 'SSH Key' },
  { value: 'deploy_key', label: 'Deploy Key' },
];

export function RemoteConfigPanel({ organizationId }: RemoteConfigPanelProps) {
  const queryClient = useQueryClient();

  // Form state
  const [remoteUrl, setRemoteUrl] = useState('');
  const [provider, setProvider] = useState<GitProvider>('github');
  const [syncStrategy, setSyncStrategy] = useState<SyncStrategy>('push_only');
  const [defaultBranch, setDefaultBranch] = useState('main');
  const [syncEnabled, setSyncEnabled] = useState(false);

  // Credential form state
  const [credentialType, setCredentialType] = useState<CredentialType>('https_token');
  const [credentialValue, setCredentialValue] = useState('');
  const [credentialLabel, setCredentialLabel] = useState('');
  const [showCredentialForm, setShowCredentialForm] = useState(false);

  // Fetch current config
  const { data: config, isLoading } = useQuery({
    queryKey: ['git-remote-config', organizationId],
    queryFn: () => gitApi.getRemoteConfig(organizationId),
  });

  // Update form when config loads
  useEffect(() => {
    if (config) {
      setRemoteUrl(config.remote_url || '');
      setProvider((config.provider as GitProvider) || 'github');
      setSyncStrategy((config.sync_strategy as SyncStrategy) || 'push_only');
      setDefaultBranch(config.default_branch || 'main');
      setSyncEnabled(config.sync_enabled);
    }
  }, [config]);

  // Mutations
  const configMutation = useMutation({
    mutationFn: (data: RemoteConfigCreate) => gitApi.configureRemote(organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['git-remote-config', organizationId] });
    },
  });

  const credentialMutation = useMutation({
    mutationFn: (data: { credential_type: CredentialType; value: string; label?: string }) =>
      gitApi.setCredential(organizationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['git-remote-config', organizationId] });
      setCredentialValue('');
      setCredentialLabel('');
      setShowCredentialForm(false);
    },
  });

  const testMutation = useMutation({
    mutationFn: () => gitApi.testConnection(organizationId),
  });

  const removeConfigMutation = useMutation({
    mutationFn: () => gitApi.removeRemoteConfig(organizationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['git-remote-config', organizationId] });
      setRemoteUrl('');
      setSyncEnabled(false);
    },
  });

  const handleSaveConfig = () => {
    if (!remoteUrl.trim()) {
      alert('Please enter a remote URL');
      return;
    }

    configMutation.mutate({
      remote_url: remoteUrl.trim(),
      provider,
      sync_strategy: syncStrategy,
      default_branch: defaultBranch,
      sync_enabled: syncEnabled,
    });
  };

  const handleSaveCredential = () => {
    if (!credentialValue.trim()) {
      alert('Please enter a credential value');
      return;
    }

    credentialMutation.mutate({
      credential_type: credentialType,
      value: credentialValue,
      label: credentialLabel || undefined,
    });
  };

  if (isLoading) {
    return <div className="p-4 text-gray-500">Loading configuration...</div>;
  }

  const selectedProvider = PROVIDERS.find((p) => p.value === provider);

  return (
    <div className="space-y-6">
      {/* Remote URL Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Remote Repository</h3>

        <div className="space-y-4">
          {/* Provider Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Git Provider
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as GitProvider)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            >
              {PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          {/* Remote URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Remote URL
            </label>
            <input
              type="text"
              value={remoteUrl}
              onChange={(e) => setRemoteUrl(e.target.value)}
              placeholder={selectedProvider?.urlHint}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            />
            <p className="mt-1 text-xs text-gray-500">
              Example: {selectedProvider?.urlHint}
            </p>
          </div>

          {/* Default Branch */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Default Branch
            </label>
            <input
              type="text"
              value={defaultBranch}
              onChange={(e) => setDefaultBranch(e.target.value)}
              placeholder="main"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
            />
          </div>

          {/* Sync Strategy */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sync Strategy
            </label>
            <div className="space-y-2">
              {SYNC_STRATEGIES.map((strategy) => (
                <label
                  key={strategy.value}
                  className={`flex items-start p-3 border rounded-md cursor-pointer ${
                    syncStrategy === strategy.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="radio"
                    name="syncStrategy"
                    value={strategy.value}
                    checked={syncStrategy === strategy.value}
                    onChange={(e) => setSyncStrategy(e.target.value as SyncStrategy)}
                    className="mt-0.5 mr-3"
                  />
                  <div>
                    <div className="font-medium text-gray-900">{strategy.label}</div>
                    <div className="text-sm text-gray-500">{strategy.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Enable Sync */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="syncEnabled"
              checked={syncEnabled}
              onChange={(e) => setSyncEnabled(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <label htmlFor="syncEnabled" className="ml-2 text-sm text-gray-700">
              Enable automatic sync
            </label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              onClick={handleSaveConfig}
              disabled={configMutation.isPending}
              className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
            >
              {configMutation.isPending ? 'Saving...' : 'Save Configuration'}
            </button>
            {config?.remote_url && (
              <>
                <button
                  onClick={() => testMutation.mutate()}
                  disabled={testMutation.isPending || !config.has_credentials}
                  className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md disabled:opacity-50"
                >
                  {testMutation.isPending ? 'Testing...' : 'Test Connection'}
                </button>
                <button
                  onClick={() => {
                    if (confirm('Remove remote configuration? This will also delete credentials.')) {
                      removeConfigMutation.mutate();
                    }
                  }}
                  className="px-4 py-2 text-sm text-red-600 bg-red-50 hover:bg-red-100 rounded-md"
                >
                  Remove Remote
                </button>
              </>
            )}
          </div>

          {/* Test Result */}
          {testMutation.data && (
            <div
              className={`p-3 rounded-md ${
                testMutation.data.success
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'
              }`}
            >
              {testMutation.data.message}
            </div>
          )}

          {/* Errors */}
          {configMutation.isError && (
            <div className="p-3 bg-red-50 text-red-700 rounded-md">
              {(configMutation.error as Error).message}
            </div>
          )}
        </div>
      </div>

      {/* Credentials Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Credentials</h3>
          {config?.has_credentials ? (
            <span className="px-2 py-1 text-xs text-green-700 bg-green-100 rounded-full">
              Configured
            </span>
          ) : (
            <span className="px-2 py-1 text-xs text-yellow-700 bg-yellow-100 rounded-full">
              Not configured
            </span>
          )}
        </div>

        {config?.has_credentials && !showCredentialForm ? (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Credentials are stored encrypted. You can update them by adding new credentials.
            </p>
            <button
              onClick={() => setShowCredentialForm(true)}
              className="px-4 py-2 text-sm text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-md"
            >
              Update Credentials
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Credential Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Credential Type
              </label>
              <select
                value={credentialType}
                onChange={(e) => setCredentialType(e.target.value as CredentialType)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              >
                {CREDENTIAL_TYPES.map((ct) => (
                  <option key={ct.value} value={ct.value}>
                    {ct.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Credential Value */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {credentialType === 'https_token' ? 'Access Token' : 'SSH Key'}
              </label>
              <textarea
                value={credentialValue}
                onChange={(e) => setCredentialValue(e.target.value)}
                placeholder={
                  credentialType === 'https_token'
                    ? 'ghp_xxxxxxxxxxxxxxxxxxxx'
                    : 'ssh-ed25519 AAAA...'
                }
                rows={credentialType === 'https_token' ? 1 : 4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm bg-white text-gray-900"
              />
              <p className="mt-1 text-xs text-gray-500">
                {credentialType === 'https_token'
                  ? 'Create a personal access token with repo permissions.'
                  : 'Paste your SSH public key here.'}
              </p>
            </div>

            {/* Label */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Label (optional)
              </label>
              <input
                type="text"
                value={credentialLabel}
                onChange={(e) => setCredentialLabel(e.target.value)}
                placeholder="e.g., GitHub Deploy Key"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={handleSaveCredential}
                disabled={credentialMutation.isPending || !credentialValue.trim()}
                className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
              >
                {credentialMutation.isPending ? 'Saving...' : 'Save Credential'}
              </button>
              {showCredentialForm && (
                <button
                  onClick={() => {
                    setShowCredentialForm(false);
                    setCredentialValue('');
                  }}
                  className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  Cancel
                </button>
              )}
            </div>

            {credentialMutation.isError && (
              <div className="p-3 bg-red-50 text-red-700 rounded-md">
                {(credentialMutation.error as Error).message}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default RemoteConfigPanel;
