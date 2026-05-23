/**
 * Unit tests for politicians-server fetch helpers.
 */

import type { Politician } from '@/types/politician'
import { createMockResponse, mockNetworkError } from '../../../jest.setup'

const politician: Politician = {
    id: 'ef8a4654-1d09-4a06-bae7-14377bc08387',
    name: 'NARENDRA MODI',
    slug: 'narendra-modi',
    state: 'Gujarat',
    constituency: 'Varanasi',
    type: 'MP',
    political_background: {
        elections: [
            {
                year: 2024,
                type: 'LS',
                state: 'UP',
                constituency: 'Varanasi',
                party: 'BJP',
                status: 'WON',
            },
        ],
    },
}

describe('fetchPoliticianBySegment', () => {
    beforeEach(() => {
        jest.resetModules()
        process.env.API_URL = 'http://test-api:8000/api/v1'
    })

    it('returns politician when slug endpoint succeeds', async () => {
        ;(global.fetch as jest.Mock).mockResolvedValueOnce(
            createMockResponse({ success: true, data: politician })
        )
        const { fetchPoliticianBySegment } = await import('@/lib/api/politicians-server')
        const result = await fetchPoliticianBySegment('narendra-modi')
        expect(result?.name).toBe('NARENDRA MODI')
        expect(String((global.fetch as jest.Mock).mock.calls[0][0])).toContain(
            '/politicians/slug/narendra-modi'
        )
        expect((global.fetch as jest.Mock).mock.calls[0][1]).toEqual({
            next: {
                revalidate: 3600,
                tags: ['politician-narendra-modi'],
            },
        })
    })

    it('falls back to UUID lookup when slug misses', async () => {
        const uuid = 'ef8a4654-1d09-4a06-bae7-14377bc08387'
        ;(global.fetch as jest.Mock)
            .mockResolvedValueOnce(createMockResponse({ success: false }, false, 404))
            .mockResolvedValueOnce(createMockResponse({ success: true, data: politician }))
        const { fetchPoliticianBySegment } = await import('@/lib/api/politicians-server')
        const result = await fetchPoliticianBySegment(uuid)
        expect(result?.id).toBe(uuid)
        expect(global.fetch).toHaveBeenCalledTimes(2)
    })

    it('returns null when slug and id lookups fail without network error', async () => {
        ;(global.fetch as jest.Mock).mockResolvedValue(
            createMockResponse({ success: false, error: 'not found' }, false, 404)
        )
        const { fetchPoliticianBySegment } = await import('@/lib/api/politicians-server')
        const result = await fetchPoliticianBySegment('unknown-slug')
        expect(result).toBeNull()
    })

    it('throws PoliticianApiUnreachableError on network failure', async () => {
        mockNetworkError()
        const { fetchPoliticianBySegment, PoliticianApiUnreachableError } =
            await import('@/lib/api/politicians-server')
        await expect(fetchPoliticianBySegment('narendra-modi')).rejects.toBeInstanceOf(
            PoliticianApiUnreachableError
        )
    })

    it('handles non-JSON slug response without throwing', async () => {
        ;(global.fetch as jest.Mock).mockResolvedValueOnce({
            ok: false,
            status: 502,
            json: () => Promise.reject(new Error('invalid json')),
        })
        const { fetchPoliticianBySegment } = await import('@/lib/api/politicians-server')
        const result = await fetchPoliticianBySegment('narendra-modi')
        expect(result).toBeNull()
    })
})
