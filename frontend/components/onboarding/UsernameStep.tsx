'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import { Input, Spinner } from '@sutra/ui'
import { userService } from '@/lib/api/user'

interface UsernameStepProps {
  value: string
  onChange: (value: string) => void
  onValidation: (isValid: boolean) => void
}

export default function UsernameStep({ value, onChange, onValidation }: UsernameStepProps) {
  const { data: session } = useSession()
  const [checking, setChecking] = useState(false)
  const [available, setAvailable] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)

  const checkUsername = useCallback(async (username: string) => {
    try {
      setChecking(true)
      setError(null)

      // Call backend API to check username availability
      const data = await userService.checkUsername(username, session?.user?.id)

      setAvailable(data.available)
      onValidation(data.available)
    } catch (err) {
      console.error('Error checking username:', err)
      setError('Failed to check username availability')
      onValidation(false)
    } finally {
      setChecking(false)
    }
  }, [onValidation, session])

  useEffect(() => {
    // Reset states when value changes
    setAvailable(null)
    setError(null)

    if (!value || value.length < 3) {
      onValidation(false)
      if (value && value.length < 3) {
        setError('Username must be at least 3 characters')
      }
      return
    }

    // Validate username format (alphanumeric and underscores only)
    const usernameRegex = /^[a-zA-Z0-9_]+$/
    if (!usernameRegex.test(value)) {
      setError('Username can only contain letters, numbers, and underscores')
      onValidation(false)
      return
    }

    // Check availability with debounce
    const timer = setTimeout(() => {
      checkUsername(value)
    }, 500)

    return () => clearTimeout(timer)
  }, [value, checkUsername, onValidation])

  return (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-content mb-2">
          Choose Your Username
        </h2>
        <p className="text-content-muted">
          Pick a unique username that represents you
        </p>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-content">
          Username
        </label>
        <div className="relative">
          <Input
            type="text"
            size="lg"
            value={value}
            onChange={(e) => onChange(e.target.value.toLowerCase())}
            placeholder="johndoe"
            aria-label="Username"
            invalid={Boolean(error)}
            className={`pr-12 ${
              available === true && !error
                ? 'border-success focus-visible:ring-success'
                : ''
            }`}
          />

          {/* Status icon */}
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            {checking && (
              <span className="text-accent">
                <Spinner size="md" label="Checking username" />
              </span>
            )}
            {!checking && available === true && (
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            )}
            {!checking && available === false && (
              <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </div>

        {/* Error or success message */}
        {error && (
          <p className="text-sm text-red-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
        {!error && available === true && (
          <p className="text-sm text-green-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Username is available!
          </p>
        )}
        {!error && available === false && (
          <p className="text-sm text-red-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            Username is already taken
          </p>
        )}

        <p className="text-xs text-content-muted mt-2">
          Only lowercase letters, numbers, and underscores. Minimum 3 characters.
        </p>
      </div>
    </div>
  )
}
