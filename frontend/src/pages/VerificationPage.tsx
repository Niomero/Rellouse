import { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, Send, CheckCircle, Loader2 } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

const VerificationPage = () => {
  const { user } = useAuthStore()
  const [description, setDescription] = useState('')
  const [telegramLinks, setTelegramLinks] = useState('')
  const [socialLinks, setSocialLinks] = useState('')
  const [websiteLinks, setWebsiteLinks] = useState('')
  const [additionalMaterials, setAdditionalMaterials] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // TODO: Implement API call to submit verification request
    setTimeout(() => {
      setSuccess(true)
      setIsSubmitting(false)
    }, 1000)
  }

  if (user?.role === 'verified' || user?.role === 'administrator' || user?.role === 'owner') {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 p-6">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="glass-card p-12 text-center max-w-md"
        >
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-2xl shadow-indigo-500/30">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-3">
            You're Verified!
          </h1>
          <p className="text-gray-400">
            Your account already has verified status.
          </p>
        </motion.div>
      </div>
    )
  }

  if (success) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 p-6">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="glass-card p-12 text-center max-w-md"
        >
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-green-600 to-emerald-600 flex items-center justify-center shadow-2xl shadow-green-500/30">
            <CheckCircle className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-3">
            Request Submitted!
          </h1>
          <p className="text-gray-400">
            Your verification request has been submitted successfully. Our team will review it soon.
          </p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-900 p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 rounded-xl bg-indigo-500/20">
              <Shield className="w-6 h-6 text-indigo-400" />
            </div>
            <h1 className="text-3xl font-bold gradient-text">Request Verification</h1>
          </div>
          <p className="text-gray-400">
            Submit your verification request to get the verified badge on your profile.
          </p>
        </motion.div>

        {/* Form */}
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          onSubmit={handleSubmit}
          className="glass-card p-8 space-y-6"
        >
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Description *
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Tell us about yourself and why you should be verified..."
              className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent resize-none transition-all"
              rows={4}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Telegram Links
            </label>
            <input
              type="text"
              value={telegramLinks}
              onChange={(e) => setTelegramLinks(e.target.value)}
              placeholder="https://t.me/username"
              className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Social Media Links
            </label>
            <input
              type="text"
              value={socialLinks}
              onChange={(e) => setSocialLinks(e.target.value)}
              placeholder="Twitter, Instagram, etc."
              className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Website Links
            </label>
            <input
              type="text"
              value={websiteLinks}
              onChange={(e) => setWebsiteLinks(e.target.value)}
              placeholder="https://yourwebsite.com"
              className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Additional Materials
            </label>
            <textarea
              value={additionalMaterials}
              onChange={(e) => setAdditionalMaterials(e.target.value)}
              placeholder="Any additional information or links..."
              className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent resize-none transition-all"
              rows={3}
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !description.trim()}
            className="w-full py-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Submit Request
              </>
            )}
          </button>
        </motion.form>
      </div>
    </div>
  )
}

export default VerificationPage