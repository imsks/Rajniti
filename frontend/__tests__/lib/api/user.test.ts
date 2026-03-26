/**
 * Unit tests for userService API functions.
 *
 * Verifies URL paths, HTTP methods, request bodies, and error handling.
 * The env var must be set before the module is required (imports are hoisted).
 */

const API_BASE = 'http://localhost:8000/api/v1'

let userService: typeof import('@/lib/api/user')['userService']
let mockFetch: jest.Mock

beforeAll(() => {
    process.env.NEXT_PUBLIC_API_URL = API_BASE
    jest.resetModules()
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    userService = require('@/lib/api/user').userService
    mockFetch = global.fetch as jest.Mock
})

beforeEach(() => {
    mockFetch.mockReset()
})

function okResponse(data: unknown) {
    return { ok: true, status: 200, json: () => Promise.resolve(data) }
}

function errorResponse(body: unknown, status = 500) {
    return { ok: false, status, statusText: 'Error', json: () => Promise.resolve(body) }
}

// ---------------------------------------------------------------------------
// syncUser
// ---------------------------------------------------------------------------
describe('userService.syncUser', () => {
    it('calls the /api/v1/users/sync endpoint', async () => {
        mockFetch.mockResolvedValueOnce(okResponse({ success: true }))

        await userService.syncUser({ id: 'u1', email: 'a@b.com' })

        expect(mockFetch).toHaveBeenCalledWith(
            `${API_BASE}/users/sync`,
            expect.any(Object),
        )
    })

    it('sends POST with JSON content-type and serialized body', async () => {
        const userData = { id: 'u1', email: 'a@b.com', name: 'Test' }
        mockFetch.mockResolvedValueOnce(okResponse({ success: true, data: userData }))

        await userService.syncUser(userData)

        const [, opts] = mockFetch.mock.calls[0]
        expect(opts.method).toBe('POST')
        expect(opts.headers['Content-Type']).toBe('application/json')
        expect(JSON.parse(opts.body)).toEqual(userData)
    })

    it('returns parsed JSON on success', async () => {
        const payload = { success: true, data: { id: 'u1' } }
        mockFetch.mockResolvedValueOnce(okResponse(payload))

        const result = await userService.syncUser({ id: 'u1', email: 'a@b.com' })
        expect(result).toEqual(payload)
    })

    it('throws when response is not ok', async () => {
        mockFetch.mockResolvedValueOnce(errorResponse({}, 500))

        await expect(
            userService.syncUser({ id: 'u1', email: 'a@b.com' }),
        ).rejects.toThrow(/Failed to sync user/)
    })
})

// ---------------------------------------------------------------------------
// updateUser
// ---------------------------------------------------------------------------
describe('userService.updateUser', () => {
    it('calls /users/{userId} with PATCH', async () => {
        mockFetch.mockResolvedValueOnce(okResponse({ success: true }))

        await userService.updateUser('user-42', { name: 'Updated' })

        const [url, opts] = mockFetch.mock.calls[0]
        expect(url).toBe(`${API_BASE}/users/user-42`)
        expect(opts.method).toBe('PATCH')
    })

    it('sends political_ideology (not political_interest)', async () => {
        const data = {
            username: 'raj',
            political_ideology: 'Centrist',
            onboarding_completed: true as const,
        }
        mockFetch.mockResolvedValueOnce(okResponse({ success: true, data }))

        await userService.updateUser('u1', data)

        const body = JSON.parse(mockFetch.mock.calls[0][1].body)
        expect(body).toHaveProperty('political_ideology', 'Centrist')
        expect(body).not.toHaveProperty('political_interest')
    })

    it('returns parsed JSON on success', async () => {
        const payload = { success: true, data: { id: 'u1', name: 'New' } }
        mockFetch.mockResolvedValueOnce(okResponse(payload))

        const result = await userService.updateUser('u1', { name: 'New' })
        expect(result).toEqual(payload)
    })

    it('throws with backend error message on failure', async () => {
        mockFetch.mockResolvedValueOnce(
            errorResponse({ error: 'Username is already taken' }, 400),
        )

        await expect(
            userService.updateUser('u1', { username: 'taken' }),
        ).rejects.toThrow('Username is already taken')
    })
})

// ---------------------------------------------------------------------------
// checkUsername
// ---------------------------------------------------------------------------
describe('userService.checkUsername', () => {
    it('calls /users/check-username with POST', async () => {
        mockFetch.mockResolvedValueOnce(okResponse({ available: true }))

        await userService.checkUsername('testuser')

        const [url, opts] = mockFetch.mock.calls[0]
        expect(url).toBe(`${API_BASE}/users/check-username`)
        expect(opts.method).toBe('POST')
    })

    it('sends username and optional user_id in body', async () => {
        mockFetch.mockResolvedValueOnce(okResponse({ available: true }))

        await userService.checkUsername('raj', 'user-99')

        const body = JSON.parse(mockFetch.mock.calls[0][1].body)
        expect(body).toEqual({ username: 'raj', user_id: 'user-99' })
    })

    it('omits user_id when not provided', async () => {
        mockFetch.mockResolvedValueOnce(okResponse({ available: true }))

        await userService.checkUsername('raj')

        const body = JSON.parse(mockFetch.mock.calls[0][1].body)
        expect(body.username).toBe('raj')
        expect(body.user_id).toBeUndefined()
    })

    it('returns availability result', async () => {
        mockFetch.mockResolvedValueOnce(okResponse({ available: false }))

        const result = await userService.checkUsername('taken')
        expect(result).toEqual({ available: false })
    })

    it('throws when response is not ok', async () => {
        mockFetch.mockResolvedValueOnce(errorResponse({}, 500))

        await expect(userService.checkUsername('test')).rejects.toThrow(
            'Failed to check username',
        )
    })
})
