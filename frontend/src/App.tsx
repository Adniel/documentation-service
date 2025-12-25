import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import Layout from './components/Layout';
import WorkspaceLayout from './components/layout/WorkspaceLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import EditorPage from './pages/EditorPage';
import NewPagePage from './pages/NewPagePage';
import PageHistoryPage from './pages/PageHistoryPage';
import ContentBrowserPage from './pages/ContentBrowserPage';
import SearchResultsPage from './pages/SearchResultsPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Main dashboard layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="org/:orgId" element={<DashboardPage />} />
      </Route>

      {/* Workspace layout with sidebar */}
      <Route
        path="/workspace/:workspaceId"
        element={
          <ProtectedRoute>
            <WorkspaceLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<ContentBrowserPage />} />
        <Route path="browse" element={<ContentBrowserPage />} />
        <Route path="search" element={<SearchResultsPage />} />
      </Route>

      {/* Editor and space views (workspace context) */}
      <Route
        path="/editor/new"
        element={
          <ProtectedRoute>
            <NewPagePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/editor/:pageId"
        element={
          <ProtectedRoute>
            <EditorPage />
          </ProtectedRoute>
        }
      />

      {/* Page history and version control */}
      <Route
        path="/pages/:pageId/history"
        element={
          <ProtectedRoute>
            <PageHistoryPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/space/:spaceId"
        element={
          <ProtectedRoute>
            <ContentBrowserPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
