import {
  isOnboardingPath,
  onboardingCompletedFromApi,
  resolveOnboardingStatus,
  shouldRedirectToDashboard,
  shouldRedirectToOnboarding,
  shouldSyncJwtOnboardingCompleted,
} from '@/lib/auth/onboarding-status'
import { ROUTES } from '@/lib/routes'

describe('onboardingCompletedFromApi', () => {
  it('returns true when onboarding_completed is true', () => {
    expect(onboardingCompletedFromApi({ onboarding_completed: true })).toBe(true)
  })

  it('returns false when missing or false', () => {
    expect(onboardingCompletedFromApi(undefined)).toBe(false)
    expect(onboardingCompletedFromApi({ onboarding_completed: false })).toBe(false)
  })
})

describe('resolveOnboardingStatus', () => {
  it('prefers API value when defined', () => {
    expect(resolveOnboardingStatus(true, false)).toBe(true)
    expect(resolveOnboardingStatus(false, true)).toBe(false)
  })

  it('falls back to JWT when API is undefined', () => {
    expect(resolveOnboardingStatus(undefined, true)).toBe(true)
    expect(resolveOnboardingStatus(undefined, false)).toBe(false)
  })
})

describe('isOnboardingPath', () => {
  it('matches onboarding routes', () => {
    expect(isOnboardingPath(ROUTES.onboarding)).toBe(true)
    expect(isOnboardingPath(`${ROUTES.onboarding}/step-2`)).toBe(true)
    expect(isOnboardingPath(ROUTES.dashboard)).toBe(false)
  })
})

describe('shouldRedirectToOnboarding', () => {
  it('redirects incomplete users off protected routes', () => {
    expect(
      shouldRedirectToOnboarding({
        completed: false,
        pathname: ROUTES.dashboard,
        redirectIfIncomplete: true,
      })
    ).toBe(true)
  })

  it('does not redirect when already on onboarding', () => {
    expect(
      shouldRedirectToOnboarding({
        completed: false,
        pathname: ROUTES.onboarding,
        redirectIfIncomplete: true,
      })
    ).toBe(false)
  })

  it('does not redirect when complete or flag disabled', () => {
    expect(
      shouldRedirectToOnboarding({
        completed: true,
        pathname: ROUTES.dashboard,
        redirectIfIncomplete: true,
      })
    ).toBe(false)
    expect(
      shouldRedirectToOnboarding({
        completed: false,
        pathname: ROUTES.dashboard,
        redirectIfIncomplete: false,
      })
    ).toBe(false)
  })
})

describe('shouldRedirectToDashboard', () => {
  it('redirects complete users away from onboarding', () => {
    expect(
      shouldRedirectToDashboard({
        completed: true,
        pathname: ROUTES.onboarding,
        redirectIfComplete: true,
      })
    ).toBe(true)
  })

  it('does not redirect incomplete users or when flag disabled', () => {
    expect(
      shouldRedirectToDashboard({
        completed: false,
        pathname: ROUTES.onboarding,
        redirectIfComplete: true,
      })
    ).toBe(false)
    expect(
      shouldRedirectToDashboard({
        completed: true,
        pathname: ROUTES.onboarding,
        redirectIfComplete: false,
      })
    ).toBe(false)
  })
})

describe('shouldSyncJwtOnboardingCompleted', () => {
  it('syncs when backend is ahead of JWT', () => {
    expect(shouldSyncJwtOnboardingCompleted(true, false)).toBe(true)
  })

  it('does not sync when JWT already matches or backend incomplete', () => {
    expect(shouldSyncJwtOnboardingCompleted(true, true)).toBe(false)
    expect(shouldSyncJwtOnboardingCompleted(false, false)).toBe(false)
  })
})
