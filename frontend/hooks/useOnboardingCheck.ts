'use client'

import { useEffect, useMemo } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { ROUTES } from '@/lib/routes'

export type UseOnboardingCheckOptions = {
  /**
   * When true (default), sends incomplete users to onboarding unless they are
   * already on an onboarding URL. Middleware already enforces this for most
   * navigations; this covers stale client session after tab restore, etc.
   */
  redirectIfIncomplete?: boolean
}

export type UseOnboardingCheckResult = {
  /** NextAuth has not finished resolving the session */
  sessionLoading: boolean
  /** Signed in and `onboardingCompleted` is false */
  needsOnboarding: boolean
  /** Signed in and onboarding is done (false if not signed in) */
  isOnboarded: boolean
}

function isOnboardingPath(pathname: string): boolean {
  return (
    pathname === ROUTES.onboarding ||
    pathname.startsWith(`${ROUTES.onboarding}/`)
  )
}

/**
 * Derives onboarding status from the session and optionally redirects incomplete
 * users to `/onboarding` when they hit protected UI (e.g. dashboard).
 */
export function useOnboardingCheck(
  options: UseOnboardingCheckOptions = {}
): UseOnboardingCheckResult {
  const { redirectIfIncomplete = true } = options
  const pathname = usePathname()
  const router = useRouter()
  const { data: session, status } = useSession()

  const sessionLoading = status === 'loading'
  const isAuthenticated = status === 'authenticated'
  const onboardingCompleted = Boolean(session?.user?.onboardingCompleted)

  const needsOnboarding = isAuthenticated && !onboardingCompleted
  const onOnboardingRoute = isOnboardingPath(pathname)

  useEffect(() => {
    if (sessionLoading) return
    if (!needsOnboarding) return
    if (onOnboardingRoute) return
    if (!redirectIfIncomplete) return

    router.replace(ROUTES.onboarding)
  }, [
    sessionLoading,
    needsOnboarding,
    onOnboardingRoute,
    redirectIfIncomplete,
    router,
  ])

  return useMemo(
    (): UseOnboardingCheckResult => ({
      sessionLoading,
      needsOnboarding,
      isOnboarded: isAuthenticated && onboardingCompleted,
    }),
    [sessionLoading, needsOnboarding, isAuthenticated, onboardingCompleted]
  )
}
