"use client"

import { useEffect, useRef } from "react"
import { useAnalytics } from "./useAnalytics"

/**
 * Fires a `time_on_page` GA4 event when the component unmounts (i.e. the user
 * navigates away). Useful for measuring genuine reading engagement on content-
 * heavy pages like politician profiles.
 *
 * The duration is capped at 30 minutes to avoid inflating numbers from tabs
 * left open overnight.
 */
export function useTimeOnPage(
  pageLocation: string,
  options?: { politician_id?: string }
) {
  const { trackEvent } = useAnalytics()
  const entryTimeRef = useRef<number>(Date.now())

  useEffect(() => {
    entryTimeRef.current = Date.now()

    return () => {
      const rawSeconds = Math.round(
        (Date.now() - entryTimeRef.current) / 1000
      )
      // Cap at 30 minutes so background tabs don't distort averages
      const duration_seconds = Math.min(rawSeconds, 30 * 60)
      if (duration_seconds < 2) return // ignore accidental quick navigations

      trackEvent("time_on_page", {
        duration_seconds,
        page_location: pageLocation,
        ...(options?.politician_id
          ? { politician_id: options.politician_id }
          : {}),
      })
    }
    // trackEvent is stable (useCallback with empty deps), safe to omit from deps
    // eslint-disable-next-line react-hooks/exhaustive-deps, react-doctor/exhaustive-deps
  }, [pageLocation, options?.politician_id])
}
