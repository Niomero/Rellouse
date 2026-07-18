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
  Zap,
  Mail,
  AtSign,
} from 'lucide-react'
import { useToast } from '../hooks/useToast'
import { useAuthStore } from '../store/authStore'
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
        return {
          icon: <Crown className="w-4 h-4" />,
          label: 'Owner',
          gradient: 'from-yellow-500 to-orange-500'
        }
      case 'administrator':
        return {
          icon: <Shield className="w-4 h-4" />,
          label: 'Admin',
          gradient: 'from-red-500 to-pink-500'
        }
      case 'verified':
        return {
          icon: <Zap className="w-4 h-4" />,
          label: 'Verified',
          gradient: 'from-indigo-500 to-purple-500'
        }
      default:
        return null
    }
  }

  const getStatusText = () => {
    if (!profile) return ''
    if (profile.is_online) return 'Online'
    if (profile.last_seen) {
      return `Last seen ${format(new Date(profile.last_seen), 'MMM dd, HH:mm')}`
    }
    return 'Offline'
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent"></div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <User className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Profile not found</p>
        </div>
      </div>
    )
  }

  const roleBadge = getRoleBadge(profile.role)
  const isOwnProfile = currentUser?.id === profile.id

  return (
    <div className="h-full overflow-y-auto bg-gray-900">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="glass-card border-b border-gray-700/50 p-6"
        >
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
        </motion.div>

        {/* Profile Content */}
        <div className="p-6 space-y-6">
          {/* Profile Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card p-8"
          >
            <div className="flex flex-col md:flex-row gap-8">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <div className="relative">
                  <div className="w-32 h-32 rounded-2xl overflow-hidden shadow-2xl"
                       style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' }}>
                    {profile.avatar_url ? (
                      <img src={profile.avatar_url} alt={profile.username} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-white font-bold text-5xl">
                        {profile.username.charAt(1).toUpperCase()}
                      </div>
                    )}
                  </div>
                  {profile.is_online && (
                    <div className="absolute bottom-2 right-2 w-6 h-6 bg-green-500 rounded-full border-4 border-gray-900"></div>
                  )}
                </div>
              </div>

              {/* Info */}
              <div className="flex-1 space-y-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h1 className="text-3xl font-bold text-white">
                      {profile.display_name || profile.username}
                    </h1>
                    {profile.is_verified && (
                      <CheckCircle className="w-6 h-6 text-indigo-400" />
                    )}
                    {profile.is_bot && (
                      <span className="px-3 py-1 text-sm font-semibold bg-purple-500/20 text-purple-400 rounded-full">
                        BOT
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-400 mb-3">
                    <AtSign className="w-4 h-4" />
                    <span>{profile.username}</span>
                  </div>

                  {roleBadge && (
                    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r ${roleBadge.gradient} text-white font-semibold shadow-lg`}>
                      {roleBadge.icon}
                      <span>{roleBadge.label}</span>
                    </div>
                  )}
                </div>

                {profile.bio && (
                  <p className="text-gray-300 leading-relaxed">{profile.bio}</p>
                )}

                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span className={profile.is_online ? 'text-green-400' : 'text-gray-400'}>
                    {getStatusText()}
                  </span>
                </div>

                {!isOwnProfile && (
                  <button
                    onClick={handleMessage}
                    className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-500/30 transition-all"
                  >
                    <MessageCircle className="w-5 h-5" />
                    Send Message
                  </button>
                )}
              </div>
            </div>
          </motion.div>

          {/* Additional Info */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">Information</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Joined</p>
                  <p className="text-white">{format(new Date(profile.created_at), 'MMMM dd, yyyy')}</p>
                </div>
              </div>

              {profile.additional_usernames && profile.additional_usernames.length > 0 && (
                <div className="flex items-start gap-3">
                  <Mail className="w-5 h-5 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Additional Usernames</p>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {profile.additional_usernames.map((username, index) => (
                        <span key={index} className="px-3 py-1 bg-gray-800/50 text-gray-300 rounded-lg text-sm">
                          {username}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
