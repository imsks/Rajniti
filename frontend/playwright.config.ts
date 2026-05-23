import { defineConfig, devices } from '@playwright/test'

/**
 * Next.js only allows one `next dev` per project (`.next/dev/lock`).
 * Reuse a server already listening on the base URL in local runs.
 */
const devServerUrl =
    process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000'
const skipWebServer = process.env.PLAYWRIGHT_SKIP_WEB_SERVER === 'true'

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
    webServer: skipWebServer
        ? undefined
        : {
              command: 'npm run dev',
              url: devServerUrl,
              reuseExistingServer: process.env.PLAYWRIGHT_REUSE_SERVER === 'true',
              timeout: 120_000,
              env: {
                  ...process.env,
                  ENABLE_TEST_AUTH: 'true',
                  NEXT_PUBLIC_ENABLE_TEST_AUTH: 'true',
                  NEXTAUTH_URL: devServerUrl,
                  NEXTAUTH_SECRET:
                      process.env.NEXTAUTH_SECRET ||
                      'local-playwright-e2e-secret-min-32-chars',
              },
          },
})
