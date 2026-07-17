import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Hash, Lock, Upload, Loader2 } from 'lucide-react'
import { cn } from '../utils/cn'
import { useToast } from '../hooks/useToast'
import api from '../services/api'

interface CreateChannelForm {
  name: string
  description: string
  avatar_url: string
  channel_type: 'public' | 'private'
  username: string
}

export default function CreateChannelPage() {
  const navigate = useNavigate()
  const { error: showError, success: showSuccess } = useToast()
  const [loading, setLoading] = useState(false)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)
  const [form, setForm] = useState<CreateChannelForm>({
    name: '',
    description: '',
    avatar_url: '',
    channel_type: 'public',
    username: '',
  })

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      showError('Please upload an image file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      showError('Image size must be less than 10MB')
      return
    }

    setUploadingAvatar(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/api/upload/avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setForm(prev => ({ ...prev, avatar_url: response.data.file_url }))
      showSuccess('Avatar uploaded')
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to upload avatar')
    } finally {
      setUploadingAvatar(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!form.name.trim()) {
      showError('Channel name is required')
      return
    }

    if (form.channel_type === 'public' && !form.username.trim()) {
      showError('Username is required for public channels')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/api/channels', {
        name: form.name.trim(),
        description: form.description.trim() || null,
        avatar_url: form.avatar_url || null,
        channel_type: form.channel_type,
        username: form.channel_type === 'public' ? form.username.trim() : null,
      })

      showSuccess('Channel created successfully')
      navigate(`/channels/${response.data.id}`)
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to create channel')
    } finally {
      setLoading(false)
    }
  }

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
            Create Channel
          </h1>
          <div className="w-10" />
        </div>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-y-auto liquid-scrollbar">
        <div className="max-w-2xl mx-auto p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Avatar Upload */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-2xl p-6"
            >
              <label className="block text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-4">
                Channel Avatar
              </label>
              <div className="flex items-center gap-4">
                <div className="liquid-avatar w-20 h-20">
                  {form.avatar_url ? (
                    <img
                      src={form.avatar_url}
                      alt="Channel avatar"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                      <Hash className="w-10 h-10 text-white" />
                    </div>
                  )}
                </div>
                <label className="liquid-btn liquid-hover liquid-press px-4 py-2 rounded-xl cursor-pointer">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                    disabled={uploadingAvatar}
                  />
                  {uploadingAvatar ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <div className="flex items-center gap-2">
                      <Upload className="w-5 h-5" />
                      <span>Upload</span>
                    </div>
                  )}
                </label>
              </div>
            </motion.div>

            {/* Channel Type */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <label className="block text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-4">
                Channel Type
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setForm(prev => ({ ...prev, channel_type: 'public' }))}
                  className={cn(
                    'liquid-btn liquid-hover liquid-press p-4 rounded-xl transition-all',
                    form.channel_type === 'public' && 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  )}
                >
                  <Hash className="w-6 h-6 mx-auto mb-2 text-primary-500" />
                  <div className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                    Public
                  </div>
                  <div className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                    Anyone can find and join
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setForm(prev => ({ ...prev, channel_type: 'private' }))}
                  className={cn(
                    'liquid-btn liquid-hover liquid-press p-4 rounded-xl transition-all',
                    form.channel_type === 'private' && 'ring-2 ring-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  )}
                >
                  <Lock className="w-6 h-6 mx-auto mb-2 text-primary-500" />
                  <div className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                    Private
                  </div>
                  <div className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
                    Join by invite link only
                  </div>
                </button>
              </div>
            </motion.div>

            {/* Channel Name */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-2xl p-6"
            >
              <label className="block text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                Channel Name *
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="My Awesome Channel"
                className="liquid-input"
                maxLength={255}
                required
              />
            </motion.div>

            {/* Username (Public only) */}
            {form.channel_type === 'public' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="glass rounded-2xl p-6"
              >
                <label className="block text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                  Username *
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-500">
                    @
                  </span>
                  <input
                    type="text"
                    value={form.username}
                    onChange={(e) => setForm(prev => ({ ...prev, username: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '') }))}
                    placeholder="mychannel"
                    className="liquid-input pl-8"
                    minLength={5}
                    maxLength={16}
                    pattern="[a-z0-9_]+"
                    required
                  />
                </div>
                <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-2">
                  5-16 characters, lowercase letters, numbers, and underscores only
                </p>
              </motion.div>
            )}

            {/* Description */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="glass rounded-2xl p-6"
            >
              <label className="block text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3">
                Description
              </label>
              <textarea
                value={form.description}
                onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Tell people what your channel is about..."
                className="liquid-input resize-none"
                rows={4}
                maxLength={500}
              />
              <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-2">
                {form.description.length}/500 characters
              </p>
            </motion.div>

            {/* Submit Button */}
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              type="submit"
              disabled={loading || uploadingAvatar}
              className={cn(
                'liquid-btn-primary w-full rounded-xl px-6 py-4 font-medium text-base',
                (loading || uploadingAvatar) && 'opacity-50 cursor-not-allowed'
              )}
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Creating Channel...</span>
                </div>
              ) : (
                'Create Channel'
              )}
            </motion.button>
          </form>
        </div>
      </div>
    </div>
  )
}
