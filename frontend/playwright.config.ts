import { defineConfig, devices } from '@playwright/test'

/**
 * E2E uses a Credentials provider when E2E_AUTH=true (see NextAuth route).
 * - CI: starts `npm run dev` with E2E_AUTH set.
 * - Local: if something already serves :3000, it is reused — that server must
 *   be started with `E2E_AUTH=true` or sign-in tests will fail.
 */
export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'html',
    use: {
        baseURL: 'http://localhost:3000',
        trace: 'on-first-retry',
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],
    webServer: {
        command: 'npm run dev',
        url: 'http://localhost:3000',
        // Local: reuse your running `next dev` (must set E2E_AUTH=true). CI starts a fresh server.
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
        env: {
            ...process.env,
            E2E_AUTH: 'true',
            NEXT_PUBLIC_E2E_AUTH: 'true',
        },
    },
})
