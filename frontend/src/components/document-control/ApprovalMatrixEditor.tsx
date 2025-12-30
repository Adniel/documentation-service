/**
 * ApprovalMatrixEditor - Create and edit approval workflows.
 *
 * Features:
 * - Define approval steps with roles/users
 * - Set sequential vs parallel approval
 * - Configure document type applicability
 *
 * Sprint 9.5: Admin UI
 */

import { useState, useCallback, useEffect } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import {
  documentControlApi,
  organizationApi,
  type ApprovalStep,
  type ApprovalMatrix,
  type ApprovalMatrixCreate,
} from '../../lib/api';

interface ApprovalMatrixEditorProps {
  matrix?: ApprovalMatrix;
  organizationId?: string;
  onClose: () => void;
  onSaved?: () => void;
}

const DEFAULT_STEP: ApprovalStep = {
  step_order: 1,
  name: '',
  approver_role: '',
  approver_user_id: undefined,
  min_approvers: 1,
  allow_delegate: false,
};

const DOCUMENT_TYPES = [
  { value: 'sop', label: 'Standard Operating Procedure (SOP)' },
  { value: 'policy', label: 'Policy' },
  { value: 'work_instruction', label: 'Work Instruction' },
  { value: 'form', label: 'Form/Template' },
  { value: 'specification', label: 'Specification' },
  { value: 'manual', label: 'Manual' },
  { value: 'other', label: 'Other' },
];

const ROLES = [
  { value: 'owner', label: 'Document Owner' },
  { value: 'quality', label: 'Quality Assurance' },
  { value: 'manager', label: 'Department Manager' },
  { value: 'admin', label: 'Administrator' },
  { value: 'specific_user', label: 'Specific User' },
];

