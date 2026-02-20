/**
 * Visitor Management Component
 *
 * Sprint D: Integrated Access Control
 *
 * Manages external visitors for published sites:
 * - Invite visitors by email
 * - Set clearance levels and page access
 * - View and revoke visitor access
 */

import React, { useState, useEffect } from 'react';
import {
  Users,
  Mail,
  Shield,
  Clock,
  Trash2,
  Send,
  RefreshCw,
  UserPlus,
  AlertCircle,
  CheckCircle,
  Copy,
  X,
} from 'lucide-react';

interface Visitor {
  id: string;
  email: string;
  display_name: string;
  is_internal: boolean;
  last_login_at: string | null;
  created_at: string;
}

interface VisitorRole {
  visitor_id: string;
  site_id: string;
  clearance_level: number;
  allowed_page_ids: string[];
  expires_at: string | null;
  is_active: boolean;
  created_at: string;
}

interface VisitorWithRole {
  visitor: Visitor;
  role: VisitorRole;
}

interface InviteResult {
  visitor: Visitor;
  magic_link_url: string;
  expires_at: string;
}

interface VisitorManagementProps {
  siteId: string;
  onClose?: () => void;
}

const CLEARANCE_LEVELS = [
  { value: 0, label: 'Public', description: 'Can view public documents only' },
  { value: 1, label: 'Internal', description: 'Can view internal and public documents' },
  { value: 2, label: 'Confidential', description: 'Can view confidential, internal, and public' },
  { value: 3, label: 'Restricted', description: 'Full access to all documents' },
];

export function VisitorManagement({ siteId, onClose }: VisitorManagementProps) {
  const [visitors, setVisitors] = useState<VisitorWithRole[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteResult, setInviteResult] = useState<InviteResult | null>(null);

  // Invite form state
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteDisplayName, setInviteDisplayName] = useState('');
  const [inviteClearance, setInviteClearance] = useState(0);
  const [inviteExpiry, setInviteExpiry] = useState('');
  const [inviting, setInviting] = useState(false);

  useEffect(() => {
    loadVisitors();
  }, [siteId]);

  async function loadVisitors() {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/visitors/sites/${siteId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to load visitors');

      const data = await response.json();
      setVisitors(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load visitors');
    } finally {
      setLoading(false);
    }
  }

  async function inviteVisitor(e: React.FormEvent) {
    e.preventDefault();
    setInviting(true);

    try {
      const response = await fetch(`/api/v1/visitors/sites/${siteId}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          email: inviteEmail,
          display_name: inviteDisplayName || undefined,
          clearance_level: inviteClearance,
          expires_at: inviteExpiry || undefined,
        }),
      });

      if (!response.ok) throw new Error('Failed to invite visitor');

      const result: InviteResult = await response.json();
      setInviteResult(result);
      setShowInviteForm(false);
      setInviteEmail('');
      setInviteDisplayName('');
      setInviteClearance(0);
      setInviteExpiry('');
      loadVisitors();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to invite visitor');
    } finally {
      setInviting(false);
    }
  }

  async function revokeAccess(visitorId: string) {
    if (!confirm('Are you sure you want to revoke this visitor\'s access?')) {
      return;
    }

    try {
      const response = await fetch(
        `/api/v1/visitors/sites/${siteId}/visitors/${visitorId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) throw new Error('Failed to revoke access');

      loadVisitors();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to revoke access');
    }
  }

  async function resendInvite(visitorId: string) {
    try {
      const response = await fetch(
        `/api/v1/visitors/sites/${siteId}/visitors/${visitorId}/resend-invite`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (!response.ok) throw new Error('Failed to resend invite');

      const result: InviteResult = await response.json();
      setInviteResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resend invite');
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
  }

  function formatDate(dateStr: string | null): string {
    if (!dateStr) return 'Never';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function getClearanceLabel(level: number): string {
    return CLEARANCE_LEVELS.find(c => c.value === level)?.label || `Level ${level}`;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-5 h-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-900">Visitor Management</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowInviteForm(true)}
            className="px-3 py-1.5 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 flex items-center gap-1.5"
          >
            <UserPlus className="w-4 h-4" />
            Invite Visitor
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-center gap-2 text-red-700">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Invite result modal */}
      {inviteResult && (
        <div className="mx-6 mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="font-medium text-green-800">Invitation Created</span>
          </div>
          <p className="text-sm text-green-700 mb-3">
            Send this link to {inviteResult.visitor.email}:
          </p>
          <div className="flex items-center gap-2">
            <input
              type="text"
              readOnly
              value={inviteResult.magic_link_url}
              className="flex-1 px-3 py-2 bg-white border border-green-300 rounded text-sm font-mono"
            />
            <button
              onClick={() => copyToClipboard(inviteResult.magic_link_url)}
              className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-green-600 mt-2">
            Expires: {formatDate(inviteResult.expires_at)}
          </p>
          <button
            onClick={() => setInviteResult(null)}
            className="mt-3 text-sm text-green-700 hover:text-green-900"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
          </div>
        ) : visitors.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No visitors yet</p>
            <p className="text-sm text-gray-400">
              Invite visitors to give them access to this site
            </p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-500 border-b border-gray-200">
                <th className="pb-3 font-medium">Visitor</th>
                <th className="pb-3 font-medium">Clearance</th>
                <th className="pb-3 font-medium">Last Login</th>
                <th className="pb-3 font-medium">Expires</th>
                <th className="pb-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {visitors.map(({ visitor, role }) => (
                <tr key={visitor.id} className="text-sm">
                  <td className="py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                        <Mail className="w-4 h-4 text-gray-400" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {visitor.display_name}
                        </p>
                        <p className="text-gray-500">{visitor.email}</p>
                      </div>
                      {visitor.is_internal && (
                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                          Internal
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3">
                    <div className="flex items-center gap-1.5">
                      <Shield className="w-4 h-4 text-gray-400" />
                      <span>{getClearanceLabel(role.clearance_level)}</span>
                    </div>
                  </td>
                  <td className="py-3 text-gray-500">
                    {formatDate(visitor.last_login_at)}
                  </td>
                  <td className="py-3">
                    {role.expires_at ? (
                      <div className="flex items-center gap-1.5 text-gray-500">
                        <Clock className="w-4 h-4" />
                        {formatDate(role.expires_at)}
                      </div>
                    ) : (
                      <span className="text-gray-400">Never</span>
                    )}
                  </td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => resendInvite(visitor.id)}
                        className="p-1.5 text-gray-400 hover:text-blue-600 rounded"
                        title="Resend invite"
                      >
                        <Send className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => revokeAccess(visitor.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 rounded"
                        title="Revoke access"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Invite Form Modal */}
      {showInviteForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold mb-4">Invite Visitor</h3>

            <form onSubmit={inviteVisitor} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address *
                </label>
                <input
                  type="email"
                  required
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="visitor@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Display Name
                </label>
                <input
                  type="text"
                  value={inviteDisplayName}
                  onChange={(e) => setInviteDisplayName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Optional display name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Clearance Level
                </label>
                <select
                  value={inviteClearance}
                  onChange={(e) => setInviteClearance(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  {CLEARANCE_LEVELS.map((level) => (
                    <option key={level.value} value={level.value}>
                      {level.label} - {level.description}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Access Expiry
                </label>
                <input
                  type="datetime-local"
                  value={inviteExpiry}
                  onChange={(e) => setInviteExpiry(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Leave empty for no expiration
                </p>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowInviteForm(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={inviting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {inviting ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <UserPlus className="w-4 h-4" />
                  )}
                  Send Invitation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default VisitorManagement;
