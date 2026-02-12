'use client'

import { motion } from "framer-motion"
import { fadeInUp, staggerContainer, scaleIn, buttonTap, quickTransition } from "@/utils/motion"

interface PoliticalInclinationStepProps {
  value: string
  onChange: (value: string) => void
}

export default function PoliticalInclinationStep({ value, onChange }: PoliticalInclinationStepProps) {
  const options = [
    { value: 'Rightist', label: 'Rightist', description: 'Conservative, traditional values, free market economy' },
    { value: 'Leftist', label: 'Leftist', description: 'Progressive, social equality, welfare policies' },
    { value: 'Communist', label: 'Communist', description: 'Collective ownership, socialist principles' },
    { value: 'Centrist', label: 'Centrist', description: 'Moderate, balanced approach to politics' },
    { value: 'Libertarian', label: 'Libertarian', description: 'Individual liberty, minimal government intervention' },
    { value: 'Neutral', label: 'Neutral/Apolitical', description: 'No strong political alignment' }
  ]

  return (
    <motion.div 
      className="space-y-4"
      initial="initial"
      animate="animate"
      variants={staggerContainer}
    >
      <motion.div className="text-center mb-6" variants={fadeInUp}>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Political Inclination
        </h2>
        <p className="text-gray-600">
          What best describes your political inclination?
        </p>
      </motion.div>

      <motion.div className="space-y-3" variants={staggerContainer}>
        {options.map((option) => (
          <motion.button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            variants={scaleIn}
            whileTap={buttonTap}
            whileHover={{ scale: 1.02, y: -2 }}
            transition={quickTransition}
            className={`w-full text-left p-5 rounded-xl border-2 transition-all ${
              value === option.value
                ? 'border-orange-500 bg-orange-50 shadow-md'
                : 'border-gray-200 bg-white hover:border-orange-300 hover:shadow-sm'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className={`shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center mt-0.5 ${
                value === option.value
                  ? 'border-orange-500 bg-orange-500'
                  : 'border-gray-300 bg-white'
              }`}>
                {value === option.value && (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className="flex-1">
                <h3 className={`font-semibold ${
                  value === option.value ? 'text-orange-700' : 'text-gray-900'
                }`}>
                  {option.label}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {option.description}
                </p>
              </div>
            </div>
          </motion.button>
        ))}
      </motion.div>
    </motion.div>
  )
}
