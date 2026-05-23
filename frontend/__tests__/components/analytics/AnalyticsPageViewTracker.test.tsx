import { render, waitFor } from "@testing-library/react"
import AnalyticsPageViewTracker from "@/components/analytics/AnalyticsPageViewTracker"
import { pageview } from "@/lib/analytics"

const mockUsePathname = jest.fn()
const mockUseSearchParams = jest.fn()

jest.mock("next/navigation", () => ({
  usePathname: () => mockUsePathname(),
  useSearchParams: () => mockUseSearchParams(),
}))

jest.mock("@/lib/analytics", () => ({
  isGAEnabled: jest.fn(() => true),
  pageview: jest.fn(),
}))

describe("AnalyticsPageViewTracker", () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUsePathname.mockReturnValue("/dashboard")
    mockUseSearchParams.mockReturnValue(new URLSearchParams("tab=overview"))
  })

  it("fires pageview with pathname and query string when GA is enabled", async () => {
    render(<AnalyticsPageViewTracker />)

    await waitFor(() => {
      expect(pageview).toHaveBeenCalledWith("/dashboard?tab=overview")
    })
  })

  it("fires pageview with pathname only when search params are empty", async () => {
    mockUseSearchParams.mockReturnValue(new URLSearchParams())

    render(<AnalyticsPageViewTracker />)

    await waitFor(() => {
      expect(pageview).toHaveBeenCalledWith("/dashboard")
    })
  })
})
