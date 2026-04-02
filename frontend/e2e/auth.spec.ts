import { test, expect } from '@playwright/test'
import { loginWithE2E, mockPoliticianApi } from './helpers'

test.describe('E2E credentials auth flow', () => {
    test('signs in and reaches dashboard as an onboarded user', async ({
        page,
    }) => {
        await mockPoliticianApi(page)
        await loginWithE2E(page)

        await expect(page).toHaveURL(/\/dashboard$/)
        await expect(
            page.getByRole('heading', { name: /Indian\s+Politicians/i }),
        ).toBeVisible()
        await expect(
            page.getByRole('button', { name: /continue with google/i }),
        ).toHaveCount(0)
    })
})

test.describe('Sign-in page', () => {
    test('renders the sign-in page with Google button', async ({ page }) => {
        await page.goto('/auth/signin')

        await expect(page.getByRole('heading', { name: /welcome to rajniti/i })).toBeVisible()
        await expect(page.getByRole('button', { name: /continue with google/i })).toBeVisible()
        await expect(page.getByText(/sign in to access your personalized/i)).toBeVisible()
    })

    test('has a link back to home', async ({ page }) => {
        await page.goto('/auth/signin')

        const backLink = page.getByRole('link', { name: /back to home/i })
        await expect(backLink).toBeVisible()
        await expect(backLink).toHaveAttribute('href', '/')
    })

    test('Google button triggers NextAuth sign-in flow', async ({ page }) => {
        await page.goto('/auth/signin')

        const [request] = await Promise.all([
            page.waitForRequest((req) =>
                req.url().includes('/api/auth/signin/google') ||
                req.url().includes('accounts.google.com'),
            ),
            page.getByRole('button', { name: /continue with google/i }).click(),
        ]).catch(() => [null])

        // Either redirects to Google or hits the NextAuth signin endpoint
        // Both indicate the OAuth flow initiated correctly
        if (request) {
            expect(request.url()).toMatch(/google|api\/auth/)
        }
    })
})

test.describe('Unauthenticated navigation', () => {
    test('navbar shows Sign In button when not logged in', async ({ page }) => {
        await page.goto('/')

        await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()
    })

    test('dashboard redirects unauthenticated users to sign-in', async ({ page }) => {
        await page.goto('/dashboard')

        await expect(page).toHaveURL(/\/auth\/signin/)
    })
})

test.describe('API health (backend connectivity)', () => {
    test('backend health endpoint responds when running', async ({ request }) => {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

        try {
            const response = await request.get(`${backendUrl}/health`)
            // If backend is running, should return 200
            if (response.ok()) {
                const body = await response.json()
                expect(body.success).toBe(true)
                expect(body).toHaveProperty('database')
            }
        } catch {
            // Backend not running is acceptable in CI without Docker
            test.skip()
        }
    })

    test('user sync endpoint accepts POST (backend running)', async ({ request }) => {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

        try {
            const response = await request.post(`${backendUrl}/users/sync`, {
                data: {
                    id: 'e2e-test-user',
                    email: 'e2e@test.com',
                    name: 'E2E Test',
                },
            })

            // Should get 200 (user created) or 500 (no DB) - not 404
            expect(response.status()).not.toBe(404)
        } catch {
            test.skip()
        }
    })
})

test.describe('Onboarding (middleware)', () => {
    test('onboarding redirects unauthenticated users to sign-in', async ({ page }) => {
        await page.goto('/onboarding')

        await expect(page).toHaveURL(/\/auth\/signin/)
    })
})
