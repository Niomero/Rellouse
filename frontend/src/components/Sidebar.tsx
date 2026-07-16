import { Link, useLocation } from 'react-router-dom'
import { MessageSquare, Search, User, Settings, LogOut, Shield } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

const Sidebar = () => {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const isActive = (path: string) => location.pathname.startsWith(path)

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="w-20 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col items-center py-4">
      {/* Logo */}
      <div className="mb-8">
        <div className="w-12 h-12 bg-primary-500 rounded-xl flex items-center justify-center text-white font-bold text-xl">
          R
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 flex flex-col space-y-4">
        <Link
          to="/chat"
          className={`p-3 rounded-xl transition-colors ${
            isActive('/chat')
              ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
          title="Chat"
        >
          <MessageSquare size={24} />
        </Link>

        <Link
          to="/search"
          className={`p-3 rounded-xl transition-colors ${
            isActive('/search')
              ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
          title="Search"
        >
          <Search size={24} />
        </Link>

        {user && (
          <Link
            to={`/profile/${user.username}`}
            className={`p-3 rounded-xl transition-colors ${
              isActive('/profile')
                ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
            title="Profile"
          >
            <User size={24} />
          </Link>
        )}

        <Link
          to="/verification"
          className={`p-3 rounded-xl transition-colors ${
            isActive('/verification')
              ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
          title="Verification"
        >
          <Shield size={24} />
        </Link>
      </nav>

      {/* Bottom Actions */}
      <div className="flex flex-col space-y-4">
        <Link
          to="/settings"
          className={`p-3 rounded-xl transition-colors ${
            isActive('/settings')
              ? 'bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
          title="Settings"
        >
          <Settings size={24} />
        </Link>

        <button
          onClick={handleLogout}
          className="p-3 rounded-xl text-gray-600 dark:text-gray-400 hover:bg-red-100 dark:hover:bg-red-900 hover:text-red-600 dark:hover:text-red-400 transition-colors"
          title="Logout"
        >
          <LogOut size={24} />
        </button>
      </div>
    </div>
  )
}

export default Sidebar
