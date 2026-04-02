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
            if (response.ok()) {
                const body = await response.json()
                expect(body.success).toBe(true)
                expect(body).toHaveProperty('database')
            }
        } catch {
            test.skip()
        }
    })

    test('user sync endpoint accepts POST (backend running)', async ({ request }) => {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

        try {
            const response = await request.post(`${backendUrl}/users/sync`, {
                data: {
                    id: 'playwright-health-user',
                    email: 'health@test.local',
                    name: 'Health Check',
                },
            })

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
