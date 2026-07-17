import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Loader2 } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { Avatar } from '../components/ui/Avatar';
import { Card } from '../components/ui/Card';
import { SkeletonCard } from '../components/ui/Skeleton';
import { UserProfile } from '../components/UserProfile';
import { api } from '../services/api';
import { showToast } from '../utils/toast';
import { useNavigate } from 'react-router-dom';

interface SearchResult {
  id: number;
  username: string;
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  role: string;
  is_verified: boolean;
  is_online: boolean;
  is_bot: boolean;
}

export const SearchPage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [showProfile, setShowProfile] = useState(false);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (query.trim().length >= 2) {
        searchUsers();
      } else {
        setResults([]);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  const searchUsers = async () => {
    setIsLoading(true);
    try {
      const data = await api.searchUsers(query);
      setResults(data);
    } catch (error) {
      showToast.error('Failed to search users');
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUserClick = async (userId: number) => {
    try {
      const userData = await api.getUserProfile(userId);
      setSelectedUser(userData);
      setShowProfile(true);
    } catch (error) {
      showToast.error('Failed to load user profile');
      console.error('Profile error:', error);
    }
  };

  const handleStartChat = (userId: number) => {
    navigate(`/chat/${userId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
      <div className="max-w-2xl mx-auto pt-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Search Users
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Find people by username, name, or login
          </p>
        </motion.div>

        {/* Search Input */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Input
            type="text"
            placeholder="Search by @username, name, or login..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            leftIcon={<Search className="w-5 h-5" />}
            rightIcon={
              query && (
                <button
                  onClick={() => setQuery('')}
                  className="hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full p-1 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )
            }
            className="text-lg"
          />
        </motion.div>

        {/* Results */}
        <div className="mt-6 space-y-3">
          <AnimatePresence mode="wait">
            {isLoading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-3"
              >
                {[1, 2, 3].map((i) => (
                  <SkeletonCard key={i} />
                ))}
              </motion.div>
            ) : results.length > 0 ? (
              <motion.div
                key="results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-3"
              >
                {results.map((user, index) => (
                  <motion.div
                    key={user.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card
                      variant="glass"
                      hover
                      onClick={() => handleUserClick(user.id)}
                      className="cursor-pointer"
                    >
                      <div className="flex items-center gap-4">
                        <Avatar
                          src={user.avatar_url}
                          alt={user.display_name || user.username}
                          size="lg"
                          status={user.is_online ? 'online' : 'offline'}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                              {user.display_name || user.username}
                            </h3>
                            {user.is_verified && (
                              <div className="flex-shrink-0 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                                <svg
                                  className="w-3 h-3 text-white"
                                  fill="currentColor"
                                  viewBox="0 0 20 20"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                              </div>
                            )}
                            {user.is_bot && (
                              <span className="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full">
                                BOT
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {user.username}
                          </p>
                          {user.bio && (
                            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-1">
                              {user.bio}
                            </p>
                          )}
                        </div>
                        <div className="flex-shrink-0">
                          <motion.div
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            className="w-10 h-10 rounded-full glass flex items-center justify-center"
                          >
                            <Search className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                          </motion.div>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </motion.div>
            ) : query.trim().length >= 2 ? (
              <motion.div
                key="no-results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-12"
              >
                <Search className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No users found
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Try searching with a different query
                </p>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-12"
              >
                <Search className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Start searching
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Enter at least 2 characters to search for users
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* User Profile Modal */}
      <AnimatePresence>
        {showProfile && selectedUser && (
          <UserProfile
            user={selectedUser}
            onClose={() => setShowProfile(false)}
            onStartChat={handleStartChat}
          />
        )}
      </AnimatePresence>
    </div>
  );
};