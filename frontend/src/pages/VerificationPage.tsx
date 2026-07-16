import { useState } from 'react'
import { Shield, Send } from 'lucide-react'
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
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
          <Shield size={64} className="mx-auto mb-4 text-verified" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            You're Already Verified!
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Your account has verified status.
          </p>
        </div>
      </div>
    )
  }

  if (success) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 text-center">
          <Shield size={64} className="mx-auto mb-4 text-green-500" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Request Submitted!
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Your verification request has been submitted successfully. Our team will review it soon.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8">
        <div className="flex items-center space-x-3 mb-6">
          <Shield size={32} className="text-verified" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Request Verification
          </h1>
        </div>

        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Submit your verification request to get the verified badge on your profile.
          Please provide detailed information about yourself and your online presence.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description *
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={4}
              placeholder="Tell us about yourself, your work, achievements, etc."
              required
              minLength={50}
              maxLength={2000}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Minimum 50 characters
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Telegram Links
            </label>
            <input
              type="text"
              value={telegramLinks}
              onChange={(e) => setTelegramLinks(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="https://t.me/yourchannel (comma-separated)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Social Media Links
            </label>
            <input
              type="text"
              value={socialLinks}
              onChange={(e) => setSocialLinks(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Twitter, Instagram, etc. (comma-separated)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Website Links
            </label>
            <input
              type="text"
              value={websiteLinks}
              onChange={(e) => setWebsiteLinks(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="https://yourwebsite.com (comma-separated)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Additional Materials
            </label>
            <textarea
              value={additionalMaterials}
              onChange={(e) => setAdditionalMaterials(e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              rows={3}
              placeholder="Any additional information that supports your verification request"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-primary-500 hover:bg-primary-600 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {isSubmitting ? (
              <span>Submitting...</span>
            ) : (
              <>
                <Send size={20} />
                <span>Submit Request</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default VerificationPage
