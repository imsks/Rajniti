"use client"

import { useEffect, useRef } from "react"
import { useAnalytics } from "./useAnalytics"
import type { AnalyticsEventMap } from "@/lib/analytics"

type SectionName = AnalyticsEventMap["section_view"]["section_name"]

/**
 * Observes child elements that carry a `data-analytics-section` attribute inside
 * the given `containerRef`. The first time each section scrolls into view (≥ 40 %
 * visible) a `section_view` GA4 event is fired. Each section fires at most once.
 *
 * Usage in JSX:
 *   <div ref={containerRef}>
 *     <div data-analytics-section="performance"> … </div>
 *     <div data-analytics-section="education">   … </div>
 *   </div>
 */
export function useSectionTracking(
  containerRef: React.RefObject<HTMLElement | null>,
  politician: { id: string; name: string }
) {
  const { trackEvent } = useAnalytics()
  const seenRef = useRef(new Set<string>())

  useEffect(() => {
    const container = containerRef.current
    if (!container || typeof IntersectionObserver === "undefined") return

    const seen = seenRef.current

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          const section = (entry.target as HTMLElement).dataset.analyticsSection
          if (!section || seen.has(section)) continue

          seen.add(section)
          trackEvent("section_view", {
            section_name: section as SectionName,
            politician_id: politician.id,
            politician_name: politician.name,
          })
        }
      },
      { threshold: 0.4 } // fire when at least 40 % of the section is visible
    )

    // Observe every section element present at mount time
    const targets = container.querySelectorAll("[data-analytics-section]")
    targets.forEach((el) => observer.observe(el))

    return () => observer.disconnect()
  }, [containerRef, politician.id, politician.name, trackEvent])
}
