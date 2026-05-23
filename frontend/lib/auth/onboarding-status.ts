import { ROUTES } from '@/lib/routes'

export function onboardingCompletedFromApi(
  data: { onboarding_completed?: boolean } | undefined
): boolean {
  return Boolean(data?.onboarding_completed)
}

export function resolveOnboardingStatus(
  apiCompleted: boolean | undefined,
  jwtFallback: boolean
): boolean {
  if (apiCompleted !== undefined) {
    return apiCompleted
  }
  return jwtFallback
}

export function isOnboardingPath(pathname: string): boolean {
  return (
    pathname === ROUTES.onboarding ||
    pathname.startsWith(`${ROUTES.onboarding}/`)
  )
}

export function shouldRedirectToOnboarding(opts: {
  completed: boolean
  pathname: string
  redirectIfIncomplete: boolean
}): boolean {
  const { completed, pathname, redirectIfIncomplete } = opts
  return (
    redirectIfIncomplete &&
    !completed &&
    !isOnboardingPath(pathname)
  )
}

export function shouldRedirectToDashboard(opts: {
  completed: boolean
  pathname: string
  redirectIfComplete: boolean
}): boolean {
  const { completed, pathname, redirectIfComplete } = opts
  return (
    redirectIfComplete &&
    completed &&
    isOnboardingPath(pathname)
  )
}

export function shouldSyncJwtOnboardingCompleted(
  apiCompleted: boolean,
  jwtFallback: boolean
): boolean {
  return apiCompleted && !jwtFallback
}
