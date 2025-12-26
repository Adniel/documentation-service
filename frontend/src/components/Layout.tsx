import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

export default function Layout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link to="/" className="text-xl font-semibold text-white">
                Documentation Service
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              <Link
                to="/admin"
                className="px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded-md transition"
              >
                Admin
              </Link>
              {user && (
                <span className="text-slate-300 text-sm">
                  {user.full_name}
                </span>
              )}
              <button
                onClick={handleLogout}
                className="px-3 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-700 rounded-md transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
