import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Hash,
  Users,
  Settings,
  Send,
  Image as ImageIcon,
  Loader2,
  UserPlus,
  Copy,
  CheckCircle,
  X,
} from 'lucide-react'
import { cn } from '../utils/cn'
import { useToast } from '../hooks/useToast'
import { useAuthStore } from '../store/authStore'
import { EmojiPicker } from '../components/EmojiPicker'
import { ImageUpload, ImagePreview } from '../components/ImageUpload'
import { ChannelSkeleton } from '../components/ui/Skeleton'
import api from '../services/api'
import { format } from 'date-fns'

interface Channel {
  id: number
  name: string
  username: string | null
  description: string | null
  avatar_url: string | null
  channel_type: string
  invite_link: string | null
  owner_id: number
  member_count: number
  is_member: boolean
  member_role: string | null
  created_at: string
  updated_at: string
}

interface ChannelPost {
  id: number
  channel_id: number
  author_id: number
  author_username: string
  author_display_name: string | null
  author_avatar_url: string | null
  content: string
  message_type: string
  attachments: PostAttachment[]
  created_at: string
  edited_at: string | null
}

interface PostAttachment {
  id: number
  file_url: string
  file_name: string
  file_size: number
  file_type: string
  attachment_type: string
  thumbnail_url?: string
  width?: number
  height?: number
}

interface ChannelMember {
  id: number
  username: string
  display_name: string | null
  avatar_url: string | null
  role: string
  is_online: boolean
  joined_at: string
}

