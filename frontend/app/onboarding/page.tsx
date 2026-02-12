'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useSession } from 'next-auth/react'
import PoliticalInclinationStep from '@/components/onboarding/PoliticalInclinationStep'
import UsernameStep from '@/components/onboarding/UsernameStep'
import { userService } from '@/lib/api/user'

export default function Onboarding() {
  const router = useRouter()
  const { data: session, update } = useSession()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [usernameValid, setUsernameValid] = useState(false)
  
  const [formData, setFormData] = useState({
    political_interest: '',
    username: ''
  })

  const updateField = (field: string, value: string) => {
    setFormData({
      ...formData,
      [field]: value
    })
  }

  const canProceedToNextStep = () => {
    switch (step) {
      case 1:
        return formData.political_interest !== ''
      case 2:
        return formData.username !== '' && usernameValid
      default:
        return false
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      if (!session?.user?.id) {
        alert('Please sign in to complete onboarding')
        return
      }
      
      // Call backend API using the generic update endpoint
      await userService.updateUser(session.user.id, {
        political_interest: formData.political_interest,
        username: formData.username,
        onboarding_completed: true
      })

      // Update NextAuth session to reflect onboarding completion
      await update({ onboardingCompleted: true })
      router.push('/dashboard')
    } catch (error) {
      console.error('Onboarding failed:', error)
      alert(error instanceof Error ? error.message : 'Failed to complete onboarding. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const totalSteps = 2

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:bg-slate-900 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Step {step} of {totalSteps}</span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {step === 1 && 'Political Inclination'}
              {step === 2 && 'Username'}
            </span>
          <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-orange-500 to-green-500 dark:from-orange-400 dark:to-green-400 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(step / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 border border-orange-100 dark:border-slate-700">
          {/* Step 1: Political Inclination */}
          {step === 1 && (
            <PoliticalInclinationStep
              value={formData.political_interest}
              onChange={(value) => updateField('political_interest', value)}
            />
          )}

          {/* Step 2: Username */}
          {step === 2 && (
            <UsernameStep
              value={formData.username}
              onChange={(value) => updateField('username', value)}
              onValidation={setUsernameValid}
            />
          )}

          {/* Navigation buttons */}
          <div className="flex gap-4 mt-8">
            {step > 1 && (
              <button
                onClick={() => setStep(step - 1)}
                className="flex-1 px-6 py-3 border-2 border-gray-300 dark:border-slate-600 rounded-lg text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-50 dark:hover:bg-slate-700 transition-all"
              >
                Back
              </button>
            )}
            
            {step < totalSteps ? (
              <button
                onClick={() => setStep(step + 1)}
                disabled={!canProceedToNextStep()}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 dark:from-orange-600 dark:to-orange-700 rounded-lg text-white font-semibold hover:from-orange-600 hover:to-orange-700 dark:hover:from-orange-700 dark:hover:to-orange-800 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 rounded-lg text-white font-semibold hover:from-green-600 hover:to-green-700 transition-all shadow-lg disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Complete Onboarding'}
              </button>
            )}
          </div>
        </div>

        {/* Skip button */}
        <div className="text-center mt-6">
          <button 
            onClick={() => router.push('/dashboard')}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 font-medium"
          >
            Skip for now →
          </button>
        </div>
      </div>
    </div>
  )
}