export function ApprovalMatrixEditor({
  matrix,
  organizationId: propOrganizationId,
  onClose,
  onSaved,
}: ApprovalMatrixEditorProps) {
  const queryClient = useQueryClient();
  const isEditing = !!matrix;

  // Form state
  const [name, setName] = useState(matrix?.name || '');
  const [description, setDescription] = useState(matrix?.description || '');
  const [requireSequential, setRequireSequential] = useState(matrix?.require_sequential ?? true);
  const [applicableTypes, setApplicableTypes] = useState<string[]>(
    matrix?.applicable_document_types || []
  );
  const [steps, setSteps] = useState<ApprovalStep[]>(
    matrix?.steps || [{ ...DEFAULT_STEP }]
  );
  const [selectedOrgId, setSelectedOrgId] = useState(propOrganizationId || '');

  // Fetch organizations
  const { data: organizations = [] } = useQuery({
    queryKey: ['organizations'],
    queryFn: organizationApi.list,
    enabled: !propOrganizationId,
  });

  // Set first organization as default if not provided
  useEffect(() => {
    if (!propOrganizationId && !selectedOrgId && organizations.length > 0) {
      setSelectedOrgId(organizations[0].id);
    }
  }, [propOrganizationId, selectedOrgId, organizations]);

  // Fetch users for user selection
  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: documentControlApi.listUsers,
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: ApprovalMatrixCreate) => documentControlApi.createApprovalMatrix(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approval-matrices'] });
      onSaved?.();
      onClose();
    },
  });

  // Step management
  const addStep = useCallback(() => {
    setSteps((prev) => [
      ...prev,
      { ...DEFAULT_STEP, step_order: prev.length + 1 },
    ]);
  }, []);

  const removeStep = useCallback((index: number) => {
    setSteps((prev) => {
      const newSteps = prev.filter((_, i) => i !== index);
      // Re-number steps
      return newSteps.map((step, i) => ({ ...step, step_order: i + 1 }));
    });
  }, []);

  const updateStep = useCallback((index: number, updates: Partial<ApprovalStep>) => {
    setSteps((prev) =>
      prev.map((step, i) => (i === index ? { ...step, ...updates } : step))
    );
  }, []);

  const moveStep = useCallback((index: number, direction: 'up' | 'down') => {
    setSteps((prev) => {
      const newSteps = [...prev];
      const targetIndex = direction === 'up' ? index - 1 : index + 1;
      if (targetIndex < 0 || targetIndex >= newSteps.length) return prev;

      // Swap
      [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]];

      // Re-number
      return newSteps.map((step, i) => ({ ...step, step_order: i + 1 }));
    });
  }, []);

  // Document type toggle
  const toggleDocType = useCallback((type: string) => {
    setApplicableTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      alert('Please enter a name for the approval matrix');
      return;
    }

    if (!selectedOrgId) {
      alert('Please select an organization');
      return;
    }

    if (steps.length === 0) {
      alert('Please add at least one approval step');
      return;
    }

    // Validate steps
    for (const step of steps) {
      if (!step.name.trim()) {
        alert('All steps must have a name');
        return;
      }
      if (!step.approver_role && !step.approver_user_id) {
        alert('All steps must have an approver role or specific user');
        return;
      }
    }

    const data: ApprovalMatrixCreate = {
      name: name.trim(),
      description: description.trim() || undefined,
      organization_id: selectedOrgId,
      applicable_document_types: applicableTypes,
      steps,
      require_sequential: requireSequential,
    };

    createMutation.mutate(data);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Dialog */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-lg font-semibold text-gray-900">
            {isEditing ? 'Edit Approval Matrix' : 'Create Approval Matrix'}
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Define the approval workflow for document changes
          </p>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Standard SOP Approval"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe when this approval matrix should be used..."
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
              />
            </div>
          </div>

          {/* Document Types */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Applicable Document Types
            </label>
            <div className="flex flex-wrap gap-2">
              {DOCUMENT_TYPES.map((type) => (
                <label
                  key={type.value}
                  className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm cursor-pointer transition ${
                    applicableTypes.includes(type.value)
                      ? 'bg-blue-100 text-blue-700 border border-blue-300'
                      : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={applicableTypes.includes(type.value)}
                    onChange={() => toggleDocType(type.value)}
                    className="sr-only"
                  />
                  {type.label}
                </label>
              ))}
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Leave empty to apply to all document types
            </p>
          </div>

          {/* Approval Order */}
          <div>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={requireSequential}
                onChange={(e) => setRequireSequential(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <span className="text-sm text-gray-700">
                Require sequential approval (steps must be completed in order)
              </span>
            </label>
          </div>

          {/* Approval Steps */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium text-gray-700">
                Approval Steps *
              </label>
              <button
                type="button"
                onClick={addStep}
                className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-md transition"
              >
                + Add Step
              </button>
            </div>

            <div className="space-y-3">
              {steps.map((step, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium text-gray-700">
                      Step {step.step_order}
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => moveStep(index, 'up')}
                        disabled={index === 0}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                        title="Move up"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                        </svg>
                      </button>
                      <button
                        type="button"
                        onClick={() => moveStep(index, 'down')}
                        disabled={index === steps.length - 1}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                        title="Move down"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      {steps.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeStep(index)}
                          className="p-1 text-red-400 hover:text-red-600"
                          title="Remove step"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Step Name *</label>
                      <input
                        type="text"
                        value={step.name}
                        onChange={(e) => updateStep(index, { name: e.target.value })}
                        placeholder="e.g., Manager Review"
                        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white text-gray-900"
                      />
                    </div>

                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Approver Role *</label>
                      <select
                        value={step.approver_role || ''}
                        onChange={(e) => updateStep(index, {
                          approver_role: e.target.value || undefined,
                          approver_user_id: e.target.value === 'specific_user' ? step.approver_user_id : undefined,
                        })}
                        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white text-gray-900"
                      >
                        <option value="">Select role...</option>
                        {ROLES.map((role) => (
                          <option key={role.value} value={role.value}>
                            {role.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    {step.approver_role === 'specific_user' && (
                      <div className="col-span-2">
                        <label className="block text-xs text-gray-600 mb-1">Select User</label>
                        <select
                          value={step.approver_user_id || ''}
                          onChange={(e) => updateStep(index, { approver_user_id: e.target.value || undefined })}
                          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white text-gray-900"
                        >
                          <option value="">Select user...</option>
                          {users.map((user) => (
                            <option key={user.id} value={user.id}>
                              {user.full_name} ({user.email})
                            </option>
                          ))}
                        </select>
                      </div>
                    )}

                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Min Approvers</label>
                      <input
                        type="number"
                        min={1}
                        max={10}
                        value={step.min_approvers || 1}
                        onChange={(e) => updateStep(index, { min_approvers: parseInt(e.target.value) || 1 })}
                        className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white text-gray-900"
                      />
                    </div>

                    <div className="flex items-end">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={step.allow_delegate || false}
                          onChange={(e) => updateStep(index, { allow_delegate: e.target.checked })}
                          className="w-4 h-4 text-blue-600 rounded"
                        />
                        <span className="text-sm text-gray-700">Allow delegation</span>
                      </label>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Error */}
          {createMutation.isError && (
            <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md">
              {(createMutation.error as Error).message}
            </div>
          )}
        </form>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3 flex-shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={createMutation.isPending}
            className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md transition disabled:opacity-50"
          >
            {createMutation.isPending ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Matrix'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ApprovalMatrixEditor;
