'use client'

import { useEffect, useMemo, useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { userService } from '@/lib/api/user'
import {
  onboardingCompletedFromApi,
  shouldRedirectToDashboard,
  shouldRedirectToOnboarding,
  shouldSyncJwtOnboardingCompleted,
} from '@/lib/auth/onboarding-status'
import { ROUTES } from '@/lib/routes'

export type UseOnboardingCheckOptions = {
  /**
   * When true (default), sends incomplete users to onboarding unless they are
   * already on an onboarding URL.
   */
  redirectIfIncomplete?: boolean
  /** When true, sends already-onboarded users away from onboarding to dashboard. */
  redirectIfComplete?: boolean
}

export type UseOnboardingCheckResult = {
  /** Session or backend onboarding check still in progress */
  sessionLoading: boolean
  /** Signed in and backend reports onboarding incomplete */
  needsOnboarding: boolean
  /** Signed in and backend reports onboarding complete */
  isOnboarded: boolean
}

/**
 * Resolves onboarding status from the backend user record (source of truth),
 * then optionally redirects. JWT/session is synced after fetch but not used
 * to decide access.
 */
export function useOnboardingCheck(
  options: UseOnboardingCheckOptions = {}
): UseOnboardingCheckResult {
  const { redirectIfIncomplete = true, redirectIfComplete = false } = options
  const pathname = usePathname()
  const router = useRouter()
  const { data: session, status, update } = useSession()

  const [onboardingStatus, setOnboardingStatus] = useState<boolean | null>(null)
  const [statusLoading, setStatusLoading] = useState(false)

  const sessionLoading = status === 'loading'
  const isAuthenticated = status === 'authenticated'
  const userId = session?.user?.id

  useEffect(() => {
    if (sessionLoading || !isAuthenticated || !userId) {
      setOnboardingStatus(null)
      setStatusLoading(false)
      return
    }

    let cancelled = false
    setStatusLoading(true)
    const jwtFallback = Boolean(session?.user?.onboardingCompleted)

    void userService
      .getUser(userId)
      .then((response) => {
        if (cancelled) return
        const completed = onboardingCompletedFromApi(response?.data)
        setOnboardingStatus(completed)

        if (shouldSyncJwtOnboardingCompleted(completed, jwtFallback)) {
          void update({ onboardingCompleted: true })
        }
      })
      .catch((error) => {
        if (cancelled) return
        console.error('Failed to fetch onboarding status:', error)
        setOnboardingStatus(jwtFallback)
      })
      .finally(() => {
        if (!cancelled) setStatusLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [sessionLoading, isAuthenticated, userId, update, session?.user?.onboardingCompleted])

  const checkingOnboarding =
    isAuthenticated && (statusLoading || onboardingStatus === null)
  const sessionLoadingCombined = sessionLoading || checkingOnboarding

  const needsOnboarding = isAuthenticated && onboardingStatus === false
  const isOnboarded = isAuthenticated && onboardingStatus === true

  useEffect(() => {
    if (sessionLoadingCombined || !isAuthenticated) return

    const completed = onboardingStatus === true

    if (
      shouldRedirectToOnboarding({
        completed,
        pathname,
        redirectIfIncomplete,
      })
    ) {
      router.replace(ROUTES.onboarding)
      return
    }

    if (
      shouldRedirectToDashboard({
        completed,
        pathname,
        redirectIfComplete,
      })
    ) {
      router.replace(ROUTES.dashboard)
    }
  }, [
    sessionLoadingCombined,
    isAuthenticated,
    onboardingStatus,
    pathname,
    redirectIfIncomplete,
    redirectIfComplete,
    router,
  ])

  return useMemo(
    (): UseOnboardingCheckResult => ({
      sessionLoading: sessionLoadingCombined,
      needsOnboarding,
      isOnboarded,
    }),
    [sessionLoadingCombined, needsOnboarding, isOnboarded]
  )
}
