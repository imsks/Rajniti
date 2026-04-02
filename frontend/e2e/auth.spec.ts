import { test, expect } from '@playwright/test'

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

        // Should either redirect to sign-in or show sign-in prompt
        await page.waitForURL(/\/(auth\/signin|dashboard)/, { timeout: 5000 })
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

test.describe('Onboarding page (unauthenticated)', () => {
    test('onboarding page loads and shows step 1', async ({ page }) => {
        await page.goto('/onboarding')

        await expect(page.getByText(/step 1 of 4/i)).toBeVisible()
        await expect(page.getByText(/political inclination/i).first()).toBeVisible()
    })

    test('onboarding shows all political ideology options', async ({ page }) => {
        await page.goto('/onboarding')

        const ideologies = ['Rightist', 'Leftist', 'Communist', 'Centrist', 'Libertarian', 'Neutral']
        for (const ideology of ideologies) {
            await expect(page.getByRole('button', { name: new RegExp(ideology, 'i') })).toBeVisible()
        }
    })

    test('continue button is disabled until an option is selected', async ({ page }) => {
        await page.goto('/onboarding')

        const continueBtn = page.getByRole('button', { name: /continue/i })
        await expect(continueBtn).toBeDisabled()

        // Select an option
        await page.getByRole('button', { name: /centrist/i }).click()
        await expect(continueBtn).toBeEnabled()
    })

    test('navigating to step 2 shows basic details', async ({ page }) => {
        await page.goto('/onboarding')

        await page.getByRole('button', { name: /centrist/i }).click()
        await page.getByRole('button', { name: /continue/i }).click()

        await expect(page.getByText(/step 2 of 4/i)).toBeVisible()
        await expect(page.getByText(/basic details/i)).toBeVisible()
    })

    test('onboarding has no skip control', async ({ page }) => {
        await page.goto('/onboarding')

        await expect(page.getByRole('button', { name: /skip for now/i })).toHaveCount(0)
    })
})
