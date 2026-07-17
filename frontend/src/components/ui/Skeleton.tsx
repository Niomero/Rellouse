import { motion } from 'framer-motion'
import { cn } from '../../utils/cn'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded'
  width?: string | number
  height?: string | number
  animate?: boolean
}

export function Skeleton({
  className,
  variant = 'rectangular',
  width,
  height,
  animate = true,
}: SkeletonProps) {
  const baseClasses = 'liquid-skeleton bg-neutral-200 dark:bg-neutral-700'
  
  const variantClasses = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
    rounded: 'rounded-2xl',
  }

  const style: React.CSSProperties = {}
  if (width) style.width = typeof width === 'number' ? `${width}px` : width
  if (height) style.height = typeof height === 'number' ? `${height}px` : height

  const Component = animate ? motion.div : 'div'
  const animationProps = animate
    ? {
        animate: {
          opacity: [0.5, 1, 0.5],
        },
        transition: {
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        },
      }
    : {}

  return (
    <Component
      className={cn(baseClasses, variantClasses[variant], className)}
      style={style}
      {...animationProps}
    />
  )
}

export function MessageSkeleton() {
  return (
    <div className="flex gap-3 p-4">
      <Skeleton variant="circular" width={40} height={40} />
      <div className="flex-1 space-y-2">
        <Skeleton variant="text" width="30%" />
        <Skeleton variant="rounded" width="80%" height={60} />
      </div>
    </div>
  )
}

export function ChatListSkeleton() {
  return (
    <div className="space-y-2 p-4">
      {[...Array(8)].map((_, i) => (
        <div key={i} className="flex gap-3 p-3">
          <Skeleton variant="circular" width={48} height={48} />
          <div className="flex-1 space-y-2">
            <div className="flex justify-between">
              <Skeleton variant="text" width="40%" />
              <Skeleton variant="text" width="15%" />
            </div>
            <Skeleton variant="text" width="70%" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function ProfileSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col items-center gap-4">
        <Skeleton variant="circular" width={120} height={120} />
        <Skeleton variant="text" width="40%" height={24} />
        <Skeleton variant="text" width="30%" height={16} />
      </div>
      
      <div className="space-y-3">
        <Skeleton variant="rounded" height={80} />
        <Skeleton variant="rounded" height={60} />
        <Skeleton variant="rounded" height={60} />
      </div>
    </div>
  )
}

export function ChannelSkeleton() {
  return (
    <div className="space-y-4 p-4">
      <div className="flex gap-3">
        <Skeleton variant="circular" width={60} height={60} />
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" width="50%" height={24} />
          <Skeleton variant="text" width="70%" />
          <Skeleton variant="text" width="30%" />
        </div>
      </div>
      
      <Skeleton variant="rounded" height={100} />
      
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} variant="rounded" height={120} />
        ))}
      </div>
    </div>
  )
}

export function SearchSkeleton() {
  return (
    <div className="space-y-2 p-4">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="flex gap-3 p-3">
          <Skeleton variant="circular" width={48} height={48} />
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" width="40%" />
            <Skeleton variant="text" width="60%" />
          </div>
        </div>
      ))}
    </div>
  )
}