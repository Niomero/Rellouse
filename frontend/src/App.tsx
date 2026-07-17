import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { useThemeStore } from './store/themeStore'
import { useToast } from './hooks/useToast'
import { useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'

// Pages
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ChatPage from './pages/ChatPage'
import ProfilePage from './pages/ProfilePage'
import SearchPage from './pages/SearchPage'
import VerificationPage from './pages/VerificationPage'
import SettingsPage from './pages/SettingsPage'
import ChannelPage from './pages/ChannelPage'
import CreateChannelPage from './pages/CreateChannelPage'

// Components
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import { ToastContainer } from './components/ui/Toast'

// Styles
import './styles/liquid-glass.css'

function App() {
  const { isAuthenticated, checkAuth } = useAuthStore()
  const { theme } = useThemeStore()
  const { toasts, removeToast } = useToast()

  useEffect(() => {
    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  useEffect(() => {
    // Check authentication on mount
    checkAuth()
  }, [checkAuth])

  return (
    <>
      <Router>
        <AnimatePresence mode="wait">
          <Routes>
            {/* Public routes */}
            <Route
              path="/login"
              element={
                isAuthenticated ? <Navigate to="/chat" replace /> : <LoginPage />
              }
            />
            <Route
              path="/register"
              element={
                isAuthenticated ? <Navigate to="/chat" replace /> : <RegisterPage />
              }
            />

            {/* Protected routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/chat" replace />} />
              <Route path="chat" element={<ChatPage />} />
              <Route path="chat/:userId" element={<ChatPage />} />
              <Route path="profile/:userId" element={<ProfilePage />} />
              <Route path="search" element={<SearchPage />} />
              <Route path="verification" element={<VerificationPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="channels/create" element={<CreateChannelPage />} />
              <Route path="channels/:channelId" element={<ChannelPage />} />
            </Route>

            {/* 404 */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AnimatePresence>
      </Router>

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </>
  )
}

export default App