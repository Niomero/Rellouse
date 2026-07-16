import { useParams } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { getRoleBadge } from '../utils/roleUtils'
import { Mail, Calendar } from 'lucide-react'

const ProfilePage = () => {
  const { username: _username } = useParams()
  const { user: currentUser } = useAuthStore()

  // TODO: Fetch user profile data
  const user = currentUser // Placeholder

  if (!user) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500 dark:text-gray-400">User not found</p>
      </div>
    )
  }

  const roleBadge = getRoleBadge(user.role)

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Profile Header */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 mb-6">
        <div className="flex items-start space-x-6">
          {/* Avatar */}
          <div className="w-24 h-24 rounded-full bg-primary-500 flex items-center justify-center text-white text-3xl font-bold flex-shrink-0">
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

          {/* User Info */}
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h1 className={`text-2xl font-bold ${roleBadge.color}`}>
                {user.username}
              </h1>
              {roleBadge.icon}
            </div>

            {/* Additional Usernames (for Owner/Admin) */}
            {user.additional_usernames && user.additional_usernames.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {user.additional_usernames.map((additionalUsername) => (
                  <span
                    key={additionalUsername}
                    className="text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full"
                  >
                    {additionalUsername}
                  </span>
                ))}
              </div>
            )}

            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {user.bio || 'No bio yet'}
            </p>

            <div className="flex items-center space-x-6 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-2">
                <Calendar size={16} />
                <span>Joined 2024</span>
              </div>
              <div className="flex items-center space-x-2">
                <Mail size={16} />
                <span>{roleBadge.label}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          {currentUser?.username === user.username && (
            <button className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors">
              Edit Profile
            </button>
          )}
        </div>
      </div>

      {/* Additional Info */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          About
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {user.bio || 'This user has not added a bio yet.'}
        </p>
      </div>
    </div>
  )
}

export default ProfilePage
