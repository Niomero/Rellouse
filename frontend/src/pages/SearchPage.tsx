import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search, User, Bot, CheckCircle, MessageCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../hooks/useToast'
import { SearchSkeleton } from '../components/ui/Skeleton'
import api from '../services/api'

interface SearchUser {
  id: number
  username: string
  display_name: string | null
  avatar_url: string | null
  bio: string | null
  role: string
  is_verified: boolean
  is_online: boolean
  is_bot: boolean
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchUser[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const navigate = useNavigate()
  const { error: showError } = useToast()

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (query.trim().length >= 2) {
        searchUsers(query.trim())
      } else {
        setResults([])
        setSearched(false)
      }
    }, 300)

    return () => clearTimeout(delayDebounceFn)
  }, [query])

  const searchUsers = async (searchQuery: string) => {
    setLoading(true)
    setSearched(true)
    
    try {
      const response = await api.get<SearchUser[]>('/api/users/search', {
        params: { query: searchQuery, limit: 20 }
      })
      setResults(response.data)
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Failed to search users')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleUserClick = (userId: number) => {
    navigate(`/profile/${userId}`)
  }

  const handleMessageClick = (userId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    navigate(`/chat/${userId}`)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Search Header */}
      <div className="glass border-b border-neutral-200 dark:border-neutral-700 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by username, @username, or name..."
              className="liquid-input pl-12 pr-4 py-3 text-base"
              autoFocus
            />
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto liquid-scrollbar">
        <div className="max-w-2xl mx-auto p-4">
          {loading ? (
            <SearchSkeleton />
          ) : searched && results.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-neutral-200 to-neutral-300 dark:from-neutral-700 dark:to-neutral-800 flex items-center justify-center">
                <Search className="w-10 h-10 text-neutral-500" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
                No users found
              </h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Try searching with a different username or name
              </p>
            </motion.div>
          ) : !searched ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
                <Search className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
                Search for users
              </h3>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                Enter a username, @username, or name to find people
              </p>
            </motion.div>
          ) : (
            <div className="space-y-2">
              {results.map((user, index) => (
                <motion.div
                  key={user.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => handleUserClick(user.id)}
                  className="glass liquid-hover liquid-press rounded-2xl p-4 cursor-pointer"
                >
                  <div className="flex items-center gap-4">
                    {/* Avatar */}
                    <div className="relative flex-shrink-0">
                      <div className="liquid-avatar w-14 h-14">
                        {user.avatar_url ? (
                          <img
                            src={user.avatar_url}
                            alt={user.display_name || user.username}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                            {user.is_bot ? (
                              <Bot className="w-7 h-7 text-white" />
                            ) : (
                              <User className="w-7 h-7 text-white" />
                            )}
                          </div>
                        )}
                      </div>
                      {user.is_online && !user.is_bot && (
                        <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-white dark:border-neutral-900 rounded-full" />
                      )}
                    </div>

                    {/* User Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 truncate">
                          {user.display_name || user.username}
                        </h3>
                        {user.is_verified && (
                          <CheckCircle className="w-4 h-4 text-primary-500 flex-shrink-0" />
                        )}
                        {user.is_bot && (
                          <span className="liquid-badge liquid-badge-primary text-xs px-2 py-0.5">
                            BOT
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-neutral-600 dark:text-neutral-400 truncate">
                        {user.username}
                      </p>
                      {user.bio && (
                        <p className="text-sm text-neutral-500 dark:text-neutral-500 truncate mt-1">
                          {user.bio}
                        </p>
                      )}
                    </div>

                    {/* Message Button */}
                    <button
                      onClick={(e) => handleMessageClick(user.id, e)}
                      className="liquid-btn-primary p-3 rounded-xl flex-shrink-0"
                      aria-label="Send message"
                    >
                      <MessageCircle className="w-5 h-5" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
