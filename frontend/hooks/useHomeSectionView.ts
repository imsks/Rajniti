"use client"

import { useEffect, useRef } from "react"
import { useAnalytics } from "./useAnalytics"
import type { AnalyticsEventMap } from "@/lib/analytics"

type HomeSectionName = AnalyticsEventMap["home_section_view"]["section_name"]

/**
 * Fires a `home_section_view` GA4 event the first time the referenced homepage
 * section is at least 50 % visible. Fires at most once per page load (also
 * under React strict mode, which mounts effects twice in development).
 *
 * Usage:
 *   const ref = useRef<HTMLElement>(null)
 *   useHomeSectionView(ref, "saransh")
 */
export function useHomeSectionView(
  sectionRef: React.RefObject<HTMLElement | null>,
  sectionName: HomeSectionName
) {
  const { trackEvent } = useAnalytics()
  const firedRef = useRef(false)

  useEffect(() => {
    const section = sectionRef.current
    if (!section || typeof IntersectionObserver === "undefined") return
    if (firedRef.current) return

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting || firedRef.current) continue

          firedRef.current = true
          trackEvent("home_section_view", { section_name: sectionName })
          observer.disconnect()
        }
      },
      { threshold: 0.5 } // fire when at least 50 % of the section is visible
    )

    observer.observe(section)

    return () => observer.disconnect()
  }, [sectionRef, sectionName, trackEvent])
}
