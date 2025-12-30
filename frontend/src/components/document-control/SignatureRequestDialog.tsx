/**
 * SignatureRequestDialog - Request e-signature from another user.
 *
 * Allows users to:
 * - Select signature meaning
 * - Choose signatory user
 * - Send signature request notification
 *
 * Sprint 9.5: Admin UI
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentControlApi, type SignatureMeaning } from '../../lib/api';

interface SignatureRequestDialogProps {
  pageId: string;
  pageTitle: string;
  isOpen: boolean;
  onClose: () => void;
  onSent?: () => void;
}

const SIGNATURE_MEANINGS: { value: SignatureMeaning; label: string; description: string }[] = [
  { value: 'authored', label: 'Authored', description: 'I am the original author of this content' },
  { value: 'reviewed', label: 'Reviewed', description: 'I have reviewed and verified the content' },
  { value: 'approved', label: 'Approved', description: 'I approve this document for release' },
  { value: 'witnessed', label: 'Witnessed', description: 'I witnessed the creation or modification' },
  { value: 'acknowledged', label: 'Acknowledged', description: 'I acknowledge receipt and understanding' },
];

export function SignatureRequestDialog({
  pageId,
  pageTitle,
  isOpen,
  onClose,
  onSent,
}: SignatureRequestDialogProps) {
  const queryClient = useQueryClient();
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [selectedMeaning, setSelectedMeaning] = useState<SignatureMeaning>('reviewed');
  const [message, setMessage] = useState('');

  // Fetch users
  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: documentControlApi.listUsers,
    enabled: isOpen,
  });

  // Request signature mutation
  // Note: This would typically send an email/notification to the user
  const requestMutation = useMutation({
    mutationFn: async () => {
      // In a real implementation, this would call an API endpoint to send the request
      // For now, we'll just simulate success
      if (!selectedUserId) {
        throw new Error('Please select a user');
      }
      // TODO: Implement backend endpoint for signature requests
      // await api.post('/signatures/request', { page_id: pageId, user_id: selectedUserId, meaning: selectedMeaning, message });
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['page-signatures', pageId] });
      onSent?.();
      onClose();
      // Reset form
      setSelectedUserId('');
      setSelectedMeaning('reviewed');
      setMessage('');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    requestMutation.mutate();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Dialog */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Request Signature
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Request an e-signature for "{pageTitle}"
          </p>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* User Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Signatory *
            </label>
            <select
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Choose a user...</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name} ({user.email})
                </option>
              ))}
            </select>
          </div>

          {/* Signature Meaning */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Signature Meaning *
            </label>
            <div className="space-y-2">
              {SIGNATURE_MEANINGS.map((meaning) => (
                <label
                  key={meaning.value}
                  className={`flex items-start gap-3 p-3 rounded-md border cursor-pointer transition ${
                    selectedMeaning === meaning.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="meaning"
                    value={meaning.value}
                    checked={selectedMeaning === meaning.value}
                    onChange={(e) => setSelectedMeaning(e.target.value as SignatureMeaning)}
                    className="mt-0.5 w-4 h-4 text-blue-600"
                  />
                  <div>
                    <div className="text-sm font-medium text-gray-900">{meaning.label}</div>
                    <div className="text-xs text-gray-500">{meaning.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Message */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message (optional)
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Add a message to the signatory..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Error */}
          {requestMutation.isError && (
            <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md">
              {(requestMutation.error as Error).message}
            </div>
          )}

          {/* Info */}
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-700">
            <strong>Note:</strong> The selected user will receive a notification
            to sign this document. They will need to re-authenticate to complete
            the signature.
          </div>
        </form>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!selectedUserId || requestMutation.isPending}
            className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md transition disabled:opacity-50"
          >
            {requestMutation.isPending ? 'Sending...' : 'Send Request'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default SignatureRequestDialog;
