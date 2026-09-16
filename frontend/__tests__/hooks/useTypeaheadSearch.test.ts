import { renderHook, act, waitFor } from "@testing-library/react"

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

// Reset mocks before each test
beforeEach(() => {
    mockFetch.mockClear()
    jest.useFakeTimers()
})

afterEach(() => {
    jest.useRealTimers()
})

// Import after setting up mocks
import { useTypeaheadSearch } from "@/hooks/useTypeaheadSearch"

describe("useTypeaheadSearch", () => {
    it("returns empty results for short queries (< 2 non-space chars)", () => {
        const { result } = renderHook(() => useTypeaheadSearch("a"))

        expect(result.current.results).toEqual([])
        expect(result.current.loading).toBe(false)
        expect(result.current.error).toBe(null)
    })

    it("returns empty results for whitespace-only queries", () => {
        const { result } = renderHook(() => useTypeaheadSearch("   "))

        expect(result.current.results).toEqual([])
        expect(result.current.loading).toBe(false)
    })

    it("does not fetch until debounce delay", async () => {
        const { result, rerender } = renderHook(
            ({ query }) => useTypeaheadSearch(query),
            { initialProps: { query: "" } },
        )

        // Set query to trigger search
        rerender({ query: "modi" })

        // Should show loading but not have fetched yet
        expect(result.current.loading).toBe(true)
        expect(mockFetch).not.toHaveBeenCalled()

        // Fast-forward past debounce
        await act(async () => {
            jest.advanceTimersByTime(300)
        })

        // Now fetch should have been called
        expect(mockFetch).toHaveBeenCalled()
    })

    it("fetches results after debounce", async () => {
        const mockPoliticians = [
            { id: "1", name: "NARENDRA MODI", type: "MP", slug: "narendra-modi" },
        ]

        mockFetch.mockResolvedValueOnce({
            ok: true,
            json: () =>
                Promise.resolve({
                    success: true,
                    data: { politicians: mockPoliticians },
                }),
        })

        const { result, rerender } = renderHook(
            ({ query }) => useTypeaheadSearch(query),
            { initialProps: { query: "" } },
        )

        rerender({ query: "modi" })

        await act(async () => {
            jest.advanceTimersByTime(300)
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.results).toEqual(mockPoliticians)
        expect(result.current.error).toBe(null)
    })

    it("clears results when query becomes too short", async () => {
        const mockPoliticians = [
            { id: "1", name: "NARENDRA MODI", type: "MP", slug: "narendra-modi" },
        ]

        mockFetch.mockResolvedValueOnce({
            ok: true,
            json: () =>
                Promise.resolve({
                    success: true,
                    data: { politicians: mockPoliticians },
                }),
        })

        const { result, rerender } = renderHook(
            ({ query }) => useTypeaheadSearch(query),
            { initialProps: { query: "modi" } },
        )

        await act(async () => {
            jest.advanceTimersByTime(300)
        })

        await waitFor(() => {
            expect(result.current.results).toHaveLength(1)
        })

        // Now clear the query
        rerender({ query: "" })

        expect(result.current.results).toEqual([])
        expect(result.current.loading).toBe(false)
    })

    it("uses custom debounce time", async () => {
        const { result, rerender } = renderHook(
            ({ query }) => useTypeaheadSearch(query, { debounceMs: 500 }),
            { initialProps: { query: "" } },
        )

        rerender({ query: "modi" })

        // Should not have fetched after default 300ms
        await act(async () => {
            jest.advanceTimersByTime(300)
        })
        expect(mockFetch).not.toHaveBeenCalled()

        // Should fetch after custom 500ms
        await act(async () => {
            jest.advanceTimersByTime(200)
        })
        expect(mockFetch).toHaveBeenCalled()
    })

    it("passes limit parameter to API", async () => {
        mockFetch.mockResolvedValueOnce({
            ok: true,
            json: () =>
                Promise.resolve({
                    success: true,
                    data: { politicians: [] },
                }),
        })

        const { rerender } = renderHook(
            ({ query }) => useTypeaheadSearch(query, { limit: 5 }),
            { initialProps: { query: "" } },
        )

        rerender({ query: "modi" })

        await act(async () => {
            jest.advanceTimersByTime(300)
        })

        expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining("limit=5"),
            expect.anything(),
        )
    })

    it("treats HTTP error statuses as failures without reading the body as success", async () => {
        const json = jest.fn()
        mockFetch.mockResolvedValueOnce({
            ok: false,
            status: 500,
            json,
        })

        const { result, rerender } = renderHook(
            ({ query }) => useTypeaheadSearch(query),
            { initialProps: { query: "" } },
        )

        rerender({ query: "modi" })

        await act(async () => {
            jest.advanceTimersByTime(300)
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(json).not.toHaveBeenCalled()
        expect(result.current.error).toBe("Search failed")
        expect(result.current.results).toEqual([])
    })

    it("handles API errors gracefully", async () => {
        mockFetch.mockRejectedValueOnce(new Error("Network error"))

        const { result, rerender } = renderHook(
            ({ query }) => useTypeaheadSearch(query),
            { initialProps: { query: "" } },
        )

        rerender({ query: "modi" })

        await act(async () => {
            jest.advanceTimersByTime(300)
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.error).toBe("Search failed")
        expect(result.current.results).toEqual([])
    })

    it("clear() resets all state", async () => {
        const mockPoliticians = [
            { id: "1", name: "NARENDRA MODI", type: "MP", slug: "narendra-modi" },
        ]

        mockFetch.mockResolvedValueOnce({
            ok: true,
            json: () =>
                Promise.resolve({
                    success: true,
                    data: { politicians: mockPoliticians },
                }),
        })

        const { result, rerender } = renderHook(
            ({ query }) => useTypeaheadSearch(query),
            { initialProps: { query: "modi" } },
        )

        await act(async () => {
            jest.advanceTimersByTime(300)
        })

        await waitFor(() => {
            expect(result.current.results).toHaveLength(1)
        })

        // Call clear
        act(() => {
            result.current.clear()
        })

        expect(result.current.results).toEqual([])
        expect(result.current.loading).toBe(false)
        expect(result.current.error).toBe(null)
    })
})
