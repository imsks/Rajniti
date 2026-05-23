import type { JWT } from 'next-auth/jwt'
import { onboardingCompletedFromApi } from '@/lib/auth/onboarding-status'

export type UserOnboardingResponse = {
  data?: {
    onboarding_completed?: boolean
  }
}

export function onboardingCompletedFromUserResponse(
  response: UserOnboardingResponse | null | undefined
): boolean {
  return onboardingCompletedFromApi(response?.data)
}

export function applyOnboardingCompleted(
  token: JWT,
  onboardingCompleted: boolean
): JWT {
  return {
    ...token,
    onboardingCompleted,
  }
}
