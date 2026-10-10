import type { AnalyticsEventMap } from "@/lib/analytics";

/** Saransh frontend URL — env-driven so the destination can change without a code change. */
export const SARANSH_URL =
  process.env.NEXT_PUBLIC_SARANSH_URL || "https://saransh-app.vercel.app";

/** Where on Rajniti a Saransh link was clicked. */
export type SaranshPlacement = AnalyticsEventMap["saransh_click"]["placement"];

/**
 * Builds the outbound Saransh URL with campaign attribution so Saransh can tell
 * the visit came from Rajniti, and from which placement.
 * No personal or user-identifying data is added.
 */
export function buildSaranshUrl(placement: SaranshPlacement): string {
  const params = new URLSearchParams({
    utm_source: "rajniti",
    utm_medium: "referral",
    utm_campaign: "saransh_cross_promo",
    utm_content: placement,
  });

  const separator = SARANSH_URL.includes("?") ? "&" : "?";
  return `${SARANSH_URL}${separator}${params.toString()}`;
}
