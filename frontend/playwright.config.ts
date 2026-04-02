import { defineConfig, devices } from '@playwright/test'

/**
 * Next.js only allows one `next dev` per project (`.next/dev/lock`).
 * Always reuse a server already listening on :3000 so local runs don't spawn a
 * second dev process while you have `npm run dev` open. CI runners start cold,
 * so nothing is listening and a single dev server is started as usual.
 */
const devServerUrl = 'http://127.0.0.1:3000'

export default defineConfig({
    testDir: './__tests__/e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'html',
    use: {
        baseURL: devServerUrl,
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
        url: devServerUrl,
        reuseExistingServer: true,
        timeout: 120_000,
    },
})
