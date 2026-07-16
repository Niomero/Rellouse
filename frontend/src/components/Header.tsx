import { useAuthStore } from '../store/authStore'
import { useThemeStore } from '../store/themeStore'
import { Moon, Sun, Bell } from 'lucide-react'
import { getRoleBadge } from '../utils/roleUtils'

const Header = () => {
  const { user } = useAuthStore()
  const { theme, toggleTheme } = useThemeStore()

  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6">
      {/* Left side - App name */}
      <div className="flex items-center space-x-4">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">
          Rellouse Messenger
        </h1>
      </div>

      {/* Right side - User info and actions */}
      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <button
          className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative"
          title="Notifications"
        >
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>

        {/* User info */}
        {user && (
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-medium ${getRoleBadge(user.role).color}`}>
                  {user.username}
                </span>
                {getRoleBadge(user.role).icon}
              </div>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {user.role}
              </span>
            </div>
            <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-medium">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.username}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                user.username.charAt(1).toUpperCase()
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header
