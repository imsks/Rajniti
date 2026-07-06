import { type AnalyticsEvent, type AnalyticsEventMap } from "@/lib/analytics";
/**
 * Central analytics hook.
 *
 * - `trackEvent`  — fire any event from the AnalyticsEventMap with full type safety
 * - `trackSearch` — debounced search tracking (won't fire on every keystroke)
 *
 * Route-change page views are tracked by AnalyticsPageViewTracker in the root layout.
 */
export declare function useAnalytics(): {
    readonly trackEvent: <E extends AnalyticsEvent>(name: E, params: AnalyticsEventMap[E]) => void;
    readonly trackSearch: (term: string, location: "dashboard" | "my_politicians", resultsCount?: number) => void;
};
//# sourceMappingURL=useAnalytics.d.ts.map