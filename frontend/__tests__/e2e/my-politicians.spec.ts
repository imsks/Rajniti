import { test, expect } from '@playwright/test'
import { signInAsTestUser } from './helpers/auth'
import {
  createDashboardMockState,
  installDashboardApiMocks,
} from './helpers/mock-api'

test.describe('My Politicians section (authenticated)', () => {
  test('shows empty Add Your Local Politicians section on dashboard', async ({
    page,
  }) => {
    await installDashboardApiMocks(page, createDashboardMockState())
    await signInAsTestUser(page)

    await expect(
      page.getByRole('heading', { name: 'Add Your Local Politicians' }),
    ).toBeVisible({ timeout: 15_000 })
    await expect(
      page.getByPlaceholder('Find your MP or MLA, e.g. Modi'),
    ).toBeVisible()
    await expect(page.getByText('Your MP', { exact: true })).toBeVisible()
    await expect(page.getByText('Your MLA', { exact: true })).toBeVisible()
  })

  test('adds MP via search dropdown', async ({ page }) => {
    await installDashboardApiMocks(page, createDashboardMockState())
    await signInAsTestUser(page)

    await expect(
      page.getByRole('heading', { name: 'Add Your Local Politicians' }),
    ).toBeVisible({ timeout: 15_000 })

    const searchInput = page.locator('#my-politicians-search')
    const searchResponse = page.waitForResponse(/politicians\/search/)

    await searchInput.fill('Modi')
    await searchResponse

    await page.getByRole('button', { name: /Narendra Modi/i }).click()

    await expect(
      page.getByRole('heading', { name: 'Your Politicians' }),
    ).toBeVisible()
    await expect(page.getByText('Narendra Modi').first()).toBeVisible()
  })

  test('removes MP and returns to empty placeholder', async ({ page }) => {
    await installDashboardApiMocks(
      page,
      createDashboardMockState([{ politician_id: 'mp-1', role: 'MP' }]),
    )
    await signInAsTestUser(page)

    await expect(page.getByText('Narendra Modi').first()).toBeVisible({
      timeout: 15_000,
    })

    await page
      .getByRole('button', { name: 'Remove from your politicians' })
      .first()
      .click()

    await expect(
      page.getByRole('heading', { name: 'Add Your Local Politicians' }),
    ).toBeVisible()
    await expect(page.getByText('Search above to add')).toHaveCount(2)
  })

  test('shows pincode fallback when geolocation is unavailable', async ({
    context,
    page,
  }) => {
    await installDashboardApiMocks(page, createDashboardMockState())
    await context.clearPermissions()
    await signInAsTestUser(page)

    await expect(
      page.getByRole('heading', { name: 'Add Your Local Politicians' }),
    ).toBeVisible({ timeout: 15_000 })

    await page
      .getByRole('button', { name: 'Use location to find by pincode' })
      .click()

    await expect(page.getByPlaceholder('Enter pincode')).toBeVisible()
    await expect(
      page.getByRole('button', { name: 'Search on Google' }),
    ).toBeVisible()
  })
})
