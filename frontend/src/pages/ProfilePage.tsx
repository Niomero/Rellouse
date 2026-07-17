import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  MessageCircle,
  User,
  Bot,
  CheckCircle,
  Calendar,
  Clock,
  Shield,
  Crown,
} from 'lucide-react'
import { cn } from '../utils/cn'
import { useToast } from '../hooks/useToast'
import { useAuthStore } from '../store/authStore'
import { ProfileSkeleton } from '../components/ui/Skeleton'
import api from '../services/api'
import { format } from 'date-fns'

interface UserProfile {
  id: number
  username: string
  display_name: string | null
  avatar_url: string | null
  bio: string | null
  role: string
  is_verified: boolean
  is_online: boolean
  is_bot: boolean
  last_seen: string | null
  created_at: string
  additional_usernames: string[] | null
}

export default function ProfilePage() {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuthStore()
  const { error: showError } = useToast()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (userId) {
      loadProfile(parseInt(userId))
    }
  }, [userId])

  const loadProfile = async (id: number) => {
    setLoading(true)
    try {
      const response = await api.get<UserProfile>(`/api/users/${id}`)
      setProfile(response.data)
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to load profile')
      navigate('/search')
    } finally {
      setLoading(false)
    }
  }

  const handleMessage = () => {
    if (profile) {
      navigate(`/chat/${profile.id}`)
    }
  }

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'owner':
        return (
          <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-xs font-medium">
            <Crown className="w-3 h-3" />
            <span>Owner</span>
          </div>
        )
      case 'administrator':
        return (
          <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs font-medium">
            <Shield className="w-3 h-3" />
            <span>Admin</span>
          </div>
        )
      case 'verified':
        return (
          <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xs font-medium">
            <CheckCircle className="w-3 h-3" />
            <span>Verified</span>
          </div>
        )
      default:
        return null
    }
  }

  const getStatusText = () => {
    if (!profile) return ''
    
    if (profile.is_bot) return 'System Bot'
    if (profile.is_online) return 'Online'
    if (profile.last_seen) {
      const lastSeen = new Date(profile.last_seen)
      const now = new Date()
      const diffMinutes = Math.floor((now.getTime() - lastSeen.getTime()) / 60000)
      
      if (diffMinutes < 1) return 'Just now'
      if (diffMinutes < 60) return `${diffMinutes}m ago`
      if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`
      return format(lastSeen, 'MMM d, yyyy')
    }
    return 'Offline'
  }

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <div className="glass border-b border-neutral-200 dark:border-neutral-700 p-4">
          <button
            onClick={() => navigate(-1)}
            className="liquid-btn liquid-hover liquid-press p-2 rounded-xl"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
        </div>
        <ProfileSkeleton />
      </div>
    )
  }

  if (!profile) return null

  const isOwnProfile = currentUser?.id === profile.id

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="glass border-b border-neutral-200 dark:border-neutral-700 p-4">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate(-1)}
            className="liquid-btn liquid-hover liquid-press p-2 rounded-xl"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            Profile
          </h1>
          <div className="w-10" />
        </div>
      </div>

      {/* Profile Content */}
      <div className="flex-1 overflow-y-auto liquid-scrollbar">
        <div className="max-w-2xl mx-auto p-6 space-y-6">
          {/* Avatar and Basic Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-3xl p-8"
          >
            <div className="flex flex-col items-center text-center space-y-4">
              {/* Avatar */}
              <div className="relative">
                <div className="liquid-avatar w-32 h-32">
                  {profile.avatar_url ? (
                    <img
                      src={profile.avatar_url}
                      alt={profile.display_name || profile.username}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                      {profile.is_bot ? (
                        <Bot className="w-16 h-16 text-white" />
                      ) : (
                        <User className="w-16 h-16 text-white" />
                      )}
                    </div>
                  )}
                </div>
                {profile.is_online && !profile.is_bot && (
                  <div className="absolute bottom-2 right-2 w-6 h-6 bg-green-500 border-4 border-white dark:border-neutral-900 rounded-full" />
                )}
              </div>

              {/* Name and Username */}
              <div className="space-y-2">
                <div className="flex items-center justify-center gap-2">
                  <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                    {profile.display_name || profile.username}
                  </h2>
                  {profile.is_verified && (
                    <CheckCircle className="w-6 h-6 text-primary-500" />
                  )}
                </div>
                <p className="text-base text-neutral-600 dark:text-neutral-400">
                  {profile.username}
                </p>
              </div>

              {/* Role Badge */}
              {getRoleBadge(profile.role)}

              {/* Status */}
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-neutral-500" />
                <span className={cn(
                  'font-medium',
                  profile.is_online ? 'text-green-600 dark:text-green-400' : 'text-neutral-600 dark:text-neutral-400'
                )}>
                  {getStatusText()}
                </span>
              </div>

              {/* Message Button */}
              {!isOwnProfile && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleMessage}
                  className="liquid-btn-primary w-full max-w-xs rounded-xl px-6 py-3 font-medium flex items-center justify-center gap-2"
                >
                  <MessageCircle className="w-5 h-5" />
                  <span>Send Message</span>
                </motion.button>
              )}
            </div>
          </motion.div>

          {/* Bio */}
          {profile.bio && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <h3 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                About
              </h3>
              <p className="text-base text-neutral-900 dark:text-neutral-100 whitespace-pre-wrap">
                {profile.bio}
              </p>
            </motion.div>
          )}

          {/* Additional Usernames */}
          {profile.additional_usernames && profile.additional_usernames.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-6"
            >
              <h3 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                Additional Usernames
              </h3>
              <div className="flex flex-wrap gap-2">
                {profile.additional_usernames.map((username, index) => (
                  <span
                    key={index}
                    className="liquid-badge px-3 py-1.5 text-sm font-medium text-neutral-700 dark:text-neutral-300"
                  >
                    {username}
                  </span>
                ))}
              </div>
            </motion.div>
          )}

          {/* Account Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass rounded-2xl p-6"
          >
            <h3 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-4">
              Account Information
            </h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="w-4 h-4 text-neutral-500" />
                <span className="text-neutral-600 dark:text-neutral-400">
                  Joined {format(new Date(profile.created_at), 'MMMM d, yyyy')}
                </span>
              </div>
              {profile.is_bot && (
                <div className="flex items-center gap-3 text-sm">
                  <Bot className="w-4 h-4 text-neutral-500" />
                  <span className="text-neutral-600 dark:text-neutral-400">
                    Automated System Bot
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}