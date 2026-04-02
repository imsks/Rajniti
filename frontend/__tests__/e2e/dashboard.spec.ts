import { test, expect } from '@playwright/test'

/**
 * Browser tests around the dashboard and other auth-guarded routes (unauthenticated).
 * Full dashboard UI requires Google OAuth; here we assert middleware / auth redirects.
 */
test.describe('Dashboard & protected routes (unauthenticated)', () => {
    test('redirects /dashboard to sign-in', async ({ page }) => {
        await page.goto('/dashboard')
        await expect(page).toHaveURL(/\/auth\/signin/)
    })

    test('redirects nested /dashboard path to sign-in', async ({ page }) => {
        await page.goto('/dashboard/extra')
        await expect(page).toHaveURL(/\/auth\/signin/)
    })

    test('redirects /profile/edit to sign-in', async ({ page }) => {
        await page.goto('/profile/edit')
        await expect(page).toHaveURL(/\/auth\/signin/)
    })

    test('redirects /onboarding to sign-in when not logged in', async ({ page }) => {
        await page.goto('/onboarding')
        await expect(page).toHaveURL(/\/auth\/signin/)
    })

    test('home page loads hero heading', async ({ page }) => {
        await page.goto('/')
        await expect(
            page.getByRole('heading', { name: /know your/i }),
        ).toBeVisible({ timeout: 10_000 })
    })

    test('home page shows Sign In in navbar', async ({ page }) => {
        await page.goto('/')
        await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible({
            timeout: 10_000,
        })
    })
})
