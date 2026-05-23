import { expect, type Page } from '@playwright/test'

type LoginAsOptions = {
  userId: string
  onboardingCompleted: boolean
  callbackUrl?: string
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export async function mockUserOnboardingStatus(
  page: Page,
  userId: string,
  onboardingCompleted: boolean
) {
  await page.route(`**${API_BASE}/users/${userId}`, async (route) => {
    if (route.request().method() !== 'GET') {
      await route.continue()
      return
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        success: true,
        data: {
          id: userId,
          onboarding_completed: onboardingCompleted,
        },
      }),
    })
  })
}

export async function loginAs(
  page: Page,
  { userId, onboardingCompleted, callbackUrl = '/dashboard' }: LoginAsOptions
) {
  await mockUserOnboardingStatus(page, userId, onboardingCompleted)

  const csrfResponse = await page.request.get('/api/auth/csrf')
  const { csrfToken } = (await csrfResponse.json()) as { csrfToken: string }

  await page.request.post('/api/auth/callback/test-credentials', {
    form: {
      csrfToken,
      userId,
      onboardingCompleted: String(onboardingCompleted),
      callbackUrl,
      json: 'true',
    },
  })

  await expect
    .poll(
      async () => {
        const sessionResponse = await page.request.get('/api/auth/session')
        const session = (await sessionResponse.json()) as {
          user?: { id?: string }
        }
        return session.user?.id ?? null
      },
      { timeout: 15_000 }
    )
    .toBe(userId)
}
