import {
  applyOnboardingCompleted,
  onboardingCompletedFromUserResponse,
} from '@/lib/auth/onboarding-token'

describe('onboardingCompletedFromUserResponse', () => {
  it('reads onboarding_completed from API payload', () => {
    expect(
      onboardingCompletedFromUserResponse({
        data: { onboarding_completed: true },
      })
    ).toBe(true)
  })

  it('returns false when onboarding_completed is missing or false', () => {
    expect(onboardingCompletedFromUserResponse({ data: {} })).toBe(false)
    expect(
      onboardingCompletedFromUserResponse({
        data: { onboarding_completed: false },
      })
    ).toBe(false)
    expect(onboardingCompletedFromUserResponse(undefined)).toBe(false)
  })
})

describe('applyOnboardingCompleted', () => {
  it('updates onboardingCompleted on the token', () => {
    expect(
      applyOnboardingCompleted(
        { userId: 'user-1', onboardingCompleted: false },
        true
      )
    ).toEqual({
      userId: 'user-1',
      onboardingCompleted: true,
    })
  })
})
