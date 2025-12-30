/**
 * UserManagementPanel - Manage organization members.
 *
 * Sprint B: Admin UI Completion
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { organizationApi } from '../../lib/api';
import type { OrganizationMember, MemberRole } from '../../types';
import { InviteUserDialog } from './InviteUserDialog';

interface UserManagementPanelProps {
  organizationId: string;
}

const ROLE_LABELS: Record<MemberRole, string> = {
  viewer: 'Viewer',
  reviewer: 'Reviewer',
  editor: 'Editor',
  admin: 'Admin',
  owner: 'Owner',
};

const ROLE_COLORS: Record<MemberRole, string> = {
  viewer: 'bg-gray-100 text-gray-700',
  reviewer: 'bg-blue-100 text-blue-700',
  editor: 'bg-green-100 text-green-700',
  admin: 'bg-purple-100 text-purple-700',
  owner: 'bg-orange-100 text-orange-700',
};

export function UserManagementPanel({ organizationId }: UserManagementPanelProps) {
  const queryClient = useQueryClient();
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [editingMember, setEditingMember] = useState<OrganizationMember | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<MemberRole | 'all'>('all');

  // Fetch members
  const { data: memberData, isLoading, error } = useQuery({
    queryKey: ['organization-members', organizationId],
    queryFn: () => organizationApi.listMembers(organizationId),
  });

  // Update role mutation
  const updateRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: MemberRole }) =>
      organizationApi.updateMemberRole(organizationId, userId, { role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organization-members', organizationId] });
      setEditingMember(null);
    },
  });

  // Remove member mutation
  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) => organizationApi.removeMember(organizationId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organization-members', organizationId] });
    },
  });

  // Filter members
  const filteredMembers = (memberData?.members || []).filter((member) => {
    const matchesSearch =
      member.user_full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.user_email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === 'all' || member.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const handleRemoveMember = (member: OrganizationMember) => {
    if (confirm(`Are you sure you want to remove ${member.user_full_name} from this organization?`)) {
      removeMemberMutation.mutate(member.user_id);
    }
  };

  const handleRoleChange = (userId: string, newRole: MemberRole) => {
    updateRoleMutation.mutate({ userId, role: newRole });
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
        Failed to load members. Please try again.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Organization Members</h3>
          <p className="mt-1 text-sm text-gray-500">
            Manage who has access to this organization and their roles.
          </p>
        </div>
        <button
          onClick={() => setShowInviteDialog(true)}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition"
        >
          Invite Member
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search members..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value as MemberRole | 'all')}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        >
          <option value="all">All Roles</option>
          {(Object.keys(ROLE_LABELS) as MemberRole[]).map((role) => (
            <option key={role} value={role}>
              {ROLE_LABELS[role]}
            </option>
          ))}
        </select>
      </div>

      {/* Members List */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {filteredMembers.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            {searchQuery || roleFilter !== 'all'
              ? 'No members match your filters.'
              : 'No members yet. Invite someone to get started.'}
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Member
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredMembers.map((member) => (
                <tr key={member.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-10 w-10 flex-shrink-0">
                        {member.user_avatar_url ? (
                          <img
                            className="h-10 w-10 rounded-full"
                            src={member.user_avatar_url}
                            alt=""
                          />
                        ) : (
                          <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 font-medium">
                            {member.user_full_name.charAt(0).toUpperCase()}
                          </div>
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {member.user_full_name}
                        </div>
                        <div className="text-sm text-gray-500">{member.user_email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {editingMember?.user_id === member.user_id ? (
                      <select
                        value={member.role}
                        onChange={(e) => handleRoleChange(member.user_id, e.target.value as MemberRole)}
                        className="px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-sm"
                        disabled={member.role === 'owner'}
                      >
                        {(Object.keys(ROLE_LABELS) as MemberRole[])
                          .filter((r) => r !== 'owner')
                          .map((role) => (
                            <option key={role} value={role}>
                              {ROLE_LABELS[role]}
                            </option>
                          ))}
                      </select>
                    ) : (
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ROLE_COLORS[member.role as MemberRole]}`}
                      >
                        {ROLE_LABELS[member.role as MemberRole]}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        member.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {member.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {member.role !== 'owner' && (
                      <div className="flex items-center justify-end gap-2">
                        {editingMember?.user_id === member.user_id ? (
                          <button
                            onClick={() => setEditingMember(null)}
                            className="text-gray-600 hover:text-gray-900"
                          >
                            Cancel
                          </button>
                        ) : (
                          <button
                            onClick={() => setEditingMember(member)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Edit Role
                          </button>
                        )}
                        <button
                          onClick={() => handleRemoveMember(member)}
                          className="text-red-600 hover:text-red-900"
                          disabled={removeMemberMutation.isPending}
                        >
                          Remove
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Summary */}
      <div className="text-sm text-gray-500">
        {memberData?.total} member{memberData?.total !== 1 ? 's' : ''} total
        {filteredMembers.length !== memberData?.total &&
          ` (${filteredMembers.length} shown)`}
      </div>

      {/* Invite Dialog */}
      {showInviteDialog && (
        <InviteUserDialog
          organizationId={organizationId}
          onClose={() => setShowInviteDialog(false)}
        />
      )}
    </div>
  );
}
