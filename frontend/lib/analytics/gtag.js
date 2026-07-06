export const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID ?? "";
export function isGAEnabled() {
    return GA_MEASUREMENT_ID !== "" && typeof window !== "undefined";
}
export function pageview(url) {
    if (!isGAEnabled())
        return;
    window.gtag("config", GA_MEASUREMENT_ID, { page_path: url });
}
export function event(name, params) {
    if (!isGAEnabled())
        return;
    window.gtag("event", name, params);
}
/**
 * Same as `event()` but forces beacon transport.
 * Use this inside `pagehide` / `beforeunload` handlers where the browser may
 * kill regular fetch-based requests before they complete.
 * GA4 internally calls `navigator.sendBeacon()` when transport_type is 'beacon'.
 */
export function beaconEvent(name, params) {
    if (!isGAEnabled())
        return;
    window.gtag("event", name, { ...params, transport_type: "beacon" });
}
//# sourceMappingURL=gtag.js.map