import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import Layout from './components/Layout';
import WorkspaceLayout from './components/layout/WorkspaceLayout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ContentBrowserPage from './pages/ContentBrowserPage';
import SearchResultsPage from './pages/SearchResultsPage';
import NewPagePage from './pages/NewPagePage';

// Lazy-loaded heavy routes
const AdminPage = lazy(() => import('./pages/AdminPage'));
const EditorPage = lazy(() => import('./pages/EditorPage'));
const ReadingPage = lazy(() => import('./pages/ReadingPage'));
const PageHistoryPage = lazy(() => import('./pages/PageHistoryPage'));

function LoadingFallback() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <div style={{ textAlign: 'center' }}>
        <div className="spinner" aria-label="Loading page" role="status" />
        <p>Loading...</p>
      </div>
    </div>
  );
}

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

      {/* Admin page */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <Suspense fallback={<LoadingFallback />}>
              <AdminPage />
            </Suspense>
          </ProtectedRoute>
        }
      />

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
            <Suspense fallback={<LoadingFallback />}>
              <EditorPage />
            </Suspense>
          </ProtectedRoute>
        }
      />

      {/* Read-only page viewer (Sprint I) */}
      <Route
        path="/pages/:pageId"
        element={
          <ProtectedRoute>
            <Suspense fallback={<LoadingFallback />}>
              <ReadingPage />
            </Suspense>
          </ProtectedRoute>
        }
      />

      {/* Page history and version control */}
      <Route
        path="/pages/:pageId/history"
        element={
          <ProtectedRoute>
            <Suspense fallback={<LoadingFallback />}>
              <PageHistoryPage />
            </Suspense>
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
