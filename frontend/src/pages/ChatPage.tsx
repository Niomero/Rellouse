import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Send,
  Image as ImageIcon,
  Smile,
  Paperclip,
  MoreVertical,
  Phone,
  Video,
  Search,
  CheckCheck,
  Check,
  Clock,
} from 'lucide-react'
import { useToast } from '../hooks/useToast'
import { useAuthStore } from '../store/authStore'
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
      const response = await api.get<ChatUser>(`/api/users/${id}`)
      setChatUser(response.data)
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to load user')
      navigate('/search')
    }
  }

  const loadMessages = async (recipientId: number) => {
    setLoading(true)
    try {
      const response = await api.get<Message[]>('/api/messages', {
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
      const response = await api.post<Message>('/api/messages', {
        recipient_id: parseInt(userId),
        content,
        message_type: 'text'
      })

      setMessages(prev => [...prev, response.data])
      scrollToBottom()
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to send message')
      setMessageText(content)
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

  const formatMessageTime = (dateString: string) => {
    const date = new Date(dateString)
    if (isToday(date)) {
      return format(date, 'HH:mm')
    } else if (isYesterday(date)) {
      return `Yesterday ${format(date, 'HH:mm')}`
    } else {
      return format(date, 'MMM dd, HH:mm')
    }
  }

  const groupMessagesByDate = (messages: Message[]) => {
    const groups: { [key: string]: Message[] } = {}
    
    messages.forEach(msg => {
      const date = new Date(msg.created_at)
      let dateKey: string
      
      if (isToday(date)) {
        dateKey = 'Today'
      } else if (isYesterday(date)) {
        dateKey = 'Yesterday'
      } else {
        dateKey = format(date, 'MMMM dd, yyyy')
      }
      
      if (!groups[dateKey]) {
        groups[dateKey] = []
      }
      groups[dateKey].push(msg)
    })
    
    return groups
  }

  if (!userId) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center"
          >
            <Search className="w-12 h-12 text-white" />
          </motion.div>
          <h2 className="text-2xl font-bold text-white mb-2">Select a chat</h2>
          <p className="text-gray-400">Choose a conversation to start messaging</p>
        </div>
      </div>
    )
  }

  const messageGroups = groupMessagesByDate(messages)

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Chat Header */}
      {chatUser && (
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="glass-card border-b border-gray-700/50 px-6 py-4 flex items-center justify-between"
        >
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/chat')}
              className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all lg:hidden"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            
            <div className="relative">
              <div className="w-12 h-12 rounded-xl overflow-hidden"
                   style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' }}>
                {chatUser.avatar_url ? (
                  <img src={chatUser.avatar_url} alt={chatUser.username} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-white font-bold text-lg">
                    {chatUser.username.charAt(1).toUpperCase()}
                  </div>
                )}
              </div>
              {chatUser.is_online && (
                <div className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-gray-900"></div>
              )}
            </div>

            <div>
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                {chatUser.display_name || chatUser.username}
                {chatUser.is_verified && (
                  <CheckCheck className="w-4 h-4 text-indigo-400" />
                )}
              </h2>
              <p className="text-sm text-gray-400">
                {chatUser.is_online ? 'Online' : 'Offline'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button className="p-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all">
              <Phone className="w-5 h-5" />
            </button>
            <button className="p-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all">
              <Video className="w-5 h-5" />
            </button>
            <button className="p-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all">
              <Search className="w-5 h-5" />
            </button>
            <button className="p-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all">
              <MoreVertical className="w-5 h-5" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gray-800/50 flex items-center justify-center">
                <Send className="w-10 h-10 text-gray-600" />
              </div>
              <p className="text-gray-400">No messages yet</p>
              <p className="text-sm text-gray-500 mt-1">Start the conversation!</p>
            </div>
          </div>
        ) : (
          Object.entries(messageGroups).map(([date, msgs]) => (
            <div key={date}>
              {/* Date Divider */}
              <div className="flex items-center justify-center my-6">
                <div className="px-4 py-1.5 rounded-full bg-gray-800/50 border border-gray-700/50">
                  <span className="text-xs font-medium text-gray-400">{date}</span>
                </div>
              </div>

              {/* Messages */}
              <div className="space-y-3">
                {msgs.map((message, index) => {
                  const isSent = message.sender_id === currentUser?.id
                  const showAvatar = index === 0 || msgs[index - 1].sender_id !== message.sender_id

                  return (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex items-end gap-2 ${isSent ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                      {!isSent && showAvatar && (
                        <div className="w-8 h-8 rounded-lg overflow-hidden flex-shrink-0"
                             style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' }}>
                          {chatUser?.avatar_url ? (
                            <img src={chatUser.avatar_url} alt="" className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-white text-xs font-bold">
                              {chatUser?.username.charAt(1).toUpperCase()}
                            </div>
                          )}
                        </div>
                      )}
                      {!isSent && !showAvatar && <div className="w-8" />}

                      <div className={`flex flex-col ${isSent ? 'items-end' : 'items-start'} max-w-[70%]`}>
                        <div
                          className={`px-4 py-2.5 rounded-2xl ${
                            isSent
                              ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
                              : 'glass-card text-white'
                          } ${isSent ? 'rounded-br-sm' : 'rounded-bl-sm'}`}
                        >
                          <p className="text-sm leading-relaxed break-words">{message.content}</p>
                        </div>
                        
                        <div className="flex items-center gap-1.5 mt-1 px-1">
                          <span className="text-xs text-gray-500">
                            {formatMessageTime(message.created_at)}
                          </span>
                          {isSent && (
                            message.is_read ? (
                              <CheckCheck className="w-3.5 h-3.5 text-indigo-400" />
                            ) : (
                              <Check className="w-3.5 h-3.5 text-gray-500" />
                            )
                          )}
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="glass-card border-t border-gray-700/50 px-6 py-4"
      >
        <div className="flex items-end gap-3">
          <button className="p-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all">
            <Paperclip className="w-5 h-5" />
          </button>
          
          <button className="p-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all">
            <ImageIcon className="w-5 h-5" />
          </button>

          <div className="flex-1 relative">
            <textarea
              ref={messageInputRef}
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message..."
              rows={1}
              className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent resize-none transition-all"
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>

          <button className="p-2.5 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all">
            <Smile className="w-5 h-5" />
          </button>

          <button
            onClick={sendMessage}
            disabled={!messageText.trim() || sending}
            className="p-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-indigo-500/30"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </motion.div>
    </div>
  )
}
