import type { AnalyticsEvent, AnalyticsEventMap } from "./events";
export declare const GA_MEASUREMENT_ID: any;
type GtagCommand = "config" | "event" | "js" | "set";
declare global {
    interface Window {
        gtag: (command: GtagCommand, ...args: unknown[]) => void;
        dataLayer: unknown[];
    }
}
export declare function isGAEnabled(): boolean;
export declare function pageview(url: string): void;
export declare function event<E extends AnalyticsEvent>(name: E, params: AnalyticsEventMap[E]): void;
/**
 * Same as `event()` but forces beacon transport.
 * Use this inside `pagehide` / `beforeunload` handlers where the browser may
 * kill regular fetch-based requests before they complete.
 * GA4 internally calls `navigator.sendBeacon()` when transport_type is 'beacon'.
 */
export declare function beaconEvent<E extends AnalyticsEvent>(name: E, params: AnalyticsEventMap[E]): void;
export {};
//# sourceMappingURL=gtag.d.ts.map