export default function ChannelPage() {
  const { channelId } = useParams<{ channelId: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuthStore()
  const { error: showError, success: showSuccess } = useToast()

  const [channel, setChannel] = useState<Channel | null>(null)
  const [posts, setPosts] = useState<ChannelPost[]>([])
  const [members, setMembers] = useState<ChannelMember[]>([])
  const [loading, setLoading] = useState(true)
  const [posting, setPosting] = useState(false)
  const [postText, setPostText] = useState('')
  const [showImageUpload, setShowImageUpload] = useState(false)
  const [showMembers, setShowMembers] = useState(false)
  const [showInvite, setShowInvite] = useState(false)

  const postsEndRef = useRef<HTMLDivElement>(null)
  const postInputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (channelId) {
      loadChannel(parseInt(channelId))
      loadPosts(parseInt(channelId))
    }
  }, [channelId])

  useEffect(() => {
    scrollToBottom()
  }, [posts])

  const scrollToBottom = () => {
    postsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadChannel = async (id: number) => {
    setLoading(true)
    try {
      const response = await api.get<Channel>(`/channels/${id}`)
      setChannel(response.data)
      
      if (response.data.is_member) {
        loadMembers(id)
      }
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to load channel')
      navigate('/chat')
    } finally {
      setLoading(false)
    }
  }

  const loadPosts = async (id: number) => {
    try {
      const response = await api.get<ChannelPost[]>(`/channels/${id}/posts`, {
        params: { limit: 50 }
      })
      setPosts(response.data.reverse())
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to load posts')
    }
  }

  const loadMembers = async (id: number) => {
    try {
      const response = await api.get<ChannelMember[]>(`/channels/${id}/members`, {
        params: { limit: 100 }
      })
      setMembers(response.data)
    } catch (error: any) {
      console.error('Failed to load members:', error)
    }
  }

  const handleJoinChannel = async () => {
    if (!channelId) return

    try {
      await api.post(`/channels/${channelId}/join`)
      showSuccess('Joined channel successfully')
      loadChannel(parseInt(channelId))
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to join channel')
    }
  }

  const handleLeaveChannel = async () => {
    if (!channelId) return

    try {
      await api.post(`/channels/${channelId}/leave`)
      showSuccess('Left channel successfully')
      navigate('/chat')
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to leave channel')
    }
  }

  const createPost = async () => {
    if (!postText.trim() || !channelId || posting) return

    const content = postText.trim()
    setPostText('')
    setPosting(true)

    try {
      const response = await api.post<ChannelPost>(`/channels/${channelId}/posts`, {
        content,
        message_type: 'text'
      })

      setPosts(prev => [...prev, response.data])
      showSuccess('Post published')
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to publish post')
      setPostText(content)
    } finally {
      setPosting(false)
    }
  }

  const handleImageUpload = async (imageUrl: string, imageData: any) => {
    if (!channelId || posting) return

    setPosting(true)
    setShowImageUpload(false)

    try {
      const response = await api.post<ChannelPost>(`/channels/${channelId}/posts`, {
        content: imageData.fileName,
        message_type: 'image',
        attachment: {
          file_url: imageUrl,
          file_name: imageData.fileName,
          file_size: imageData.fileSize,
          file_type: imageData.fileType,
          attachment_type: 'image',
          thumbnail_url: imageData.thumbnailUrl,
          width: imageData.width,
          height: imageData.height,
        }
      })

      setPosts(prev => [...prev, response.data])
      showSuccess('Image posted')
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to post image')
    } finally {
      setPosting(false)
    }
  }

  const handleEmojiSelect = (emoji: string) => {
    setPostText(prev => prev + emoji)
    postInputRef.current?.focus()
  }

  const copyInviteLink = () => {
    if (channel?.invite_link) {
      const fullLink = `${window.location.origin}/channels/join/${channel.invite_link}`
      navigator.clipboard.writeText(fullLink)
      showSuccess('Invite link copied')
    }
  }

  const canPost = channel?.is_member && (channel?.member_role === 'owner' || channel?.member_role === 'admin')

  if (loading) {
    return <ChannelSkeleton />
  }

  if (!channel) return null

  return (
    <div className="flex flex-col h-full">
      {/* Channel Header */}
      <div className="glass border-b border-neutral-200 dark:border-neutral-700 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/chat')}
            className="liquid-btn liquid-hover liquid-press p-2 rounded-xl"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="liquid-avatar w-10 h-10 flex-shrink-0">
              {channel.avatar_url ? (
                <img
                  src={channel.avatar_url}
                  alt={channel.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                  <Hash className="w-5 h-5 text-white" />
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <h2 className="font-semibold text-neutral-900 dark:text-neutral-100 truncate">
                {channel.name}
              </h2>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                {channel.member_count} {channel.member_count === 1 ? 'member' : 'members'}
              </p>
            </div>
          </div>

          {channel.is_member && (
            <button
              onClick={() => setShowMembers(true)}
              className="liquid-btn liquid-hover liquid-press p-2 rounded-xl"
            >
              <Users className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Channel Info */}
      {!channel.is_member && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass border-b border-neutral-200 dark:border-neutral-700 p-6"
        >
          <div className="max-w-2xl mx-auto text-center space-y-4">
            <div className="liquid-avatar w-24 h-24 mx-auto">
              {channel.avatar_url ? (
                <img src={channel.avatar_url} alt={channel.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                  <Hash className="w-12 h-12 text-white" />
                </div>
              )}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
                {channel.name}
              </h1>
              {channel.username && (
                <p className="text-neutral-600 dark:text-neutral-400">{channel.username}</p>
              )}
            </div>
            {channel.description && (
              <p className="text-neutral-700 dark:text-neutral-300">{channel.description}</p>
            )}
            <button
              onClick={handleJoinChannel}
              className="liquid-btn-primary px-8 py-3 rounded-xl font-medium"
            >
              <UserPlus className="w-5 h-5 inline mr-2" />
              Join Channel
            </button>
          </div>
        </motion.div>
      )}

      {/* Posts */}
      <div className="flex-1 overflow-y-auto liquid-scrollbar p-4">
        {channel.is_member ? (
          posts.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 mb-4 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                <Hash className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
                No posts yet
              </h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                {canPost ? 'Be the first to post in this channel' : 'Check back later for new posts'}
              </p>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-4">
              {posts.map((post) => (
                <motion.div
                  key={post.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass rounded-2xl p-6"
                >
                  <div className="flex gap-3 mb-4">
                    <div className="liquid-avatar w-10 h-10 flex-shrink-0">
                      {post.author_avatar_url ? (
                        <img
                          src={post.author_avatar_url}
                          alt={post.author_display_name || post.author_username}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold">
                          {(post.author_display_name || post.author_username).charAt(0).toUpperCase()}
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-neutral-900 dark:text-neutral-100">
                          {post.author_display_name || post.author_username}
                        </span>
                        <span className="text-sm text-neutral-500">
                          {format(new Date(post.created_at), 'MMM d, HH:mm')}
                        </span>
                      </div>
                      <span className="text-sm text-neutral-600 dark:text-neutral-400">
                        {post.author_username}
                      </span>
                    </div>
                  </div>

                  {post.message_type === 'image' && post.attachments[0] && (
                    <ImagePreview
                      src={post.attachments[0].file_url}
                      alt={post.attachments[0].file_name}
                      className="mb-3 rounded-xl max-h-96"
                    />
                  )}

                  <p className="text-neutral-900 dark:text-neutral-100 whitespace-pre-wrap break-words">
                    {post.content}
                  </p>
                </motion.div>
              ))}
              <div ref={postsEndRef} />
            </div>
          )
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-neutral-600 dark:text-neutral-400">
              Join the channel to see posts
            </p>
          </div>
        )}
      </div>

      {/* Post Input (Admin/Owner only) */}
      {canPost && (
        <div className="glass border-t border-neutral-200 dark:border-neutral-700 p-4">
          <div className="max-w-3xl mx-auto flex items-end gap-2">
            <button
              onClick={() => setShowImageUpload(true)}
              className="liquid-btn liquid-hover liquid-press p-3 rounded-xl flex-shrink-0"
              disabled={posting}
            >
              <ImageIcon className="w-5 h-5 text-neutral-600 dark:text-neutral-400" />
            </button>

            <div className="flex-1 glass rounded-2xl p-3 flex items-end gap-2">
              <textarea
                ref={postInputRef}
                value={postText}
                onChange={(e) => setPostText(e.target.value)}
                placeholder="Write a post..."
                className="flex-1 bg-transparent outline-none resize-none max-h-32 text-neutral-900 dark:text-neutral-100 placeholder:text-neutral-500"
                rows={1}
                disabled={posting}
              />
              <EmojiPicker onEmojiSelect={handleEmojiSelect} />
            </div>

            <button
              onClick={createPost}
              disabled={!postText.trim() || posting}
              className={cn(
                'liquid-btn-primary p-3 rounded-xl flex-shrink-0 transition-all',
                (!postText.trim() || posting) && 'opacity-50 cursor-not-allowed'
              )}
            >
              {posting ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      )}

      {/* Image Upload Modal */}
      <AnimatePresence>
        {showImageUpload && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="liquid-modal-backdrop fixed inset-0 flex items-center justify-center p-4 z-50"
            onClick={() => setShowImageUpload(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="liquid-modal p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                  Post Image
                </h3>
                <button
                  onClick={() => setShowImageUpload(false)}
                  className="liquid-btn p-2 rounded-xl"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <ImageUpload
                onUpload={handleImageUpload}
                onCancel={() => setShowImageUpload(false)}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Members Modal */}
      <AnimatePresence>
        {showMembers && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="liquid-modal-backdrop fixed inset-0 flex items-center justify-center p-4 z-50"
            onClick={() => setShowMembers(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="liquid-modal p-6 max-h-[80vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                  Members ({members.length})
                </h3>
                <button
                  onClick={() => setShowMembers(false)}
                  className="liquid-btn p-2 rounded-xl"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="space-y-2">
                {members.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center gap-3 p-3 glass rounded-xl"
                  >
                    <div className="liquid-avatar w-10 h-10 relative">
                      {member.avatar_url ? (
                        <img
                          src={member.avatar_url}
                          alt={member.display_name || member.username}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold">
                          {(member.display_name || member.username).charAt(0).toUpperCase()}
                        </div>
                      )}
                      {member.is_online && (
                        <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white dark:border-neutral-900 rounded-full" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-neutral-900 dark:text-neutral-100 truncate">
                        {member.display_name || member.username}
                      </div>
                      <div className="text-sm text-neutral-600 dark:text-neutral-400 truncate">
                        {member.username}
                      </div>
                    </div>
                    {member.role !== 'member' && (
                      <span className="liquid-badge liquid-badge-primary text-xs px-2 py-1">
                        {member.role.toUpperCase()}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
