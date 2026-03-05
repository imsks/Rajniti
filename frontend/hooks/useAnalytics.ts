"use client"

import { useCallback, useEffect, useRef } from "react"
import { usePathname, useSearchParams } from "next/navigation"
import { event, pageview, isGAEnabled } from "@/lib/analytics"
import type { AnalyticsEvent, AnalyticsEventMap } from "@/lib/analytics"

const IS_DEV = process.env.NODE_ENV === "development"
const SEARCH_DEBOUNCE_MS = 800

/**
 * Central analytics hook.
 *
 * - `trackEvent`  — fire any event from the AnalyticsEventMap with full type safety
 * - `trackSearch` — debounced search tracking (won't fire on every keystroke)
 *
 * Route-change page views are tracked automatically when this hook is mounted.
 */
export function useAnalytics() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const searchTimer = useRef<ReturnType<typeof setTimeout>>(null)

  useEffect(() => {
    if (!isGAEnabled()) return
    const url = pathname + (searchParams?.toString() ? `?${searchParams}` : "")
    pageview(url)
  }, [pathname, searchParams])

  const trackEvent = useCallback(
    <E extends AnalyticsEvent>(name: E, params: AnalyticsEventMap[E]) => {
      if (IS_DEV) {
        // eslint-disable-next-line no-console
        console.debug("[Analytics]", name, params)
      }
      event(name, params)
    },
    []
  )

  const trackSearch = useCallback(
    (
      term: string,
      location: "dashboard" | "my_politicians",
      resultsCount?: number
    ) => {
      if (searchTimer.current) clearTimeout(searchTimer.current)
      if (!term.trim()) return

      searchTimer.current = setTimeout(() => {
        trackEvent("search", {
          search_term: term,
          results_count: resultsCount,
          search_location: location,
        })
      }, SEARCH_DEBOUNCE_MS)
    },
    [trackEvent]
  )

  return { trackEvent, trackSearch } as const
}
