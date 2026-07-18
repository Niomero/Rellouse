import { motion } from 'framer-motion'
import { useThemeStore } from '../store/themeStore'
import { useAuthStore } from '../store/authStore'
import { Moon, Sun, User, Bell, Shield, LogOut, Palette, Lock, Globe } from 'lucide-react'

const SettingsPage = () => {
  const { theme, toggleTheme } = useThemeStore()
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
        >
          <h1 className="text-3xl font-bold gradient-text mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account and preferences</p>
        </motion.div>

        {/* Appearance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-indigo-500/20">
              <Palette className="w-5 h-5 text-indigo-400" />
            </div>
            <h2 className="text-xl font-bold text-white">Appearance</h2>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700/50">
            <div className="flex items-center gap-3">
              {theme === 'light' ? (
                <Sun className="w-5 h-5 text-yellow-400" />
              ) : (
                <Moon className="w-5 h-5 text-indigo-400" />
              )}
              <div>
                <p className="font-semibold text-white">Theme</p>
                <p className="text-sm text-gray-400">
                  {theme === 'light' ? 'Light mode' : 'Dark mode'}
                </p>
              </div>
            </div>
            <button
              onClick={toggleTheme}
              className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl transition-all font-semibold"
            >
              Switch to {theme === 'light' ? 'Dark' : 'Light'}
            </button>
          </div>
        </motion.div>

        {/* Account */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-purple-500/20">
              <User className="w-5 h-5 text-purple-400" />
            </div>
            <h2 className="text-xl font-bold text-white">Account</h2>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700/50 hover:bg-gray-800/70 transition-all">
              <div className="flex items-center gap-3">
                <User className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="font-semibold text-white">Profile</p>
                  <p className="text-sm text-gray-400">{user?.username}</p>
                </div>
              </div>
              <button className="px-4 py-2 bg-gray-700/50 hover:bg-gray-700 text-white rounded-xl transition-all font-semibold">
                Edit
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700/50 hover:bg-gray-800/70 transition-all">
              <div className="flex items-center gap-3">
                <Lock className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="font-semibold text-white">Privacy & Security</p>
                  <p className="text-sm text-gray-400">Manage your privacy settings</p>
                </div>
              </div>
              <button className="px-4 py-2 bg-gray-700/50 hover:bg-gray-700 text-white rounded-xl transition-all font-semibold">
                Manage
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700/50 hover:bg-gray-800/70 transition-all">
              <div className="flex items-center gap-3">
                <Bell className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="font-semibold text-white">Notifications</p>
                  <p className="text-sm text-gray-400">Configure notification preferences</p>
                </div>
              </div>
              <button className="px-4 py-2 bg-gray-700/50 hover:bg-gray-700 text-white rounded-xl transition-all font-semibold">
                Configure
              </button>
            </div>
          </div>
        </motion.div>

        {/* Preferences */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-blue-500/20">
              <Globe className="w-5 h-5 text-blue-400" />
            </div>
            <h2 className="text-xl font-bold text-white">Preferences</h2>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 bg-gray-800/50 rounded-xl border border-gray-700/50">
              <div>
                <p className="font-semibold text-white">Language</p>
                <p className="text-sm text-gray-400">English (US)</p>
              </div>
              <button className="px-4 py-2 bg-gray-700/50 hover:bg-gray-700 text-white rounded-xl transition-all font-semibold">
                Change
              </button>
            </div>
          </div>
        </motion.div>

        {/* Danger Zone */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6 border-red-500/30"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-red-500/20">
              <Shield className="w-5 h-5 text-red-400" />
            </div>
            <h2 className="text-xl font-bold text-white">Danger Zone</h2>
          </div>
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 p-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 rounded-xl transition-all font-semibold"
          >
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </motion.div>
      </div>
    </div>
  )
}

export default SettingsPage