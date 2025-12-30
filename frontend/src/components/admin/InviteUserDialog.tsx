/**
 * InviteUserDialog - Dialog to invite a user to an organization.
 *
 * Sprint B: Admin UI Completion
 */

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { organizationApi } from '../../lib/api';
import type { MemberRole } from '../../types';

interface InviteUserDialogProps {
  organizationId: string;
  onClose: () => void;
}

const ROLES: { value: MemberRole; label: string; description: string }[] = [
  { value: 'viewer', label: 'Viewer', description: 'Can view content only' },
  { value: 'reviewer', label: 'Reviewer', description: 'Can view and comment on content' },
  { value: 'editor', label: 'Editor', description: 'Can create and edit content' },
  { value: 'admin', label: 'Admin', description: 'Can manage members and settings' },
];

export function InviteUserDialog({ organizationId, onClose }: InviteUserDialogProps) {
  const queryClient = useQueryClient();
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<MemberRole>('viewer');
  const [error, setError] = useState<string | null>(null);

  const inviteMutation = useMutation({
    mutationFn: () => organizationApi.addMember(organizationId, { email, role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organization-members', organizationId] });
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to invite user');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email.trim()) {
      setError('Email is required');
      return;
    }
    inviteMutation.mutate();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div className="fixed inset-0 bg-black bg-opacity-30" onClick={onClose} />

        {/* Dialog */}
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Invite Member</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@example.com"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                autoFocus
              />
              <p className="mt-1 text-xs text-gray-500">
                The user must already have an account in the system.
              </p>
            </div>

            {/* Role Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role
              </label>
              <div className="space-y-2">
                {ROLES.map((r) => (
                  <label
                    key={r.value}
                    className={`flex items-start p-3 border rounded-lg cursor-pointer transition ${
                      role === r.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value={r.value}
                      checked={role === r.value}
                      onChange={(e) => setRole(e.target.value as MemberRole)}
                      className="mt-0.5 h-4 w-4 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="ml-3">
                      <div className="text-sm font-medium text-gray-900">{r.label}</div>
                      <div className="text-xs text-gray-500">{r.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={inviteMutation.isPending}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {inviteMutation.isPending ? 'Inviting...' : 'Invite Member'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
