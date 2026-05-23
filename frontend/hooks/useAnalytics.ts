"use client"

import { useCallback, useRef } from "react"
import { event, type AnalyticsEvent, type AnalyticsEventMap} from "@/lib/analytics"

const IS_DEV = process.env.NODE_ENV === "development"
const SEARCH_DEBOUNCE_MS = 800

/**
 * Central analytics hook.
 *
 * - `trackEvent`  — fire any event from the AnalyticsEventMap with full type safety
 * - `trackSearch` — debounced search tracking (won't fire on every keystroke)
 *
 * Route-change page views are tracked by AnalyticsPageViewTracker in the root layout.
 */
export function useAnalytics() {
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

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
