import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

interface User {
  id: number
  username: string
  role: 'user' | 'verified' | 'administrator' | 'owner'
  avatar_url?: string
  bio?: string
  additional_usernames?: string[]
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (login: string, password: string) => Promise<void>
  register: (login: string, password: string, username: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
  refreshAccessToken: () => Promise<void>
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (login: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/api/auth/login', { login, password })
          const { access_token, refresh_token, user } = response.data
          
          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          })
          
          // Store tokens in localStorage
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
        } catch (error: any) {
          set({ isLoading: false })
          throw new Error(error.response?.data?.detail || 'Login failed')
        }
      },

      register: async (login: string, password: string, username: string) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/api/auth/register', {
            login,
            password,
            username,
          })
          const { access_token, refresh_token, user } = response.data
          
          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
          })
          
          // Store tokens in localStorage
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
        } catch (error: any) {
          set({ isLoading: false })
          throw new Error(error.response?.data?.detail || 'Registration failed')
        }
      },

      logout: async () => {
        const { accessToken } = get()
        
        try {
          if (accessToken) {
            await api.post('/api/auth/logout')
          }
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          })
          
          // Remove tokens from localStorage
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      },

      checkAuth: async () => {
        const { accessToken, refreshToken } = get()
        
        if (!accessToken) {
          set({ isAuthenticated: false })
          return
        }
        
        try {
          const response = await api.get('/api/auth/me')
          
          set({
            user: response.data,
            isAuthenticated: true,
          })
        } catch (error) {
          // Token invalid, clear auth state
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          })
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get()
        
        if (!refreshToken) {
          set({ isAuthenticated: false })
          return
        }
        
        try {
          const response = await api.post('/api/auth/refresh', {
            refresh_token: refreshToken,
          })
          
          const { access_token } = response.data
          
          set({ accessToken: access_token })
          localStorage.setItem('access_token', access_token)
          
          // Re-check auth
          await get().checkAuth()
        } catch (error) {
          // Refresh failed, logout
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          })
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      },

      updateUser: (userData: Partial<User>) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        }))
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
)
