/**
 * DocumentMetadataEditor - Edit document control metadata.
 *
 * Allows editing:
 * - Owner and Custodian
 * - Review schedule
 * - Training requirements
 * - Retention policy
 *
 * Sprint 9.5: Admin UI
 */

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  documentControlApi,
  type DocumentMetadataUpdate,
} from '../../lib/api';

interface DocumentMetadataEditorProps {
  pageId: string;
  onClose?: () => void;
  onSaved?: () => void;
}

export function DocumentMetadataEditor({
  pageId,
  onClose,
  onSaved,
}: DocumentMetadataEditorProps) {
  const queryClient = useQueryClient();

  // Fetch current metadata
  const {
    data: metadataResponse,
    isLoading: loadingMetadata,
    error: metadataError,
  } = useQuery({
    queryKey: ['document-metadata', pageId],
    queryFn: () => documentControlApi.getMetadata(pageId),
  });

  // Fetch users for owner/custodian dropdowns
  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: documentControlApi.listUsers,
  });

  // Fetch retention policies
  const { data: retentionPolicies = [] } = useQuery({
    queryKey: ['retention-policies'],
    queryFn: () => documentControlApi.listRetentionPolicies(),
  });

  const metadata = metadataResponse?.metadata;

  // Form state
  const [formData, setFormData] = useState<DocumentMetadataUpdate>({
    owner_id: undefined,
    custodian_id: undefined,
    review_cycle_months: undefined,
    next_review_date: undefined,
    requires_training: undefined,
    training_validity_months: undefined,
    retention_policy_id: undefined,
  });

  // Initialize form when metadata loads
  useEffect(() => {
    if (metadata) {
      setFormData({
        owner_id: metadata.owner_id || undefined,
        custodian_id: metadata.custodian_id || undefined,
        review_cycle_months: metadata.review_cycle_months || undefined,
        next_review_date: metadata.next_review_date?.split('T')[0] || undefined,
        requires_training: metadata.requires_training,
        training_validity_months: metadata.training_validity_months || undefined,
        retention_policy_id: metadata.retention_policy_id || undefined,
      });
    }
  }, [metadata]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: DocumentMetadataUpdate) =>
      documentControlApi.updateMetadata(pageId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document-metadata', pageId] });
      queryClient.invalidateQueries({ queryKey: ['page', pageId] });
      onSaved?.();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Only send fields that have values
    const updateData: DocumentMetadataUpdate = {};
    if (formData.owner_id) updateData.owner_id = formData.owner_id;
    if (formData.custodian_id) updateData.custodian_id = formData.custodian_id;
    if (formData.review_cycle_months) updateData.review_cycle_months = formData.review_cycle_months;
    if (formData.next_review_date) updateData.next_review_date = formData.next_review_date;
    if (formData.requires_training !== undefined) updateData.requires_training = formData.requires_training;
    if (formData.training_validity_months) updateData.training_validity_months = formData.training_validity_months;
    if (formData.retention_policy_id) updateData.retention_policy_id = formData.retention_policy_id;

    updateMutation.mutate(updateData);
  };

  if (loadingMetadata) {
    return (
      <div className="p-6 text-center text-gray-500">
        <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2" />
        Loading metadata...
      </div>
    );
  }

  if (metadataError) {
    return (
      <div className="p-6 text-center text-red-500">
        Error loading metadata: {(metadataError as Error).message}
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Document Info (read-only) */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Document Information</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Document Number:</span>
            <span className="ml-2 font-mono">{metadata?.document_number || 'Not assigned'}</span>
          </div>
          <div>
            <span className="text-gray-500">Version:</span>
            <span className="ml-2">{metadata?.version || '1.0'}</span>
          </div>
          <div>
            <span className="text-gray-500">Status:</span>
            <span className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${
              metadata?.status === 'effective' ? 'bg-green-100 text-green-700' :
              metadata?.status === 'approved' ? 'bg-blue-100 text-blue-700' :
              metadata?.status === 'in_review' ? 'bg-yellow-100 text-yellow-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {metadata?.status || 'draft'}
            </span>
          </div>
          {metadata?.effective_date && (
            <div>
              <span className="text-gray-500">Effective Date:</span>
              <span className="ml-2">{new Date(metadata.effective_date).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      </div>

      {/* Ownership */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Ownership</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Owner</label>
            <select
              value={formData.owner_id || ''}
              onChange={(e) => setFormData({ ...formData, owner_id: e.target.value || undefined })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select owner...</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name} ({user.email})
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Person responsible for document content and accuracy
            </p>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Custodian</label>
            <select
              value={formData.custodian_id || ''}
              onChange={(e) => setFormData({ ...formData, custodian_id: e.target.value || undefined })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select custodian...</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name} ({user.email})
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Person responsible for document distribution and control
            </p>
          </div>
        </div>
      </div>

      {/* Review Schedule */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Review Schedule</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Review Cycle (months)</label>
            <input
              type="number"
              min={1}
              max={120}
              value={formData.review_cycle_months || ''}
              onChange={(e) => setFormData({
                ...formData,
                review_cycle_months: e.target.value ? parseInt(e.target.value) : undefined,
              })}
              placeholder="e.g., 12"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500">
              How often this document should be reviewed
            </p>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Next Review Date</label>
            <input
              type="date"
              value={formData.next_review_date || ''}
              onChange={(e) => setFormData({
                ...formData,
                next_review_date: e.target.value || undefined,
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500">
              Override next review date (auto-calculated from cycle if empty)
            </p>
          </div>
        </div>
      </div>

      {/* Training Requirements */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Training Requirements</h3>
        <div className="space-y-4">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={formData.requires_training || false}
              onChange={(e) => setFormData({
                ...formData,
                requires_training: e.target.checked,
                training_validity_months: e.target.checked ? (formData.training_validity_months || 12) : undefined,
              })}
              className="w-4 h-4 text-blue-600 rounded"
            />
            <span className="text-sm text-gray-700">Requires training acknowledgment</span>
          </label>

          {formData.requires_training && (
            <div className="ml-7">
              <label className="block text-sm text-gray-600 mb-1">Training Validity (months)</label>
              <input
                type="number"
                min={1}
                max={120}
                value={formData.training_validity_months || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  training_validity_months: e.target.value ? parseInt(e.target.value) : undefined,
                })}
                placeholder="e.g., 12"
                className="w-48 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                How long training acknowledgment remains valid
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Retention Policy */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-3">Retention Policy</h3>
        <select
          value={formData.retention_policy_id || ''}
          onChange={(e) => setFormData({
            ...formData,
            retention_policy_id: e.target.value || undefined,
          })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">No retention policy</option>
          {retentionPolicies.map((policy) => (
            <option key={policy.id} value={policy.id}>
              {policy.name} ({policy.retention_years} years - {policy.disposition_method})
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">
          Defines how long to keep the document and how to dispose of it
        </p>
        {metadata?.disposition_date && (
          <p className="mt-2 text-sm text-amber-600">
            Scheduled for disposition: {new Date(metadata.disposition_date).toLocaleDateString()}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={updateMutation.isPending}
          className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md transition disabled:opacity-50"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {updateMutation.isError && (
        <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md">
          Error: {(updateMutation.error as Error).message}
        </div>
      )}

      {updateMutation.isSuccess && (
        <div className="p-3 bg-green-50 text-green-700 text-sm rounded-md">
          Metadata updated successfully
        </div>
      )}
    </form>
  );
}

export default DocumentMetadataEditor;
