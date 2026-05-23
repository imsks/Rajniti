/**
 * Unit tests for getApiBaseUrl (server vs client API base).
 */

describe('getApiBaseUrl', () => {
    const originalEnv = process.env

    beforeEach(() => {
        jest.resetModules()
        process.env = { ...originalEnv }
    })

    afterAll(() => {
        process.env = originalEnv
    })

    it('prefers API_URL on the server', async () => {
        process.env.API_URL = 'http://rajniti-api:8000/api/v1'
        process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api/v1'
        const { getApiBaseUrl } = await import('@/lib/api/api-base')
        expect(getApiBaseUrl({ forServer: true })).toBe('http://rajniti-api:8000/api/v1')
    })

    it('strips trailing slash from server URL', async () => {
        process.env.API_URL = 'http://rajniti-api:8000/api/v1/'
        const { getApiBaseUrl } = await import('@/lib/api/api-base')
        expect(getApiBaseUrl({ forServer: true })).toBe('http://rajniti-api:8000/api/v1')
    })

    it('uses Next proxy when only localhost NEXT_PUBLIC is set on server', async () => {
        delete process.env.API_URL
        delete process.env.INTERNAL_API_URL
        process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api/v1'
        process.env.PORT = '3000'
        const { getApiBaseUrl } = await import('@/lib/api/api-base')
        expect(getApiBaseUrl({ forServer: true })).toBe('http://127.0.0.1:3000/api/v1')
    })

    it('uses non-localhost NEXT_PUBLIC on server (e.g. production API)', async () => {
        delete process.env.API_URL
        process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com/api/v1'
        const { getApiBaseUrl } = await import('@/lib/api/api-base')
        expect(getApiBaseUrl({ forServer: true })).toBe('https://api.example.com/api/v1')
    })

    it('uses NEXT_PUBLIC_API_URL in the browser', async () => {
        process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000/api/v1'
        const { getApiBaseUrl } = await import('@/lib/api/api-base')
        expect(getApiBaseUrl({ forServer: false })).toBe('http://localhost:8000/api/v1')
    })

    it('falls back to localhost for browser when env vars are unset', async () => {
        delete process.env.API_URL
        delete process.env.INTERNAL_API_URL
        delete process.env.NEXT_PUBLIC_API_URL
        const { getApiBaseUrl } = await import('@/lib/api/api-base')
        expect(getApiBaseUrl({ forServer: false })).toBe('http://localhost:8000/api/v1')
    })
})
