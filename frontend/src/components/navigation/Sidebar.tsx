/**
 * Sidebar Navigation Component
 *
 * Displays hierarchical tree structure of spaces and pages.
 */

import { useState } from 'react';
import { Link, useLocation, useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { navigationApi, type NavigationTreeNode } from '../../lib/api';
import { clsx } from 'clsx';

interface SidebarProps {
  workspaceId: string;
  collapsed?: boolean;
  onToggle?: () => void;
}

const DIATAXIS_ICONS: Record<string, string> = {
  tutorial: '📚',
  how_to: '🔧',
  reference: '📖',
  explanation: '💡',
  mixed: '📁',
};

const DIATAXIS_COLORS: Record<string, string> = {
  tutorial: 'text-green-400',
  how_to: 'text-blue-400',
  reference: 'text-purple-400',
  explanation: 'text-yellow-400',
  mixed: 'text-slate-400',
};

export function Sidebar({ workspaceId, collapsed = false, onToggle }: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const currentSpaceId = searchParams.get('space');

  const { data: tree, isLoading } = useQuery({
    queryKey: ['workspace-tree', workspaceId],
    queryFn: () => navigationApi.getWorkspaceTree(workspaceId),
    enabled: !!workspaceId,
  });

  if (collapsed) {
    return (
      <div className="w-12 bg-slate-800 border-r border-slate-700 flex flex-col items-center py-4">
        <button
          onClick={onToggle}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded"
          title="Expand sidebar"
        >
          →
        </button>
      </div>
    );
  }

  return (
    <aside className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 flex items-center justify-between">
        <div className="flex-1 min-w-0">
          {tree && (
            <>
              <div className="text-xs text-slate-500 truncate">
                {tree.organization.name}
              </div>
              <h2 className="font-semibold text-white truncate">{tree.name}</h2>
            </>
          )}
        </div>
        {onToggle && (
          <button
            onClick={onToggle}
            className="p-1 text-slate-400 hover:text-white hover:bg-slate-700 rounded ml-2"
            title="Collapse sidebar"
          >
            ←
          </button>
        )}
      </div>

      {/* Tree Content */}
      <div className="flex-1 overflow-y-auto p-2">
        {isLoading ? (
          <div className="text-slate-400 text-sm p-2">Loading...</div>
        ) : tree ? (
          <TreeNode
            nodes={tree.children || []}
            currentPath={location.pathname}
            level={0}
          />
        ) : (
          <div className="text-slate-400 text-sm p-2">No content</div>
        )}
      </div>

      {/* Footer - Quick actions */}
      <div className="p-2 border-t border-slate-700">
        <button
          onClick={() => {
            if (currentSpaceId) {
              navigate(`/editor/new?space=${currentSpaceId}`);
            } else {
              // If no space selected, navigate to workspace content browser
              navigate(`/workspace/${workspaceId}`);
            }
          }}
          className={clsx(
            'w-full px-3 py-2 text-sm rounded flex items-center gap-2',
            currentSpaceId
              ? 'text-slate-300 hover:text-white hover:bg-slate-700'
              : 'text-slate-500 hover:text-slate-400 hover:bg-slate-700/50'
          )}
          title={currentSpaceId ? 'Create a new page' : 'Select a space first to create pages'}
        >
          <span>+</span>
          <span>New Page</span>
          {!currentSpaceId && <span className="text-xs text-slate-600">(select space)</span>}
        </button>
      </div>
    </aside>
  );
}

interface TreeNodeProps {
  nodes: NavigationTreeNode[];
  currentPath: string;
  level: number;
}

function TreeNode({ nodes, currentPath, level }: TreeNodeProps) {
  return (
    <ul className="space-y-0.5">
      {nodes.map((node) => (
        <TreeItem key={node.id} node={node} currentPath={currentPath} level={level} />
      ))}
    </ul>
  );
}

interface TreeItemProps {
  node: NavigationTreeNode;
  currentPath: string;
  level: number;
}

function TreeItem({ node, currentPath, level }: TreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(level < 2);
  const hasChildren = (node.children && node.children.length > 0) || (node.pages && node.pages.length > 0);

  const diataxisType = node.diataxis_type || 'mixed';
  const icon = DIATAXIS_ICONS[diataxisType];
  const colorClass = DIATAXIS_COLORS[diataxisType];

  if (node.type === 'space') {
    return (
      <li>
        <div
          className={clsx(
            'flex items-center gap-1 px-2 py-1 rounded cursor-pointer',
            'hover:bg-slate-700/50 text-slate-300 hover:text-white',
            'transition-colors'
          )}
          style={{ paddingLeft: `${level * 12 + 8}px` }}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {hasChildren && (
            <span className="text-xs text-slate-500 w-4">
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
          {!hasChildren && <span className="w-4" />}
          <span className={clsx('text-sm', colorClass)} title={diataxisType}>
            {icon}
          </span>
          <Link
            to={`/space/${node.id}`}
            className="flex-1 text-sm truncate"
            onClick={(e) => e.stopPropagation()}
          >
            {node.name}
          </Link>
        </div>

        {isExpanded && hasChildren && (
          <div className="mt-0.5">
            {/* Child spaces */}
            {node.children && node.children.length > 0 && (
              <TreeNode
                nodes={node.children}
                currentPath={currentPath}
                level={level + 1}
              />
            )}
            {/* Pages in this space */}
            {node.pages && node.pages.length > 0 && (
              <ul className="space-y-0.5 mt-0.5">
                {node.pages.map((page) => (
                  <li key={page.id}>
                    <Link
                      to={`/editor/${page.id}`}
                      className={clsx(
                        'flex items-center gap-2 px-2 py-1 rounded text-sm',
                        'hover:bg-slate-700/50 transition-colors',
                        currentPath === `/editor/${page.id}`
                          ? 'bg-blue-600/20 text-blue-400'
                          : 'text-slate-400 hover:text-white'
                      )}
                      style={{ paddingLeft: `${(level + 1) * 12 + 8 + 16}px` }}
                    >
                      <span className="text-xs">📄</span>
                      <span className="truncate">{page.title}</span>
                      {page.status === 'draft' && (
                        <span className="text-xs text-yellow-500">●</span>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </li>
    );
  }

  return null;
}

export default Sidebar;
