import { CheckCircle2 } from 'lucide-react'

export type UserRole = 'user' | 'verified' | 'administrator' | 'owner'

interface RoleBadge {
  color: string
  icon: JSX.Element | null
  label: string
}

export const getRoleBadge = (role: UserRole): RoleBadge => {
  switch (role) {
    case 'verified':
      return {
        color: 'text-verified',
        icon: <CheckCircle2 size={16} className="text-verified" />,
        label: 'Verified',
      }
    case 'administrator':
      return {
        color: 'text-admin',
        icon: <CheckCircle2 size={16} className="text-admin" />,
        label: 'Administrator',
      }
    case 'owner':
      return {
        color: 'text-owner',
        icon: <CheckCircle2 size={16} className="text-owner" />,
        label: 'Owner',
      }
    default:
      return {
        color: 'text-gray-900 dark:text-white',
        icon: null,
        label: 'User',
      }
  }
}

export const getRoleColor = (role: UserRole): string => {
  switch (role) {
    case 'verified':
      return 'text-verified'
    case 'administrator':
      return 'text-admin'
    case 'owner':
      return 'text-owner'
    default:
      return 'text-gray-900 dark:text-white'
  }
}
