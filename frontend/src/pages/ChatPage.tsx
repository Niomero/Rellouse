import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Send,
  Image as ImageIcon,
  User,
  Bot,
  CheckCircle,
  Loader2,
  X,
} from 'lucide-react'
import { cn } from '../utils/cn'
import { useToast } from '../hooks/useToast'
import { useAuthStore } from '../store/authStore'
import { EmojiPicker } from '../components/EmojiPicker'
import { ImageUpload, ImagePreview } from '../components/ImageUpload'
import { MessageSkeleton } from '../components/ui/Skeleton'
import api from '../services/api'
import { format, isToday, isYesterday } from 'date-fns'

interface Message {
  id: number
  sender_id: number
  recipient_id: number
  content: string
  message_type: string
  is_read: boolean
  created_at: string
  attachments?: MessageAttachment[]
}

interface MessageAttachment {
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

interface ChatUser {
  id: number
  username: string
  display_name: string | null
  avatar_url: string | null
  is_online: boolean
  is_bot: boolean
  is_verified: boolean
}

export default function ChatPage() {
  const { userId } = useParams<{ userId: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuthStore()
  const { error: showError, success: showSuccess } = useToast()
  
  const [chatUser, setChatUser] = useState<ChatUser | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [messageText, setMessageText] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [showImageUpload, setShowImageUpload] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messageInputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (userId) {
      loadChatUser(parseInt(userId))
      loadMessages(parseInt(userId))
    }
  }, [userId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadChatUser = async (id: number) => {
    try {
      const response = await api.get<ChatUser>(`/users/${id}`)
      setChatUser(response.data)
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to load user')
      navigate('/search')
    }
  }

  const loadMessages = async (recipientId: number) => {
    setLoading(true)
    try {
      const response = await api.get<Message[]>('/messages', {
        params: { recipient_id: recipientId, limit: 50 }
      })
      setMessages(response.data.reverse())
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to load messages')
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!messageText.trim() || !userId || sending) return

    const content = messageText.trim()
    setMessageText('')
    setSending(true)

    try {
      const response = await api.post<Message>('/messages', {
        recipient_id: parseInt(userId),
        content,
        message_type: 'text'
      })

      setMessages(prev => [...prev, response.data])
      showSuccess('Message sent')
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to send message')
      setMessageText(content)
    } finally {
      setSending(false)
    }
  }

  const handleImageUpload = async (imageUrl: string, imageData: any) => {
    if (!userId || sending) return

    setSending(true)
    setShowImageUpload(false)

    try {
      const response = await api.post<Message>('/messages', {
        recipient_id: parseInt(userId),
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

      setMessages(prev => [...prev, response.data])
      showSuccess('Image sent')
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to send image')
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleEmojiSelect = (emoji: string) => {
    setMessageText(prev => prev + emoji)
    messageInputRef.current?.focus()
  }

  const formatMessageTime = (dateString: string) => {
    const date = new Date(dateString)
    if (isToday(date)) return format(date, 'HH:mm')
    if (isYesterday(date)) return `Yesterday ${format(date, 'HH:mm')}`
    return format(date, 'MMM d, HH:mm')
  }

  const groupMessagesByDate = (messages: Message[]) => {
    const groups: { [key: string]: Message[] } = {}
    
    messages.forEach(message => {
      const date = new Date(message.created_at)
      let key: string
      
      if (isToday(date)) {
        key = 'Today'
      } else if (isYesterday(date)) {
        key = 'Yesterday'
      } else {
        key = format(date, 'MMMM d, yyyy')
      }
      
      if (!groups[key]) groups[key] = []
      groups[key].push(message)
    })
    
    return groups
  }

  if (!chatUser) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  const messageGroups = groupMessagesByDate(messages)

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="glass border-b border-neutral-200 dark:border-neutral-700 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/chat')}
            className="liquid-btn liquid-hover liquid-press p-2 rounded-xl"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          <div
            onClick={() => navigate(`/profile/${chatUser.id}`)}
            className="flex items-center gap-3 flex-1 cursor-pointer liquid-hover rounded-xl p-2 -m-2"
          >
            <div className="relative flex-shrink-0">
              <div className="liquid-avatar w-10 h-10">
                {chatUser.avatar_url ? (
                  <img
                    src={chatUser.avatar_url}
                    alt={chatUser.display_name || chatUser.username}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                    {chatUser.is_bot ? (
                      <Bot className="w-5 h-5 text-white" />
                    ) : (
                      <User className="w-5 h-5 text-white" />
                    )}
                  </div>
                )}
              </div>
              {chatUser.is_online && !chatUser.is_bot && (
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white dark:border-neutral-900 rounded-full" />
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <h2 className="font-semibold text-neutral-900 dark:text-neutral-100 truncate">
                  {chatUser.display_name || chatUser.username}
                </h2>
                {chatUser.is_verified && (
                  <CheckCircle className="w-4 h-4 text-primary-500 flex-shrink-0" />
                )}
              </div>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                {chatUser.is_online ? 'Online' : 'Offline'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto liquid-scrollbar p-4 space-y-6">
        {loading ? (
          <MessageSkeleton />
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-20 h-20 mb-4 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
              <Send className="w-10 h-10 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
              No messages yet
            </h3>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              Start the conversation by sending a message
            </p>
          </div>
        ) : (
          Object.entries(messageGroups).map(([date, msgs]) => (
            <div key={date} className="space-y-3">
              {/* Date Separator */}
              <div className="flex items-center justify-center">
                <div className="liquid-badge px-3 py-1 text-xs font-medium">
                  {date}
                </div>
              </div>

              {/* Messages */}
              {msgs.map((message, index) => {
                const isSent = message.sender_id === currentUser?.id
                const showAvatar = index === 0 || msgs[index - 1].sender_id !== message.sender_id

                return (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.2 }}
                    className={cn('flex gap-2', isSent ? 'justify-end' : 'justify-start')}
                  >
                    {!isSent && showAvatar && (
                      <div className="liquid-avatar w-8 h-8 flex-shrink-0">
                        {chatUser.avatar_url ? (
                          <img
                            src={chatUser.avatar_url}
                            alt={chatUser.display_name || chatUser.username}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                            {chatUser.is_bot ? (
                              <Bot className="w-4 h-4 text-white" />
                            ) : (
                              <User className="w-4 h-4 text-white" />
                            )}
                          </div>
                        )}
                      </div>
                    )}
                    {!isSent && !showAvatar && <div className="w-8" />}

                    <div className={cn('max-w-[70%] space-y-1', isSent && 'items-end')}>
                      <div
                        className={cn(
                          'liquid-message',
                          isSent ? 'liquid-message-sent' : 'liquid-message-received'
                        )}
                      >
                        {message.message_type === 'image' && message.attachments?.[0] && (
                          <ImagePreview
                            src={message.attachments[0].file_url}
                            alt={message.attachments[0].file_name}
                            className="mb-2 max-w-sm rounded-xl"
                          />
                        )}
                        <p className="text-sm whitespace-pre-wrap break-words">
                          {message.content}
                        </p>
                      </div>
                      <span className="text-xs text-neutral-500 px-2">
                        {formatMessageTime(message.created_at)}
                      </span>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

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
                  Send Image
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

      {/* Message Input */}
      <div className="glass border-t border-neutral-200 dark:border-neutral-700 p-4">
        <div className="flex items-end gap-2">
          <button
            onClick={() => setShowImageUpload(true)}
            className="liquid-btn liquid-hover liquid-press p-3 rounded-xl flex-shrink-0"
            disabled={sending}
          >
            <ImageIcon className="w-5 h-5 text-neutral-600 dark:text-neutral-400" />
          </button>

          <div className="flex-1 glass rounded-2xl p-3 flex items-end gap-2">
            <textarea
              ref={messageInputRef}
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              className="flex-1 bg-transparent outline-none resize-none max-h-32 text-neutral-900 dark:text-neutral-100 placeholder:text-neutral-500"
              rows={1}
              disabled={sending}
            />
            <EmojiPicker onEmojiSelect={handleEmojiSelect} />
          </div>

          <button
            onClick={sendMessage}
            disabled={!messageText.trim() || sending}
            className={cn(
              'liquid-btn-primary p-3 rounded-xl flex-shrink-0 transition-all',
              (!messageText.trim() || sending) && 'opacity-50 cursor-not-allowed'
            )}
          >
            {sending ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}