"use client"

import { useEffect, useRef } from "react"
import { useAnalytics } from "./useAnalytics"

const DEPTH_MILESTONES = [25, 50, 75, 90] as const

/**
 * Tracks how far the user scrolls down the page.
 * Fires a `scroll_depth` GA4 event at 25 %, 50 %, 75 %, and 90 % milestones —
 * each milestone is fired at most once per page mount.
 *
 * The scroll listener is registered as `passive` so it never blocks paint.
 */
export function useScrollDepth(
  pageLocation: string,
  options?: { politician_id?: string }
) {
  const { trackEvent } = useAnalytics()
  const firedRef = useRef(new Set<number>())

  useEffect(() => {
    const fired = firedRef.current

    function onScroll() {
      const scrollTop = window.scrollY
      const docHeight =
        document.documentElement.scrollHeight - window.innerHeight
      if (docHeight <= 0) return

      const percent = Math.round((scrollTop / docHeight) * 100)

      for (const milestone of DEPTH_MILESTONES) {
        if (percent >= milestone && !fired.has(milestone)) {
          fired.add(milestone)
          trackEvent("scroll_depth", {
            depth_percent: milestone,
            page_location: pageLocation,
            ...(options?.politician_id
              ? { politician_id: options.politician_id }
              : {}),
          })
        }
      }
    }

    window.addEventListener("scroll", onScroll, { passive: true })
    // Run once on mount in case the page is already scrolled (e.g. restored scroll position)
    onScroll()

    return () => window.removeEventListener("scroll", onScroll)
  }, [pageLocation, options?.politician_id, trackEvent])
}
