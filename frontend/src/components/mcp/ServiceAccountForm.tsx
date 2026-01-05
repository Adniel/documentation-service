/**
 * Service Account Form Component
 *
 * Sprint C: MCP Integration
 *
 * Form for creating and editing service accounts.
 */

import { useState } from 'react';
import {
  serviceAccountApi,
  type ServiceAccount,
  type ServiceAccountCreate,
  type ServiceAccountUpdate,
  type ServiceAccountRole,
} from '../../lib/api';

// Available MCP operations
const MCP_OPERATIONS = [
  { id: 'search_documents', name: 'Search Documents', description: 'Search for documents' },
  { id: 'get_document', name: 'Get Document', description: 'Get document with content' },
  { id: 'get_document_content', name: 'Get Document Content', description: 'Get markdown content' },
  { id: 'list_spaces', name: 'List Spaces', description: 'List accessible spaces' },
  { id: 'get_document_metadata', name: 'Get Metadata', description: 'Get document metadata' },
  { id: 'get_document_history', name: 'Get History', description: 'Get version history' },
];

interface ServiceAccountFormProps {
  account?: ServiceAccount;
  onSuccess?: (account: ServiceAccount, apiKey?: string) => void;
  onCancel?: () => void;
}

export function ServiceAccountForm({ account, onSuccess, onCancel }: ServiceAccountFormProps) {
  const isEditing = !!account;

  const [formData, setFormData] = useState<ServiceAccountCreate & ServiceAccountUpdate>({
    name: account?.name || '',
    description: account?.description || '',
    role: account?.role || 'reader',
    allowed_spaces: account?.allowed_spaces || [],
    allowed_operations: account?.allowed_operations || [],
    ip_allowlist: account?.ip_allowlist || [],
    rate_limit_per_minute: account?.rate_limit_per_minute || 60,
    expires_at: account?.expires_at ? account.expires_at.split('T')[0] : '',
    is_active: account?.is_active ?? true,
  });

  const [ipInput, setIpInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      setError('Name is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const submitData = {
        ...formData,
        expires_at: formData.expires_at
          ? new Date(formData.expires_at).toISOString()
          : undefined,
        allowed_spaces:
          formData.allowed_spaces && formData.allowed_spaces.length > 0
            ? formData.allowed_spaces
            : undefined,
        allowed_operations:
          formData.allowed_operations && formData.allowed_operations.length > 0
            ? formData.allowed_operations
            : undefined,
        ip_allowlist:
          formData.ip_allowlist && formData.ip_allowlist.length > 0
            ? formData.ip_allowlist
            : undefined,
      };

      if (isEditing && account) {
        const updated = await serviceAccountApi.update(account.id, submitData);
        onSuccess?.(updated);
      } else {
        const created = await serviceAccountApi.create(submitData as ServiceAccountCreate);
        setNewApiKey(created.api_key);
        onSuccess?.(created, created.api_key);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save service account');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = (role: ServiceAccountRole) => {
    setFormData({ ...formData, role });
  };

  const handleOperationToggle = (operationId: string) => {
    const current = formData.allowed_operations || [];
    const updated = current.includes(operationId)
      ? current.filter((op) => op !== operationId)
      : [...current, operationId];
    setFormData({ ...formData, allowed_operations: updated });
  };

  const handleAddIp = () => {
    if (!ipInput.trim()) return;
    const current = formData.ip_allowlist || [];
    if (!current.includes(ipInput.trim())) {
      setFormData({ ...formData, ip_allowlist: [...current, ipInput.trim()] });
    }
    setIpInput('');
  };

  const handleRemoveIp = (ip: string) => {
    const current = formData.ip_allowlist || [];
    setFormData({ ...formData, ip_allowlist: current.filter((i) => i !== ip) });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  // Show API key after creation
  if (newApiKey) {
    return (
      <div className="max-w-lg mx-auto p-6 bg-white rounded-lg shadow">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <svg
              className="h-6 w-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            Service Account Created
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            Copy your API key now. It will not be shown again.
          </p>
        </div>

        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700">API Key</label>
          <div className="mt-1 flex rounded-md shadow-sm">
            <input
              type="text"
              readOnly
              value={newApiKey}
              className="flex-1 min-w-0 block w-full px-3 py-2 rounded-l-md border border-gray-300 bg-gray-50 font-mono text-sm"
            />
            <button
              onClick={() => copyToClipboard(newApiKey)}
              className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 hover:bg-gray-100"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </button>
          </div>
          <p className="mt-2 text-xs text-gray-500">
            Use this key in the Authorization header: <code>Bearer {newApiKey.slice(0, 10)}...</code>
          </p>
        </div>

        <div className="mt-6">
          <button
            onClick={() => onCancel?.()}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Done
          </button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          {isEditing ? 'Edit Service Account' : 'Create Service Account'}
        </h3>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {/* Basic Info */}
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Name *
            </label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="e.g., AI Documentation Assistant"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={2}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Optional description of this service account's purpose"
            />
          </div>

          {/* Role */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <div className="grid grid-cols-3 gap-4">
              {(['reader', 'contributor', 'admin'] as ServiceAccountRole[]).map((role) => (
                <button
                  key={role}
                  type="button"
                  onClick={() => handleRoleChange(role)}
                  className={`p-3 border rounded-lg text-center ${
                    formData.role === role
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="font-medium capitalize">{role}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {role === 'reader'
                      ? 'Read-only access'
                      : role === 'contributor'
                        ? 'Read & limited write'
                        : 'Full access'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Rate Limit */}
          <div>
            <label htmlFor="rate_limit" className="block text-sm font-medium text-gray-700">
              Rate Limit (requests/minute)
            </label>
            <input
              type="number"
              id="rate_limit"
              value={formData.rate_limit_per_minute}
              onChange={(e) =>
                setFormData({ ...formData, rate_limit_per_minute: parseInt(e.target.value) || 60 })
              }
              min={1}
              max={1000}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          {/* Expiration */}
          <div>
            <label htmlFor="expires_at" className="block text-sm font-medium text-gray-700">
              Expiration Date (optional)
            </label>
            <input
              type="date"
              id="expires_at"
              value={formData.expires_at?.split('T')[0] || ''}
              onChange={(e) => setFormData({ ...formData, expires_at: e.target.value })}
              min={new Date().toISOString().split('T')[0]}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Allowed Operations */}
      <div className="bg-white shadow rounded-lg p-6">
        <h4 className="text-md font-medium text-gray-900 mb-2">Allowed Operations</h4>
        <p className="text-sm text-gray-500 mb-4">
          Leave empty to allow all operations. Select specific operations to restrict access.
        </p>
        <div className="grid grid-cols-2 gap-3">
          {MCP_OPERATIONS.map((op) => (
            <label
              key={op.id}
              className={`flex items-start p-3 border rounded-lg cursor-pointer ${
                (formData.allowed_operations || []).includes(op.id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="checkbox"
                checked={(formData.allowed_operations || []).includes(op.id)}
                onChange={() => handleOperationToggle(op.id)}
                className="mt-0.5 h-4 w-4 rounded border-gray-300 text-blue-600"
              />
              <div className="ml-3">
                <span className="text-sm font-medium text-gray-900">{op.name}</span>
                <p className="text-xs text-gray-500">{op.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* IP Allowlist */}
      <div className="bg-white shadow rounded-lg p-6">
        <h4 className="text-md font-medium text-gray-900 mb-2">IP Allowlist</h4>
        <p className="text-sm text-gray-500 mb-4">
          Leave empty to allow access from any IP. Add IP addresses or CIDR ranges to restrict access.
        </p>
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={ipInput}
            onChange={(e) => setIpInput(e.target.value)}
            placeholder="e.g., 192.168.1.0/24"
            className="flex-1 rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddIp();
              }
            }}
          />
          <button
            type="button"
            onClick={handleAddIp}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            Add
          </button>
        </div>
        {(formData.ip_allowlist || []).length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.ip_allowlist?.map((ip) => (
              <span
                key={ip}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-sm bg-gray-100 text-gray-800"
              >
                {ip}
                <button
                  type="button"
                  onClick={() => handleRemoveIp(ip)}
                  className="ml-1.5 text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Status (editing only) */}
      {isEditing && (
        <div className="bg-white shadow rounded-lg p-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4 rounded border-gray-300 text-blue-600"
            />
            <span className="ml-3 text-sm font-medium text-gray-900">Active</span>
          </label>
          <p className="mt-1 text-sm text-gray-500 ml-7">
            Inactive service accounts cannot make API requests.
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Service Account'}
        </button>
      </div>
    </form>
  );
}
