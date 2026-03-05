'use client'

import { Suspense } from 'react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { motion, AnimatePresence } from 'framer-motion'
import PoliticalInclinationStep from '@/components/onboarding/PoliticalInclinationStep'
import UsernameStep from '@/components/onboarding/UsernameStep'
import { userService } from '@/lib/api/user'
import { useAnalytics } from '@/hooks/useAnalytics'

export default function Onboarding() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 flex items-center justify-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent"></div>
      </div>
    }>
      <OnboardingContent />
    </Suspense>
  )
}

function OnboardingContent() {
  const router = useRouter()
  const { data: session, update } = useSession()
  const { trackEvent } = useAnalytics()
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

      trackEvent('onboarding_complete', { political_interest: formData.political_interest })
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
    <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 py-12 px-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl mx-auto">
        {/* Progress bar */}
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Step {step} of {totalSteps}</span>
            <span className="text-sm text-gray-500">
              {step === 1 && 'Political Inclination'}
              {step === 2 && 'Username'}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${(step / totalSteps) * 100}%` }}
              transition={{ duration: 0.5 }}
              className="bg-gradient-to-r from-orange-500 to-green-500 h-2 rounded-full"
            />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-white rounded-2xl shadow-xl p-8 border border-orange-100">
          <AnimatePresence mode="wait">
            {/* Step 1: Political Inclination */}
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <PoliticalInclinationStep
                  value={formData.political_interest}
                  onChange={(value) => updateField('political_interest', value)}
                />
              </motion.div>
            )}

            {/* Step 2: Username */}
            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <UsernameStep
                      value={formData.username}
                  onChange={(value) => updateField('username', value)}
                  onValidation={setUsernameValid}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation buttons */}
          <div className="flex gap-4 mt-8">
            {step > 1 && (
              <motion.button
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setStep(step - 1)}
                className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-all"
              >
                Back
              </motion.button>
            )}
            
            {step < totalSteps ? (
              <motion.button
                whileHover={{ scale: canProceedToNextStep() ? 1.02 : 1 }}
                whileTap={{ scale: canProceedToNextStep() ? 0.98 : 1 }}
                onClick={() => {
                  const stepNames = ['political_inclination', 'username']
                  trackEvent('onboarding_step_complete', { step, step_name: stepNames[step - 1] })
                  setStep(step + 1)
                }}
                disabled={!canProceedToNextStep()}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg text-white font-semibold hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: !loading ? 1.02 : 1 }}
                whileTap={{ scale: !loading ? 0.98 : 1 }}
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 rounded-lg text-white font-semibold hover:from-green-600 hover:to-green-700 transition-all shadow-lg disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Complete Onboarding'}
              </motion.button>
            )}
          </div>
        </motion.div>

        {/* Skip button */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="text-center mt-6">
          <button 
            onClick={() => {
              trackEvent('onboarding_skip', { at_step: step })
              router.push('/dashboard')
            }}
            className="text-gray-500 hover:text-gray-700 font-medium"
          >
            Skip for now →
          </button>
        </motion.div>
      </motion.div>
    </div>
  )
}
