'use client'

import { Spinner } from '@sutra/ui'
import { useOnboardingCheck, type UseOnboardingCheckOptions } from '@/hooks/useOnboardingCheck'

type OnboardingGateProps = UseOnboardingCheckOptions & {
  children: React.ReactNode
  fallback?: React.ReactNode
  /** When true (default), block children while loading or when user needs onboarding. */
  blockUntilReady?: boolean
}

const defaultFallback = (
  <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 flex items-center justify-center">
    <span className="text-accent">
      <Spinner size="lg" label="Loading" />
    </span>
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
