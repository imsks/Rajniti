import type { Page } from '@playwright/test'

export const TEST_USER_ID = 'test-user-1'
export const TEST_USER_EMAIL = 'test-user@rajniti.test'
export const TEST_USER_NAME = 'Test User'

export type LoginAsOptions = {
  userId: string
  callbackUrl?: string
  onboardingCompleted?: boolean
}

/**
 * Signs in via the test-credentials provider (/auth/test-signin).
 * Requires ENABLE_TEST_AUTH=true on the Next.js server (set in playwright webServer).
 */
export async function loginAs(
  page: Page,
  options: LoginAsOptions,
): Promise<void> {
  const callbackUrl = options.callbackUrl ?? '/dashboard'
  const onboardingCompleted = options.onboardingCompleted ?? true

  const params = new URLSearchParams({
    userId: options.userId,
    onboardingCompleted: String(onboardingCompleted),
    callbackUrl,
  })

  await page.goto(`/auth/test-signin?${params.toString()}`)
  await page.waitForURL(`**${callbackUrl}`, { timeout: 15_000 })
}

export async function signInAsTestUser(
  page: Page,
  options: { callbackUrl?: string; onboardingCompleted?: boolean } = {},
): Promise<void> {
  await loginAs(page, {
    userId: TEST_USER_ID,
    callbackUrl: options.callbackUrl,
    onboardingCompleted: options.onboardingCompleted,
  })
}
