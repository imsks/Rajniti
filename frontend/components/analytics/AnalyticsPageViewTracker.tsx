"use client"

import { Suspense, useEffect } from "react"
import { usePathname, useSearchParams } from "next/navigation"
import { isGAEnabled, pageview } from "@/lib/analytics"

function AnalyticsPageViewTrackerInner() {
  const pathname = usePathname()
  const searchParams = useSearchParams()

  useEffect(() => {
    if (!isGAEnabled()) return
    const url = pathname + (searchParams?.toString() ? `?${searchParams}` : "")
    pageview(url)
  }, [pathname, searchParams])

  return null
}

/**
 * Tracks route-change page views. Wrapped in Suspense because useSearchParams()
 * opts out of static prerendering (Next.js CSR bailout).
 */
export default function AnalyticsPageViewTracker() {
  return (
    <Suspense fallback={null}>
      <AnalyticsPageViewTrackerInner />
    </Suspense>
  )
}
