import type { AnalyticsEvent, AnalyticsEventMap } from "./events"

export const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID ?? ""

type GtagCommand = "config" | "event" | "js" | "set"

declare global {
  interface Window {
    gtag: (command: GtagCommand, ...args: unknown[]) => void
    dataLayer: unknown[]
  }
}

export function isGAEnabled(): boolean {
  return GA_MEASUREMENT_ID !== "" && typeof window !== "undefined"
}

export function pageview(url: string) {
  if (!isGAEnabled()) return
  window.gtag("config", GA_MEASUREMENT_ID, { page_path: url })
}

export function event<E extends AnalyticsEvent>(
  name: E,
  params: AnalyticsEventMap[E]
) {
  if (!isGAEnabled()) return
  window.gtag("event", name, params)
}

/**
 * Same as `event()` but forces beacon transport.
 * Use this inside `pagehide` / `beforeunload` handlers where the browser may
 * kill regular fetch-based requests before they complete.
 * GA4 internally calls `navigator.sendBeacon()` when transport_type is 'beacon'.
 */
export function beaconEvent<E extends AnalyticsEvent>(
  name: E,
  params: AnalyticsEventMap[E]
) {
  if (!isGAEnabled()) return
  window.gtag("event", name, { ...params, transport_type: "beacon" })
}
