import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, User, Bot, CheckCircle, MessageCircle, Loader2, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../hooks/useToast'
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
    navigate(`/chat/${userId}`)
  }

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Search Header */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="glass-card border-b border-gray-700/50 p-6"
      >
        <div className="max-w-3xl mx-auto">
          <h1 className="text-2xl font-bold gradient-text mb-4">Search Users</h1>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by username or @username..."
              className="w-full pl-12 pr-4 py-3.5 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent transition-all text-base"
              autoFocus
            />
          </div>
        </div>
      </motion.div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto">
          {!searched && !loading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-20"
            >
              <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-2xl shadow-indigo-500/30">
                <Users className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Find People</h2>
              <p className="text-gray-400 max-w-md mx-auto">
                Search for users by their username or @username to start chatting
              </p>
            </motion.div>
          )}

          {loading && (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="glass-card p-4 animate-pulse">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-xl bg-gray-700/50"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-700/50 rounded w-1/3"></div>
                      <div className="h-3 bg-gray-700/50 rounded w-1/2"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {searched && !loading && results.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-20"
            >
              <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gray-800/50 flex items-center justify-center">
                <Search className="w-10 h-10 text-gray-600" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">No users found</h3>
              <p className="text-gray-400">Try searching with a different username</p>
            </motion.div>
          )}

          {searched && !loading && results.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-3"
            >
              <p className="text-sm text-gray-400 mb-4">
                Found {results.length} {results.length === 1 ? 'user' : 'users'}
              </p>
              
              <AnimatePresence>
                {results.map((user, index) => (
                  <motion.div
                    key={user.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => handleUserClick(user.id)}
                    className="glass-card p-4 hover:bg-gray-800/60 transition-all cursor-pointer group"
                  >
                    <div className="flex items-center gap-4">
                      {/* Avatar */}
                      <div className="relative flex-shrink-0">
                        <div className="w-14 h-14 rounded-xl overflow-hidden"
                             style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' }}>
                          {user.avatar_url ? (
                            <img src={user.avatar_url} alt={user.username} className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-white font-bold text-xl">
                              {user.username.charAt(1).toUpperCase()}
                            </div>
                          )}
                        </div>
                        {user.is_online && (
                          <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 rounded-full border-2 border-gray-900"></div>
                        )}
                      </div>

                      {/* User Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-base font-semibold text-white truncate">
                            {user.display_name || user.username}
                          </h3>
                          {user.is_verified && (
                            <CheckCircle className="w-4 h-4 text-indigo-400 flex-shrink-0" />
                          )}
                          {user.is_bot && (
                            <span className="px-2 py-0.5 text-xs font-semibold bg-purple-500/20 text-purple-400 rounded-full flex-shrink-0">
                              BOT
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-400 truncate">{user.username}</p>
                        {user.bio && (
                          <p className="text-sm text-gray-500 mt-1 line-clamp-1">{user.bio}</p>
                        )}
                      </div>

                      {/* Action Button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleUserClick(user.id)
                        }}
                        className="p-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500 transition-all shadow-lg shadow-indigo-500/30 opacity-0 group-hover:opacity-100"
                      >
                        <MessageCircle className="w-5 h-5" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}