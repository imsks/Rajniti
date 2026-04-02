import { test, expect } from '@playwright/test'
import { loginWithE2E, mockPoliticianApi } from './helpers'

test.describe('Dashboard — search & my politicians', () => {
    test.beforeEach(async ({ page }) => {
        await mockPoliticianApi(page)
        await loginWithE2E(page)
    })

    test('filters the main grid when searching by politician name', async ({
        page,
    }) => {
        await page
            .getByPlaceholder(/search by name, constituency, state or party/i)
            .fill('E2E Test MP')

        await expect(
            page.getByRole('link', { name: /E2E Test MP/i }).first(),
        ).toBeVisible()
        await expect(page.getByText(/E2E Test MLA/i)).toHaveCount(0)
    })

    test('my politicians search shows API results after debounce', async ({
        page,
    }) => {
        const search = page.locator('#my-politicians-search')
        await search.fill('E2E Test')
        await expect(
            page.getByRole('button', { name: /E2E Test MP/i }),
        ).toBeVisible({ timeout: 5_000 })
        await expect(
            page.getByRole('button', { name: /E2E Test MLA/i }),
        ).toBeVisible()
    })

    test('adds local MP from search dropdown', async ({ page }) => {
        const search = page.locator('#my-politicians-search')
        await search.fill('E2E Test MP')
        await page.getByRole('button', { name: /E2E Test MP/i }).click()

        await expect(page.getByText('E2E Test MP').first()).toBeVisible()
        await expect(page.getByText(/MP of New Delhi/i)).toBeVisible()
    })

    test('adds local MLA from search dropdown', async ({ page }) => {
        const search = page.locator('#my-politicians-search')
        await search.fill('E2E Test MLA')
        await page.getByRole('button', { name: /E2E Test MLA/i }).click()

        await expect(page.getByText('E2E Test MLA').first()).toBeVisible()
        await expect(page.getByText(/MLA of Test Assembly/i)).toBeVisible()
    })
})
