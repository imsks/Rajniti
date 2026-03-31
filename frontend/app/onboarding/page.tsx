'use client'

import { Suspense } from 'react'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { motion, AnimatePresence } from 'framer-motion'
import PoliticalInclinationStep from '@/components/onboarding/PoliticalInclinationStep'
import UsernameStep from '@/components/onboarding/UsernameStep'
import UserDetailsStep from '@/components/onboarding/UserDetailsStep'
import PreferencesStep from '@/components/onboarding/PreferencesStep'
import { userService } from '@/lib/api/user'
import { useAnalytics } from '@/hooks/useAnalytics'

// ── Types ────────────────────────────────────────────────────────────────────
interface OnboardingData {
  // Step 1
  political_ideology: string
  // Step 2
  phone: string
  state: string
  city: string
  age_group: string
  // Step 3
  preferred_parties: string[]
  topics_of_interest: string[]
  // Step 4
  username: string
}

const INITIAL_DATA: OnboardingData = {
  political_ideology: '',
  phone: '',
  state: '',
  city: '',
  age_group: '',
  preferred_parties: [],
  topics_of_interest: [],
  username: '',
}

const STEP_LABELS = [
  'Political Inclination',
  'Basic Details',
  'Preferences',
  'Username',
]

// ── Root (with Suspense for useSearchParams safety) ─────────────────────────
export default function Onboarding() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 flex items-center justify-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent" />
        </div>
      }
    >
      <OnboardingContent />
    </Suspense>
  )
}

// ── Main controller ──────────────────────────────────────────────────────────
function OnboardingContent() {
  const router = useRouter()
  const { data: session, update } = useSession()
  const { trackEvent } = useAnalytics()

  const [step, setStep]               = useState(1)
  const [loading, setLoading]         = useState(false)
  const [usernameValid, setUsernameValid] = useState(false)
  const [formData, setFormData]       = useState<OnboardingData>(INITIAL_DATA)

  const totalSteps = STEP_LABELS.length

  // ── Shared updater ───────────────────────────────────────────────────────
  const updateField = (field: keyof OnboardingData, value: string | string[]) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  // ── Per-step "can proceed" guard ─────────────────────────────────────────
  const canProceed = () => {
    switch (step) {
      case 1: return formData.political_ideology !== ''
      case 2: return formData.state !== '' && formData.age_group !== ''
      case 3: return true                                     // preferences optional
      case 4: return formData.username !== '' && usernameValid
      default: return false
    }
  }

  // ── Final submit ─────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    setLoading(true)
    try {
      if (!session?.user?.id) {
        alert('Please sign in to complete onboarding')
        return
      }

      await userService.updateUser(session.user.id, {
        political_ideology:  formData.political_ideology,
        username:            formData.username,
        phone:               formData.phone,
        state:               formData.state,
        city:                formData.city,
        age_group:           formData.age_group,
        preferred_parties: formData.preferred_parties?.join(", "),
        topics_of_interest: formData.topics_of_interest?.join(", "),
        onboarding_completed: true,
      })

      trackEvent('onboarding_complete', {
        political_ideology: formData.political_ideology,
      })

      await update({ onboardingCompleted: true })
      router.push('/dashboard')
    } catch (error) {
      console.error('Onboarding failed:', error)
      alert(
        error instanceof Error
          ? error.message
          : 'Failed to complete onboarding. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  // ── Next handler ─────────────────────────────────────────────────────────
  const handleNext = () => {
    trackEvent('onboarding_step_complete', {
      step,
      step_name: STEP_LABELS[step - 1],
    })
    setStep(s => s + 1)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-2xl mx-auto"
      >
        {/* ── Progress bar ── */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">
              Step {step} of {totalSteps}
            </span>
            <span className="text-sm text-gray-500">
              {STEP_LABELS[step - 1]}
            </span>
          </div>

          {/* Segmented step dots */}
          <div className="flex gap-1.5 mb-2">
            {STEP_LABELS.map((_, i) => (
              <div
                key={i}
                className={`h-2 flex-1 rounded-full transition-all duration-500 ${
                  i < step
                    ? 'bg-gradient-to-r from-orange-500 to-green-500'
                    : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </motion.div>

        {/* ── Card ── */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-white rounded-2xl shadow-xl p-8 border border-orange-100"
        >
          <AnimatePresence mode="wait">
            {/* Step 1 — Political Inclination */}
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <PoliticalInclinationStep
                  value={formData.political_ideology}
                  onChange={val => updateField('political_ideology', val)}
                />
              </motion.div>
            )}

            {/* Step 2 — User Details */}
            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <UserDetailsStep
                  formData={{
                    phone:     formData.phone,
                    state:     formData.state,
                    city:      formData.city,
                    age_group: formData.age_group,
                  }}
                  onChange={(field, value) =>
                    updateField(field as keyof OnboardingData, value)
                  }
                />
              </motion.div>
            )}

            {/* Step 3 — Preferences */}
            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <PreferencesStep
                  formData={{
                    preferred_parties:  formData.preferred_parties,
                    topics_of_interest: formData.topics_of_interest,
                  }}
                  onChange={(field, values) =>
                    updateField(field as keyof OnboardingData, values)
                  }
                />
              </motion.div>
            )}

            {/* Step 4 — Username */}
            {step === 4 && (
              <motion.div
                key="step4"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                <UsernameStep
                  value={formData.username}
                  onChange={val => updateField('username', val)}
                  onValidation={setUsernameValid}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Navigation buttons ── */}
          <div className="flex gap-4 mt-8">
            {step > 1 && (
              <motion.button
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setStep(s => s - 1)}
                className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-all"
              >
                Back
              </motion.button>
            )}

            {step < totalSteps ? (
              <motion.button
                whileHover={{ scale: canProceed() ? 1.02 : 1 }}
                whileTap={{ scale: canProceed() ? 0.98 : 1 }}
                onClick={handleNext}
                disabled={!canProceed()}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg text-white font-semibold hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: !loading ? 1.02 : 1 }}
                whileTap={{ scale: !loading ? 0.98 : 1 }}
                onClick={handleSubmit}
                disabled={loading || !canProceed()}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 rounded-lg text-white font-semibold hover:from-green-600 hover:to-green-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Saving...' : 'Complete Onboarding 🚀'}
              </motion.button>
            )}
          </div>
        </motion.div>

        {/* ── Skip ── */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="text-center mt-6"
        >
          <button
            onClick={async () => {
  try {
    // track event
    trackEvent('onboarding_skip', { at_step: step })

    // ✅ direct fetch (bypass userService issues)
    await fetch("http://127.0.0.1:5000/api/v1/users/onboarding", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        id: session?.user?.id,
        onboarding_completed: true
      })
    })

    // ✅ update session (IMPORTANT)
    await update({ onboardingCompleted: true })

    // ✅ redirect
    router.push('/dashboard')

  } catch (err) {
    console.error("Skip failed:", err)
  }
}}
            className="text-gray-500 hover:text-gray-700 font-medium text-sm"
          >
            Skip for now →
          </button>
        </motion.div>
      </motion.div>
    </div>
  )
}