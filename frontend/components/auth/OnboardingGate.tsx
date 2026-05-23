'use client'

import { useOnboardingCheck, type UseOnboardingCheckOptions } from '@/hooks/useOnboardingCheck'

type OnboardingGateProps = UseOnboardingCheckOptions & {
  children: React.ReactNode
  fallback?: React.ReactNode
  /** When true (default), block children while loading or when user needs onboarding. */
  blockUntilReady?: boolean
}

const defaultFallback = (
  <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 flex items-center justify-center">
    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent" />
  </div>
)

export default function OnboardingGate({
  children,
  fallback = defaultFallback,
  blockUntilReady = true,
  redirectIfIncomplete = true,
  redirectIfComplete = false,
}: OnboardingGateProps) {
  const { sessionLoading, needsOnboarding } = useOnboardingCheck({
    redirectIfIncomplete,
    redirectIfComplete,
  })

  if (blockUntilReady && (sessionLoading || needsOnboarding)) {
    return <>{fallback}</>
  }

  if (sessionLoading) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
