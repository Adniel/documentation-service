/**
 * ContentBrowser Page
 *
 * Main content browsing interface with space listing and page grid.
 */

import { useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { spaceApi, contentApi, navigationApi, workspaceApi } from '../lib/api';
import type { Space, PageSummary } from '../types';
import { Breadcrumbs } from '../components/navigation/Breadcrumbs';
import CreateSpaceModal from '../components/CreateSpaceModal';
import { clsx } from 'clsx';

type DiátaxisType = 'tutorial' | 'how_to' | 'reference' | 'explanation' | 'all';

const DIATAXIS_TYPES: Array<{ value: DiátaxisType; label: string; icon: string; color: string }> = [
  { value: 'all', label: 'All', icon: '📚', color: 'text-slate-400' },
  { value: 'tutorial', label: 'Tutorials', icon: '📚', color: 'text-green-400' },
  { value: 'how_to', label: 'How-to Guides', icon: '🔧', color: 'text-blue-400' },
  { value: 'reference', label: 'Reference', icon: '📖', color: 'text-purple-400' },
  { value: 'explanation', label: 'Explanation', icon: '💡', color: 'text-yellow-400' },
];

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  in_review: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  approved: 'bg-green-500/20 text-green-400 border-green-500/30',
  effective: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  obsolete: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
};

