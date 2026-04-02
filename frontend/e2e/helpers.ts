import type { Page } from '@playwright/test'

/** Minimal politicians matching app types; used to mock the REST API in E2E. */
const MOCK_POLITICIANS = [
    {
        id: 'e2e-mp-1',
        name: 'E2E Test MP',
        state: 'Delhi',
        constituency: 'New Delhi',
        type: 'MP' as const,
        political_background: {
            elections: [
                {
                    year: 2024,
                    type: 'General',
                    state: 'Delhi',
                    constituency: 'New Delhi',
                    party: 'TEST',
                    status: 'Won',
                },
            ],
        },
        performance: { attendance: 90, questions: 10, debates: 5 },
    },
    {
        id: 'e2e-mla-1',
        name: 'E2E Test MLA',
        state: 'Delhi',
        constituency: 'Test Assembly',
        type: 'MLA' as const,
        political_background: {
            elections: [
                {
                    year: 2024,
                    type: 'Assembly',
                    state: 'Delhi',
                    constituency: 'Test Assembly',
                    party: 'TEST',
                    status: 'Won',
                },
            ],
        },
        performance: { attendance: 80, questions: 5, debates: 3 },
    },
]

const LIST_RESPONSE = {
    success: true,
    data: { politicians: MOCK_POLITICIANS },
}

/**
 * Stubs backend politician endpoints so dashboard E2E does not require a running API.
 */
export async function mockPoliticianApi(page: Page) {
    await page.route('**/api/v1/politicians?**', async (route) => {
        if (route.request().method() !== 'GET') {
            await route.continue()
            return
        }
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(LIST_RESPONSE),
        })
    })

    await page.route('**/api/v1/politicians/search?**', async (route) => {
        if (route.request().method() !== 'GET') {
            await route.continue()
            return
        }
        const url = new URL(route.request().url())
        const q = (url.searchParams.get('q') ?? '').toLowerCase().trim()
        const filtered = MOCK_POLITICIANS.filter((p) =>
            p.name.toLowerCase().includes(q),
        )
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
                success: true,
                data: { politicians: filtered },
            }),
        })
    })
}

/**
 * Signs in with the E2E credentials provider (server must have E2E_AUTH=true).
 * Uses the NextAuth CSRF + callback POST so tests do not depend on the optional
 * "Continue with E2E Test Account" UI button.
 */
export async function loginWithE2E(page: Page) {
    await page.goto('/auth/signin')
    await page.evaluate(async () => {
        const csrfRes = await fetch('/api/auth/csrf')
        const { csrfToken } = (await csrfRes.json()) as { csrfToken: string }
        const origin = window.location.origin
        const res = await fetch(
            `${origin}/api/auth/callback/e2e-credentials`,
            {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    csrfToken,
                    callbackUrl: `${origin}/dashboard`,
                }).toString(),
            },
        )
        if (!res.ok) {
            throw new Error(`E2E sign-in failed: HTTP ${res.status}`)
        }
    })
    await page.goto('/dashboard')
    await page.waitForURL(/\/dashboard/, { timeout: 15_000 })
}
