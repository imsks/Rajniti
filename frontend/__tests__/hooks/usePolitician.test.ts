/**
 * Unit tests for usePolitician — single profile fetch by slug or UUID.
 */
import { renderHook, waitFor } from '@testing-library/react'
import { usePolitician } from '@/hooks/usePoliticians'
import type { Politician } from '@/types/politician'
import { createMockResponse } from '../../jest.setup'

const politician: Politician = {
    id: 'ef8a4654-1d09-4a06-bae7-14377bc08387',
    name: 'NARENDRA MODI',
    slug: 'narendra-modi',
    state: 'Gujarat',
    constituency: 'Varanasi',
    type: 'MP',
    political_background: {
        elections: [
            { year: 2024, type: 'LS', state: 'UP', constituency: 'V', party: 'BJP', status: 'WON' },
        ],
    },
}

describe('usePolitician', () => {
    it('loads politician by slug', async () => {
        ;(global.fetch as jest.Mock).mockResolvedValueOnce(
            createMockResponse({ success: true, data: politician })
        )
        const { result } = renderHook(() => usePolitician('narendra-modi'))

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(result.current.politician?.name).toBe('NARENDRA MODI')
        expect(result.current.error).toBeNull()
        expect(String((global.fetch as jest.Mock).mock.calls[0][0])).toContain(
            '/politicians/slug/narendra-modi'
        )
    })

    it('falls back to UUID when slug misses', async () => {
        const uuid = politician.id
        ;(global.fetch as jest.Mock)
            .mockResolvedValueOnce(createMockResponse({ success: false }, false, 404))
            .mockResolvedValueOnce(createMockResponse({ success: true, data: politician }))
        const { result } = renderHook(() => usePolitician(uuid))

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(result.current.politician?.id).toBe(uuid)
        expect(global.fetch).toHaveBeenCalledTimes(2)
    })

    it('sets error when slug misses and segment is not a UUID', async () => {
        ;(global.fetch as jest.Mock).mockResolvedValueOnce(
            createMockResponse({ success: false }, false, 404)
        )
        const { result } = renderHook(() => usePolitician('unknown-person'))

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(result.current.politician).toBeNull()
        expect(result.current.error).toBe('Politician not found')
    })

    it('sets not found when slug fetch fails (network errors are swallowed on slug path)', async () => {
        ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network down'))
        const { result } = renderHook(() => usePolitician('narendra-modi'))

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(result.current.error).toBe('Politician not found')
    })

    it('does not fetch when id is null', async () => {
        const { result } = renderHook(() => usePolitician(null))
        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(global.fetch).not.toHaveBeenCalled()
        expect(result.current.politician).toBeNull()
    })
})
