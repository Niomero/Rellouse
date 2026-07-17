import { motion } from 'framer-motion';
import { X, MessageCircle, Shield, CheckCircle, Bot } from 'lucide-react';
import { Avatar } from './ui/Avatar';
import { Button } from './ui/Button';
import { Card } from './ui/Card';
import { formatDistanceToNow } from 'date-fns';

interface UserProfileProps {
  user: {
    id: number;
    username: string;
    display_name?: string;
    avatar_url?: string;
    bio?: string;
    role: string;
    is_verified: boolean;
    is_online: boolean;
    is_bot: boolean;
    last_seen?: string;
    created_at: string;
  };
  onClose: () => void;
  onStartChat: (userId: number) => void;
}

export const UserProfile = ({ user, onClose, onStartChat }: UserProfileProps) => {
  const getRoleBadge = () => {
    if (user.role === 'owner') {
      return (
        <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-medium">
          <Shield className="w-3 h-3" />
          Owner
        </div>
      );
    }
    if (user.role === 'administrator') {
      return (
        <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xs font-medium">
          <Shield className="w-3 h-3" />
          Admin
        </div>
      );
    }
    if (user.is_verified) {
      return (
        <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-blue-500 text-white text-xs font-medium">
          <CheckCircle className="w-3 h-3" />
          Verified
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-md"
      >
        <Card variant="glass" padding="none" className="overflow-hidden">
          {/* Header */}
          <div className="relative h-32 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500">
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-2 rounded-full glass hover:bg-white/20 transition-colors"
            >
              <X className="w-5 h-5 text-white" />
            </button>
          </div>

          {/* Profile Content */}
          <div className="p-6 -mt-16">
            <div className="flex flex-col items-center">
              {/* Avatar */}
              <Avatar
                src={user.avatar_url}
                alt={user.display_name || user.username}
                size="xl"
                status={user.is_online ? 'online' : 'offline'}
                className="ring-4 ring-white dark:ring-gray-900"
              />

              {/* Name & Username */}
              <div className="mt-4 text-center">
                <div className="flex items-center justify-center gap-2">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {user.display_name || user.username}
                  </h2>
                  {user.is_bot && (
                    <Bot className="w-5 h-5 text-blue-500" />
                  )}
                </div>
                <p className="text-gray-500 dark:text-gray-400 mt-1">
                  {user.username}
                </p>
              </div>

              {/* Badges */}
              <div className="flex gap-2 mt-3">
                {getRoleBadge()}
              </div>

              {/* Bio */}
              {user.bio && (
                <p className="mt-4 text-center text-gray-600 dark:text-gray-300 max-w-sm">
                  {user.bio}
                </p>
              )}

              {/* Status */}
              <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
                {user.is_online ? (
                  <span className="text-green-500 font-medium">Online</span>
                ) : user.last_seen ? (
                  <span>
                    Last seen {formatDistanceToNow(new Date(user.last_seen), { addSuffix: true })}
                  </span>
                ) : (
                  <span>Offline</span>
                )}
              </div>

              {/* Member Since */}
              <div className="mt-2 text-xs text-gray-400">
                Member since {new Date(user.created_at).toLocaleDateString()}
              </div>

              {/* Actions */}
              <div className="mt-6 w-full">
                <Button
                  variant="primary"
                  className="w-full"
                  leftIcon={<MessageCircle className="w-5 h-5" />}
                  onClick={() => {
                    onStartChat(user.id);
                    onClose();
                  }}
                >
                  Send Message
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
};
