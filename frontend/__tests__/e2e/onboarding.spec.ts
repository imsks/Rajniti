import { test, expect } from '@playwright/test'
import { loginAs } from './helpers/auth'

test.describe('Onboarding flow (authenticated)', () => {
  test('incomplete user visiting dashboard lands on onboarding', async ({
    page,
  }) => {
    await loginAs(page, {
      userId: 'e2e-incomplete-user',
      onboardingCompleted: false,
      callbackUrl: '/dashboard',
    })

    await page.goto('/dashboard')

    await expect(page).toHaveURL(/\/onboarding/, { timeout: 15_000 })
  })

  test('complete user visiting onboarding lands on dashboard', async ({
    page,
  }) => {
    await loginAs(page, {
      userId: 'e2e-complete-user',
      onboardingCompleted: true,
      callbackUrl: '/onboarding',
    })

    await page.goto('/onboarding')

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 15_000 })
  })

  test('incomplete user on onboarding sees step 1 UI', async ({ page }) => {
    await loginAs(page, {
      userId: 'e2e-wizard-user',
      onboardingCompleted: false,
      callbackUrl: '/onboarding',
    })

    await page.goto('/onboarding')

    await expect(page).toHaveURL(/\/onboarding/)
    await expect(page.getByText(/step 1 of 4/i)).toBeVisible({
      timeout: 15_000,
    })
    await expect(
      page.getByRole('heading', { name: /political inclination/i })
    ).toBeVisible()
  })
})
