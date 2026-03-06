'use client'

import { Suspense } from 'react'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { motion } from 'framer-motion'
import UserDetailsStep from '@/components/onboarding/UserDetailsStep'
import PreferencesStep from '@/components/onboarding/PreferencesStep'
import { useAnalytics } from '@/hooks/useAnalytics'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL

export default function EditProfile() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 py-12 px-4 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    }>
      <EditProfileContent />
    </Suspense>
  )
}

function EditProfileContent() {
  const router = useRouter()
  const { data: session } = useSession()
  const { trackEvent } = useAnalytics()
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  const [formData, setFormData] = useState({
    phone: '',
    state: '',
    city: '',
    age_group: '',
    preferred_parties: [] as string[],
    topics_of_interest: [] as string[]
  })

  // Fetch current user data
  useEffect(() => {
    const fetchUserData = async () => {
      if (!session?.user?.id) {
        setFetching(false)
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/users/${session.user.id}`)
        if (response.ok) {
          const result = await response.json()
          const user = result.data

          setFormData({
            phone: user.phone || '',
            state: user.state || '',
            city: user.city || '',
            age_group: user.age_group || '',
            preferred_parties: user.preferred_parties || [],
            topics_of_interest: user.topics_of_interest || []
          })
        }
      } catch (error) {
        console.error('Failed to fetch user data:', error)
      } finally {
        setFetching(false)
      }
    }

    fetchUserData()
  }, [session])

  const updateField = (field: string, value: string | string[]) => {
    setFormData({
      ...formData,
      [field]: value
    })
  }

  const handleSubmit = async () => {
    setLoading(true)
    trackEvent('profile_update_submit', {})
    try {
      if (!session?.user?.id) {
        alert('Please sign in to update your profile')
        return
      }

      const response = await fetch(`${API_BASE_URL}/users/${session.user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: formData.phone,
          state: formData.state,
          city: formData.city,
          age_group: formData.age_group,
          preferred_parties: formData.preferred_parties,
          topics_of_interest: formData.topics_of_interest
        })
      })

      if (response.ok) {
        trackEvent('profile_update_success', {})
        alert('Profile updated successfully!')
        router.push('/dashboard')
      } else {
        const error = await response.json()
        trackEvent('profile_update_error', { error_message: error.error || 'Unknown error' })
        alert(error.error || 'Failed to update profile')
      }
    } catch (error) {
      console.error('Profile update failed:', error)
      trackEvent('profile_update_error', { error_message: 'Network error' })
      alert('Failed to update profile. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 py-12 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 py-12 px-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Edit Profile</h1>
          <p className="text-gray-600">Update your personal information and preferences</p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-white rounded-2xl shadow-xl p-8 border border-orange-100 space-y-8">
          {/* Basic Details Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Details</h2>
            <UserDetailsStep
              formData={{
                phone: formData.phone,
                state: formData.state,
                city: formData.city,
                age_group: formData.age_group
              }}
              onChange={updateField}
            />
          </motion.div>

          {/* Divider */}
          <div className="border-t border-gray-200"></div>

          {/* Preferences Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Preferences</h2>
            <PreferencesStep
              formData={{
                preferred_parties: formData.preferred_parties,
                topics_of_interest: formData.topics_of_interest
              }}
              onChange={(field, values) => updateField(field, values)}
            />
          </motion.div>

          {/* Action buttons */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="flex gap-4 pt-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => router.push('/dashboard')}
              className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-all"
            >
              Cancel
            </motion.button>

            <motion.button
              whileHover={{ scale: !loading ? 1.02 : 1 }}
              whileTap={{ scale: !loading ? 0.98 : 1 }}
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg text-white font-semibold hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </motion.button>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  )
}

