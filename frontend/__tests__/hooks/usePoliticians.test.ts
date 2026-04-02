/**
 * Unit tests for usePoliticians — dashboard data loading and client-side filtering.
 */
import { renderHook, waitFor, act } from '@testing-library/react'
import { usePoliticians } from '@/hooks/usePoliticians'
import type { Politician } from '@/types/politician'

const mk = (over: Partial<Politician> & Pick<Politician, 'id' | 'name' | 'state' | 'constituency' | 'type'>): Politician => ({
    political_background: { elections: [{ year: 2024, type: 'G', state: 'X', constituency: 'C', party: 'AAA', status: 'Won' }] },
    ...over,
})

const sampleList: Politician[] = [
    mk({ id: '1', name: 'Alpha Singh', state: 'Maharashtra', constituency: 'Mumbai', type: 'MP', political_background: { elections: [{ year: 2024, type: 'G', state: 'MH', constituency: 'Mumbai', party: 'BJP', status: 'Won' }] }, performance: { attendance: 90, questions: 10, debates: 2 } }),
    mk({ id: '2', name: 'Beta Rao', state: 'Karnataka', constituency: 'Bengaluru', type: 'MLA', political_background: { elections: [{ year: 2023, type: 'A', state: 'KA', constituency: 'BLR', party: 'INC', status: 'Won' }] }, performance: { attendance: 70, questions: 5, debates: 1 } }),
    mk({ id: '3', name: 'Gamma Patel', state: 'Maharashtra', constituency: 'Pune', type: 'MLA', political_background: { elections: [{ year: 2023, type: 'A', state: 'MH', constituency: 'Pune', party: 'BJP', status: 'Won' }] } }),
]

function mockPoliticiansResponse(politicians: Politician[]) {
    ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () =>
            Promise.resolve({
                success: true,
                data: { politicians },
            }),
    })
}

describe('usePoliticians', () => {
    it('loads politicians and clears loading state', async () => {
        mockPoliticiansResponse(sampleList)
        const { result } = renderHook(() => usePoliticians())

        expect(result.current.loading).toBe(true)

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.all).toHaveLength(3)
        expect(result.current.error).toBeNull()
    })

    it('sets error when API returns success: false', async () => {
        ;(global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: () =>
                Promise.resolve({
                    success: false,
                    error: 'Bad request',
                }),
        })

        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(result.current.error).toBe('Bad request')
        expect(result.current.all).toHaveLength(0)
    })

    it('sets error on network failure', async () => {
        ;(global.fetch as jest.Mock).mockRejectedValue(new Error('Network down'))

        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(result.current.error).toBe('Cannot connect to API')
    })

    it('filter() narrows by search query (name)', async () => {
        mockPoliticiansResponse(sampleList)
        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))

        const filtered = result.current.filter({ query: 'beta' })
        expect(filtered).toHaveLength(1)
        expect(filtered[0].name).toBe('Beta Rao')
    })

    it('filter() narrows by state', async () => {
        mockPoliticiansResponse(sampleList)
        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))

        const filtered = result.current.filter({ state: 'Maharashtra' })
        expect(filtered).toHaveLength(2)
    })

    it('filter() narrows by party', async () => {
        mockPoliticiansResponse(sampleList)
        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))

        const filtered = result.current.filter({ party: 'BJP' })
        expect(filtered).toHaveLength(2)
    })

    it('stats reflect list totals and top party', async () => {
        mockPoliticiansResponse(sampleList)
        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))

        expect(result.current.stats.total).toBe(3)
        expect(result.current.stats.totalStates).toBe(2)
        expect(result.current.stats.totalParties).toBe(2)
        expect(result.current.stats.topParty).toBe('BJP')
    })

    it('refetch() triggers another fetch', async () => {
        mockPoliticiansResponse(sampleList)
        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(global.fetch).toHaveBeenCalledTimes(1)

        mockPoliticiansResponse([sampleList[0]])
        await act(async () => {
            await result.current.refetch()
        })

        await waitFor(() => expect(result.current.all).toHaveLength(1))
        expect(global.fetch).toHaveBeenCalledTimes(2)
    })
})
