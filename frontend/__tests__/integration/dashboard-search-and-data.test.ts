/**
 * Integration-style tests: dashboard-related hooks (list + debounced search).
 */
import { renderHook, waitFor, act } from '@testing-library/react'
import { usePoliticians } from '@/hooks/usePoliticians'
import { usePoliticianSearch } from '@/hooks/usePoliticianSearch'
import type { Politician } from '@/types/politician'

const politician: Politician = {
    id: 'p1',
    name: 'Searchable Name',
    state: 'Goa',
    constituency: 'North Goa',
    type: 'MP',
    political_background: {
        elections: [
            { year: 2024, type: 'G', state: 'Goa', constituency: 'North Goa', party: 'X', status: 'Won' },
        ],
    },
}

describe('dashboard data + search integration', () => {
    beforeEach(() => {
        jest.useFakeTimers({ advanceTimers: true })
    })

    afterEach(() => {
        jest.useRealTimers()
    })

    it('usePoliticians + usePoliticianSearch can run in parallel hooks with separate fetch URLs', async () => {
        ;(global.fetch as jest.Mock).mockImplementation((url: string) => {
            if (String(url).includes('/politicians?')) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve({
                            success: true,
                            data: { politicians: [politician] },
                        }),
                })
            }
            if (String(url).includes('/politicians/search')) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve({
                            success: true,
                            data: { politicians: [politician] },
                        }),
                })
            }
            return Promise.reject(new Error('unexpected url'))
        })

        const listHook = renderHook(() => usePoliticians())
        const searchHook = renderHook(() => usePoliticianSearch('ab'))

        await waitFor(() => expect(listHook.result.current.loading).toBe(false))
        expect(listHook.result.current.all).toHaveLength(1)

        await act(async () => {
            jest.advanceTimersByTime(1600)
        })

        await waitFor(() => {
            expect(searchHook.result.current.results.length).toBeGreaterThanOrEqual(1)
        })
    })

    it('usePoliticianSearch does not fetch when query is too short', async () => {
        ;(global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ success: true, data: { politicians: [] } }),
        })

        const { result, rerender } = renderHook(({ q }: { q: string }) => usePoliticianSearch(q), {
            initialProps: { q: 'a' },
        })

        await act(async () => {
            jest.advanceTimersByTime(2000)
        })

        expect(result.current.results).toEqual([])
        expect(global.fetch).not.toHaveBeenCalled()

        rerender({ q: 'ab' })
        await act(async () => {
            jest.advanceTimersByTime(1600)
        })

        await waitFor(() => expect(global.fetch).toHaveBeenCalled())
    })

    it('usePoliticianSearch clears results when query drops below minimum length', async () => {
        const searchJson = {
            success: true,
            data: { politicians: [politician] },
        }
        ;(global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: () => Promise.resolve(searchJson),
        })

        const { result, rerender } = renderHook(({ q }: { q: string }) => usePoliticianSearch(q), {
            initialProps: { q: 'ab' },
        })

        await act(async () => {
            jest.advanceTimersByTime(1600)
        })
        await waitFor(() => expect(result.current.results).toHaveLength(1))

        rerender({ q: 'a' })
        await waitFor(() => expect(result.current.results).toEqual([]))
    })

    it('usePoliticianSearch surfaces error when search fetch throws', async () => {
        ;(global.fetch as jest.Mock).mockRejectedValue(new Error('fail'))

        const { result } = renderHook(() => usePoliticianSearch('query'))

        await act(async () => {
            jest.advanceTimersByTime(1600)
        })

        await waitFor(() => {
            expect(result.current.error).toBe('Search failed')
        })
    })

    it('usePoliticians states and parties lists are sorted', async () => {
        const p2: Politician = {
            ...politician,
            id: 'p2',
            name: 'Other',
            state: 'Assam',
            political_background: {
                elections: [
                    { year: 2024, type: 'G', state: 'AS', constituency: 'X', party: 'Zebra', status: 'Won' },
                ],
            },
        }
        ;(global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: () =>
                Promise.resolve({
                    success: true,
                    data: { politicians: [politician, p2] },
                }),
        })

        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))

        expect(result.current.states).toEqual(['Assam', 'Goa'])
        expect(result.current.parties).toEqual(['X', 'Zebra'])
    })

    it('usePoliticians filter combines query + state', async () => {
        const mh: Politician = {
            ...politician,
            id: 'mh',
            state: 'Maharashtra',
            name: 'Mumbai MP',
            political_background: {
                elections: [
                    { year: 2024, type: 'G', state: 'MH', constituency: 'Mumbai', party: 'P1', status: 'Won' },
                ],
            },
        }
        const ka: Politician = {
            ...politician,
            id: 'ka',
            state: 'Karnataka',
            name: 'Mumbai Street MLA',
            political_background: {
                elections: [
                    { year: 2024, type: 'A', state: 'KA', constituency: 'B', party: 'P2', status: 'Won' },
                ],
            },
        }
        ;(global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: () =>
                Promise.resolve({
                    success: true,
                    data: { politicians: [mh, ka] },
                }),
        })

        const { result } = renderHook(() => usePoliticians())

        await waitFor(() => expect(result.current.loading).toBe(false))

        const onlyMaharashtraMumbai = result.current.filter({
            query: 'mumbai',
            state: 'Maharashtra',
        })
        expect(onlyMaharashtraMumbai).toHaveLength(1)
        expect(onlyMaharashtraMumbai[0].id).toBe('mh')
    })
})
