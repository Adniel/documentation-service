/**
 * WorkspaceLayout Component
 *
 * Layout for workspace views with sidebar navigation.
 */

import { useState } from 'react';
import { Outlet, Link, useNavigate, useParams } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { Sidebar } from '../navigation/Sidebar';
import { SearchBar } from '../search/SearchBar';

export function WorkspaceLayout() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!workspaceId) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">No workspace selected</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 h-14 flex-shrink-0">
        <div className="h-full px-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-lg font-semibold text-white hover:text-blue-400 transition-colors">
              📚 DocService
            </Link>
          </div>

          {/* Search */}
          <div className="flex-1 max-w-xl">
            <SearchBar workspaceId={workspaceId} />
          </div>

          {/* User menu */}
          <div className="flex items-center gap-4">
            {user && (
              <span className="text-slate-300 text-sm hidden md:block">
                {user.full_name}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main area with sidebar */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          workspaceId={workspaceId}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Content area */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default WorkspaceLayout;
