'use client'

import { motion } from "framer-motion"
import { fadeInUp, staggerContainer, scaleIn, buttonTap, quickTransition } from "@/utils/motion"

interface PreferencesStepProps {
  formData: {
    preferred_parties: string[]
    topics_of_interest: string[]
  }
  onChange: (field: 'preferred_parties' | 'topics_of_interest', values: string[]) => void
}

const PARTIES = [
  'Bharatiya Janata Party',
  'Indian National Congress',
  'Aam Aadmi Party',
  'Trinamool Congress',
  'Dravida Munnetra Kazhagam',
  'Shiv Sena',
  'Nationalist Congress Party',
  'Communist Party of India (Marxist)',
  'Bahujan Samaj Party',
  'Others'
]

const TOPICS = [
  'Economy',
  'Healthcare',
  'Education',
  'Infrastructure',
  'Agriculture',
  'Environment',
  'Technology',
  'Social Justice',
  'Employment',
  'National Security'
]

export default function PreferencesStep({ formData, onChange }: PreferencesStepProps) {
  const toggleSelection = (field: 'preferred_parties' | 'topics_of_interest', value: string) => {
    const current = formData[field]
    if (current.includes(value)) {
      onChange(field, current.filter(item => item !== value))
    } else {
      onChange(field, [...current, value])
    }
  }

  return (
    <motion.div 
      className="space-y-6"
      initial="initial"
      animate="animate"
      variants={staggerContainer}
    >
      <motion.div className="text-center mb-6" variants={fadeInUp}>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Your Preferences
        </h2>
        <p className="text-gray-600">
          Help us tailor content to your interests
        </p>
      </motion.div>

      {/* Preferred Parties */}
      <motion.div variants={fadeInUp}>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Preferred Parties <span className="text-gray-400">(Select all that apply)</span>
        </label>
        <motion.div 
          className="grid grid-cols-1 sm:grid-cols-2 gap-3"
          variants={staggerContainer}
        >
          {PARTIES.map((party) => (
            <motion.button
              key={party}
              type="button"
              onClick={() => toggleSelection('preferred_parties', party)}
              variants={scaleIn}
              whileTap={buttonTap}
              whileHover={{ scale: 1.02 }}
              transition={quickTransition}
              className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all text-left ${
                formData.preferred_parties.includes(party)
                  ? 'border-orange-500 bg-orange-50 text-orange-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-orange-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <div className={`w-4 h-4 rounded border-2 flex items-center justify-center shrink-0 ${
                  formData.preferred_parties.includes(party)
                    ? 'border-orange-500 bg-orange-500'
                    : 'border-gray-300 bg-white'
                }`}>
                  {formData.preferred_parties.includes(party) && (
                    <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <span className="truncate">{party}</span>
              </div>
            </motion.button>
          ))}
        </motion.div>
      </motion.div>

      {/* Topics of Interest */}
      <motion.div variants={fadeInUp}>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Topics of Interest <span className="text-gray-400">(Select all that apply)</span>
        </label>
        <motion.div 
          className="grid grid-cols-2 sm:grid-cols-3 gap-3"
          variants={staggerContainer}
        >
          {TOPICS.map((topic) => (
            <motion.button
              key={topic}
              type="button"
              onClick={() => toggleSelection('topics_of_interest', topic)}
              variants={scaleIn}
              whileTap={buttonTap}
              whileHover={{ scale: 1.02 }}
              transition={quickTransition}
              className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                formData.topics_of_interest.includes(topic)
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-green-300'
              }`}
            >
              {topic}
            </motion.button>
          ))}
        </motion.div>
      </motion.div>

      <motion.div 
        className="bg-blue-50 border border-blue-200 rounded-lg p-4"
        variants={fadeInUp}
      >
        <div className="flex gap-3">
          <svg className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <p className="text-sm text-blue-800">
            Your preferences help us show you relevant political news and updates. You can change these anytime in your profile settings.
          </p>
        </div>
      </motion.div>
    </motion.div>
  )
}
