import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { User } from 'lucide-react';

interface AvatarProps {
  src?: string | null;
  alt?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  status?: 'online' | 'offline' | 'away';
  onClick?: () => void;
  className?: string;
}

export const Avatar = ({
  src,
  alt = 'User avatar',
  size = 'md',
  status,
  onClick,
  className,
}: AvatarProps) => {
  const sizes = {
    xs: 'w-6 h-6',
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const statusSizes = {
    xs: 'w-1.5 h-1.5',
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
    lg: 'w-3 h-3',
    xl: 'w-4 h-4',
  };

  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-gray-400',
    away: 'bg-yellow-500',
  };

  return (
    <motion.div
      className={clsx('relative inline-block', className)}
      whileHover={onClick ? { scale: 1.05 } : undefined}
      whileTap={onClick ? { scale: 0.95 } : undefined}
    >
      <div
        className={clsx(
          sizes[size],
          'rounded-full overflow-hidden',
          'glass border-2 border-white/20',
          'flex items-center justify-center',
          onClick && 'cursor-pointer'
        )}
        onClick={onClick}
      >
        {src ? (
          <img
            src={src}
            alt={alt}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <User className="w-1/2 h-1/2 text-gray-400" />
        )}
      </div>
      {status && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className={clsx(
            statusSizes[size],
            statusColors[status],
            'absolute bottom-0 right-0',
            'rounded-full border-2 border-white dark:border-gray-900'
          )}
        />
      )}
    </motion.div>
  );
};
