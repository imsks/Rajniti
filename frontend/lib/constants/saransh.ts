import type { AnalyticsEventMap } from "@/lib/analytics";

/** Saransh frontend URL — env-driven so the destination can change without a code change. */
export const SARANSH_URL =
  process.env.NEXT_PUBLIC_SARANSH_URL || "https://saransh-app.vercel.app";

/**
 * Build the Saransh URL with campaign parameters so GA4 can attribute traffic
 * to the exact placement the user clicked (`utm_content`).
 */
export function buildSaranshUrl(placement: string): string {
  const url = new URL(SARANSH_URL);
  url.searchParams.set("utm_source", "rajniti");
  url.searchParams.set("utm_medium", "referral");
  url.searchParams.set("utm_campaign", "cross_promo");
  url.searchParams.set("utm_content", placement);
  return url.toString();
}