export default function ContentBrowserPage() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const spaceId = searchParams.get('space');
  const [selectedType, setSelectedType] = useState<DiátaxisType>('all');
  const [showCreateSpaceModal, setShowCreateSpaceModal] = useState(false);

  // Fetch workspace details
  const { data: workspace } = useQuery({
    queryKey: ['workspace', workspaceId],
    queryFn: () => workspaceApi.get(workspaceId!),
    enabled: !!workspaceId,
  });

  // Fetch spaces for this workspace
  const { data: spaces, isLoading: spacesLoading } = useQuery({
    queryKey: ['workspace-spaces', workspaceId],
    queryFn: () => spaceApi.listByWorkspace(workspaceId!),
    enabled: !!workspaceId,
  });

  // Fetch pages if a space is selected
  const { data: pages, isLoading: pagesLoading } = useQuery({
    queryKey: ['space-pages', spaceId],
    queryFn: () => contentApi.listBySpace(spaceId!),
    enabled: !!spaceId,
  });

  // Fetch recent pages for workspace overview
  const { data: recentPages } = useQuery({
    queryKey: ['recent-pages', workspaceId],
    queryFn: () => navigationApi.getRecentPages(10, workspaceId),
    enabled: !!workspaceId && !spaceId,
  });

  const handleSpaceSelect = (space: Space | null) => {
    if (space) {
      setSearchParams({ space: space.id });
    } else {
      setSearchParams({});
    }
  };

  const filteredSpaces = spaces?.filter((space) => {
    if (selectedType === 'all') return true;
    return space.diataxis_type === selectedType;
  });

  const filteredPages = pages?.filter((page) => {
    if (selectedType === 'all') return true;
    // Pages inherit type from their space
    const parentSpace = spaces?.find((s) => s.id === page.space_id);
    return parentSpace?.diataxis_type === selectedType;
  });

  if (!workspaceId) {
    return <div className="p-8 text-slate-400">No workspace selected</div>;
  }

  return (
    <div className="h-full flex flex-col">
      {/* Create Space Modal */}
      <CreateSpaceModal
        isOpen={showCreateSpaceModal}
        onClose={() => setShowCreateSpaceModal(false)}
        workspaceId={workspaceId}
        workspaceName={workspace?.name || 'Workspace'}
      />

      {/* Header with breadcrumbs and filters */}
      <div className="bg-slate-800/50 border-b border-slate-700 px-6 py-4">
        <div className="mb-3">
          {spaceId ? (
            <Breadcrumbs spaceId={spaceId} />
          ) : (
            <nav className="text-sm text-slate-400">
              <span className="text-white font-medium">Content Browser</span>
            </nav>
          )}
        </div>

        {/* Diátaxis filter */}
        <div className="flex flex-wrap gap-2">
          {DIATAXIS_TYPES.map((type) => (
            <button
              key={type.value}
              onClick={() => setSelectedType(type.value)}
              className={clsx(
                'px-3 py-1.5 rounded-full text-sm font-medium transition-colors flex items-center gap-1.5',
                selectedType === type.value
                  ? 'bg-slate-600 text-white'
                  : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700 hover:text-white'
              )}
            >
              <span>{type.icon}</span>
              <span>{type.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-y-auto p-6">
        {spaceId ? (
          // Space content view
          <SpaceContentView
            spaceId={spaceId}
            pages={filteredPages || []}
            isLoading={pagesLoading}
            onBack={() => handleSpaceSelect(null)}
          />
        ) : (
          // Workspace overview
          <WorkspaceOverview
            spaces={filteredSpaces || []}
            recentPages={recentPages || []}
            isLoading={spacesLoading}
            onSpaceSelect={handleSpaceSelect}
            onCreateSpace={() => setShowCreateSpaceModal(true)}
          />
        )}
      </div>
    </div>
  );
}

interface WorkspaceOverviewProps {
  spaces: Space[];
  recentPages: PageSummary[];
  isLoading: boolean;
  onSpaceSelect: (space: Space) => void;
  onCreateSpace: () => void;
}

function WorkspaceOverview({
  spaces,
  recentPages,
  isLoading,
  onSpaceSelect,
  onCreateSpace,
}: WorkspaceOverviewProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="h-32 bg-slate-800 rounded-lg animate-pulse border border-slate-700"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Spaces grid */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-white">Spaces</h2>
          <button
            onClick={onCreateSpace}
            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            + New Space
          </button>
        </div>
        {spaces.length === 0 ? (
          <div className="text-center py-12 bg-slate-800/50 rounded-lg border border-slate-700">
            <p className="text-slate-400 mb-4">No spaces found</p>
            <button
              onClick={onCreateSpace}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create First Space
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {spaces.map((space) => (
              <SpaceCard key={space.id} space={space} onClick={() => onSpaceSelect(space)} />
            ))}
          </div>
        )}
      </section>

      {/* Recent pages */}
      {recentPages.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-white mb-4">Recent Pages</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {recentPages.map((page) => (
              <PageListItem key={page.id} page={page} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

interface SpaceCardProps {
  space: Space;
  onClick: () => void;
}

function SpaceCard({ space, onClick }: SpaceCardProps) {
  const typeInfo = DIATAXIS_TYPES.find((t) => t.value === space.diataxis_type) || DIATAXIS_TYPES[0];

  return (
    <button
      onClick={onClick}
      className="text-left p-4 bg-slate-800 rounded-lg border border-slate-700 hover:border-slate-600 hover:bg-slate-750 transition-all group"
    >
      <div className="flex items-start gap-3">
        <span className={clsx('text-2xl', typeInfo.color)}>{typeInfo.icon}</span>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-white group-hover:text-blue-400 transition-colors truncate">
            {space.name}
          </h3>
          <p className="text-sm text-slate-400 line-clamp-2 mt-1">
            {space.description || 'No description'}
          </p>
          <div className="mt-2 flex items-center gap-2">
            <span className={clsx('text-xs px-2 py-0.5 rounded-full bg-slate-700', typeInfo.color)}>
              {typeInfo.label}
            </span>
          </div>
        </div>
      </div>
    </button>
  );
}

interface SpaceContentViewProps {
  spaceId: string;
  pages: PageSummary[];
  isLoading: boolean;
  onBack: () => void;
}

function SpaceContentView({ spaceId, pages, isLoading, onBack }: SpaceContentViewProps) {
  const { data: spaceDetails } = useQuery({
    queryKey: ['space', spaceId],
    queryFn: () => spaceApi.get(spaceId),
  });

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="h-16 bg-slate-800 rounded-lg animate-pulse border border-slate-700"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Space header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={onBack}
            className="text-sm text-slate-400 hover:text-white mb-2 flex items-center gap-1"
          >
            ← Back to spaces
          </button>
          <h2 className="text-xl font-semibold text-white">{spaceDetails?.name || 'Space'}</h2>
          {spaceDetails?.description && (
            <p className="text-slate-400 mt-1">{spaceDetails.description}</p>
          )}
        </div>
        <Link
          to={`/editor/new?space=${spaceId}`}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <span>+</span>
          <span>New Page</span>
        </Link>
      </div>

      {/* Pages list */}
      {pages.length === 0 ? (
        <div className="text-center py-12 bg-slate-800/50 rounded-lg border border-slate-700">
          <p className="text-slate-400 mb-4">No pages in this space yet</p>
          <Link
            to={`/editor/new?space=${spaceId}`}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
          >
            <span>+</span>
            <span>Create First Page</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {pages.map((page) => (
            <PageListItem key={page.id} page={page} showSpace={false} />
          ))}
        </div>
      )}
    </div>
  );
}

interface PageListItemProps {
  page: PageSummary;
  showSpace?: boolean;
}

function PageListItem({ page, showSpace = true }: PageListItemProps) {
  const statusClass = STATUS_COLORS[page.status] || STATUS_COLORS.draft;

  return (
    <Link
      to={`/editor/${page.id}`}
      className="flex items-center gap-4 p-3 bg-slate-800 rounded-lg border border-slate-700 hover:border-slate-600 hover:bg-slate-750 transition-all group"
    >
      <span className="text-xl text-slate-500 group-hover:text-slate-400">📄</span>
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-white group-hover:text-blue-400 transition-colors truncate">
          {page.title}
        </h4>
        {page.summary && (
          <p className="text-sm text-slate-400 truncate">{page.summary}</p>
        )}
      </div>
      <div className="flex items-center gap-3">
        <span className={clsx('text-xs px-2 py-1 rounded border', statusClass)}>
          {page.status.replace('_', ' ')}
        </span>
        <span className="text-xs text-slate-500">v{page.version}</span>
        {page.document_number && (
          <span className="text-xs text-slate-500 font-mono">{page.document_number}</span>
        )}
      </div>
    </Link>
  );
}
