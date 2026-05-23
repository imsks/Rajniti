import { renderHook, act } from "@testing-library/react"
import { useDeferredMount } from "@/hooks/useDeferredMount"

describe("useDeferredMount", () => {
    beforeEach(() => {
        jest.useFakeTimers()
    })

    afterEach(() => {
        jest.useRealTimers()
    })

    it("starts false then becomes true after idle timeout fallback", () => {
        const { result } = renderHook(() => useDeferredMount(2000))

        expect(result.current).toBe(false)

        act(() => {
            jest.advanceTimersByTime(100)
        })

        expect(result.current).toBe(true)
    })
})
