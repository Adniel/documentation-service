import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { organizationApi, workspaceApi, type Workspace } from '../lib/api';
import CreateOrganizationModal from '../components/CreateOrganizationModal';
import CreateWorkspaceModal from '../components/CreateWorkspaceModal';

export default function DashboardPage() {
  const { orgId } = useParams<{ orgId?: string }>();
  const [selectedOrg, setSelectedOrg] = useState<string | null>(null);
  const [showCreateOrgModal, setShowCreateOrgModal] = useState(false);
  const [showCreateWorkspaceModal, setShowCreateWorkspaceModal] = useState(false);

  const { data: organizations, isLoading: orgsLoading, error: orgsError } = useQuery({
    queryKey: ['organizations'],
    queryFn: organizationApi.list,
  });

  // Load workspaces for selected org
  const activeOrgId = orgId || selectedOrg || organizations?.[0]?.id;

  const { data: workspaces, isLoading: workspacesLoading } = useQuery({
    queryKey: ['workspaces', activeOrgId],
    queryFn: () => workspaceApi.listByOrg(activeOrgId!),
    enabled: !!activeOrgId,
  });

  if (orgsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading...</div>
      </div>
    );
  }

  if (orgsError) {
    return (
      <div className="bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 rounded">
        Failed to load organizations
      </div>
    );
  }

  const activeOrg = organizations?.find((o) => o.id === activeOrgId);

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <button
          onClick={() => setShowCreateOrgModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
        >
          Create Organization
        </button>
      </div>

      <CreateOrganizationModal
        isOpen={showCreateOrgModal}
        onClose={() => setShowCreateOrgModal(false)}
      />

      {/* Organization tabs */}
      {organizations && organizations.length > 0 && (
        <div className="border-b border-slate-700">
          <nav className="flex gap-1 -mb-px overflow-x-auto">
            {organizations.map((org) => (
              <button
                key={org.id}
                onClick={() => setSelectedOrg(org.id)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                  org.id === activeOrgId
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-slate-400 hover:text-white hover:border-slate-600'
                }`}
              >
                {org.name}
              </button>
            ))}
          </nav>
        </div>
      )}

      {/* Workspaces */}
      {activeOrg && (
        <section>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-white">
              Workspaces in {activeOrg.name}
            </h2>
            <button
              onClick={() => setShowCreateWorkspaceModal(true)}
              className="px-3 py-1.5 text-sm bg-slate-700 text-slate-300 rounded hover:bg-slate-600 transition"
            >
              + New Workspace
            </button>
          </div>

          <CreateWorkspaceModal
            isOpen={showCreateWorkspaceModal}
            onClose={() => setShowCreateWorkspaceModal(false)}
            organizationId={activeOrg.id}
            organizationName={activeOrg.name}
          />

          {workspacesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-32 bg-slate-800 rounded-lg animate-pulse border border-slate-700"
                />
              ))}
            </div>
          ) : workspaces && workspaces.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {workspaces.map((workspace) => (
                <WorkspaceCard key={workspace.id} workspace={workspace} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-slate-800 rounded-lg border border-slate-700">
              <h3 className="text-lg font-medium text-white mb-2">
                No workspaces yet
              </h3>
              <p className="text-slate-400 mb-4">
                Create your first workspace to start documenting
              </p>
              <button
                onClick={() => setShowCreateWorkspaceModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
              >
                Create Workspace
              </button>
            </div>
          )}
        </section>
      )}

      {/* Empty state when no orgs */}
      {(!organizations || organizations.length === 0) && (
        <div className="text-center py-12 bg-slate-800 rounded-lg border border-slate-700">
          <h3 className="text-lg font-medium text-white mb-2">
            No organizations yet
          </h3>
          <p className="text-slate-400 mb-4">
            Create your first organization to get started
          </p>
          <button
            onClick={() => setShowCreateOrgModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            Create Organization
          </button>
        </div>
      )}

      {/* Quick stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-2xl font-bold text-white">
            {organizations?.length || 0}
          </div>
          <div className="text-sm text-slate-400">Organizations</div>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-2xl font-bold text-white">
            {workspaces?.length || 0}
          </div>
          <div className="text-sm text-slate-400">Workspaces</div>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-2xl font-bold text-white">0</div>
          <div className="text-sm text-slate-400">Pending Reviews</div>
        </div>
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-2xl font-bold text-white">0</div>
          <div className="text-sm text-slate-400">My Drafts</div>
        </div>
      </div>
    </div>
  );
}

interface WorkspaceCardProps {
  workspace: Workspace;
}

function WorkspaceCard({ workspace }: WorkspaceCardProps) {
  return (
    <Link
      to={`/workspace/${workspace.id}`}
      className="block bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-blue-500/50 hover:bg-slate-750 transition-all group"
    >
      <div className="flex items-start gap-4">
        <span className="text-3xl">📂</span>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors truncate">
            {workspace.name}
          </h3>
          <p className="text-slate-400 text-sm mt-1 line-clamp-2">
            {workspace.description || 'No description'}
          </p>
          <div className="flex items-center gap-3 mt-3">
            <span className="text-xs text-slate-500">/{workspace.slug}</span>
            {workspace.is_public && (
              <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded">
                Public
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
