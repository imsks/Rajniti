'use client'

import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import UserDetailsStep from '@/components/onboarding/UserDetailsStep'
import PreferencesStep from '@/components/onboarding/PreferencesStep'

// API Base URL - configurable via environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export default function EditProfile() {
  const router = useRouter()
  const { data: session } = useSession()
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
    try {
      if (!session?.user?.id) {
        alert('Please sign in to update your profile')
        return
      }
      
      // Call backend API to update profile
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
        alert('Profile updated successfully!')
        router.push('/dashboard')
      } else {
        const error = await response.json()
        alert(error.error || 'Failed to update profile')
      }
    } catch (error) {
      console.error('Profile update failed:', error)
      alert('Failed to update profile. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (fetching) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:bg-slate-900 py-12 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 dark:border-orange-400 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Loading your profile...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:bg-slate-900 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">Edit Profile</h1>
          <p className="text-gray-600 dark:text-gray-300">Update your personal information and preferences</p>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-orange-100 dark:border-slate-700 space-y-8">
          {/* Basic Details Section */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Basic Details</h2>
            <UserDetailsStep
              formData={{
                phone: formData.phone,
                state: formData.state,
                city: formData.city,
                age_group: formData.age_group
              }}
              onChange={updateField}
            />
          </div>

          {/* Divider */}
          <div className="border-t border-gray-200 dark:border-slate-700"></div>

          {/* Preferences Section */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Preferences</h2>
            <PreferencesStep
              formData={{
                preferred_parties: formData.preferred_parties,
                topics_of_interest: formData.topics_of_interest
              }}
              onChange={(field, values) => updateField(field, values)}
            />
          </div>

          {/* Action buttons */}
          <div className="flex gap-4 pt-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="flex-1 px-6 py-3 border-2 border-gray-300 dark:border-slate-600 rounded-lg text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-50 dark:hover:bg-slate-700 transition-all"
            >
              Cancel
            </button>
            
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 dark:from-orange-600 dark:to-orange-700 rounded-lg text-white font-semibold hover:from-orange-600 hover:to-orange-700 dark:hover:from-orange-700 dark:hover:to-orange-800 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

