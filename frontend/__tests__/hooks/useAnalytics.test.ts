import { renderHook, act } from "@testing-library/react"
import { useAnalytics } from "@/hooks/useAnalytics"
import { event } from "@/lib/analytics"

jest.mock("@/lib/analytics", () => ({
  event: jest.fn(),
}))

describe("useAnalytics", () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it("trackEvent forwards typed events to analytics", () => {
    const { result } = renderHook(() => useAnalytics())

    act(() => {
      result.current.trackEvent("signin_page_view", { referrer: "direct" })
    })

    expect(event).toHaveBeenCalledWith("signin_page_view", {
      referrer: "direct",
    })
  })

  it("trackSearch debounces search events", () => {
    const { result } = renderHook(() => useAnalytics())

    act(() => {
      result.current.trackSearch("modi", "dashboard", 3)
    })

    expect(event).not.toHaveBeenCalled()

    act(() => {
      jest.advanceTimersByTime(800)
    })

    expect(event).toHaveBeenCalledWith("search", {
      search_term: "modi",
      results_count: 3,
      search_location: "dashboard",
    })
  })

  it("trackSearch ignores blank terms", () => {
    const { result } = renderHook(() => useAnalytics())

    act(() => {
      result.current.trackSearch("   ", "dashboard")
      jest.advanceTimersByTime(800)
    })

    expect(event).not.toHaveBeenCalled()
  })
})
