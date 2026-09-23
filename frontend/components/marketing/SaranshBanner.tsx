"use client";

import Text from "@/components/ui/Text";
import { m } from "framer-motion";
import { useAnalytics } from "@/hooks/useAnalytics";
import { SARANSH_URL } from "@/components/marketing/SaranshSection";

interface SaranshBannerProps {
  /** Analytics label for where the banner was rendered. */
  pageLocation?: string;
  className?: string;
}

/**
 * Compact cross-promo banner for Saransh, sized for in-app pages such as the
 * dashboard where the full marketing section would be too heavy.
 */
export default function SaranshBanner({
  pageLocation = "dashboard_saransh",
  className = "",
}: SaranshBannerProps) {
  const { trackEvent } = useAnalytics();

  const trackClick = () =>
    trackEvent("saransh_click", {
      link_url: SARANSH_URL,
      page_location: pageLocation,
    });

  return (
    <m.a
      href={SARANSH_URL}
      target="_blank"
      rel="noopener noreferrer"
      onClick={trackClick}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`group relative flex flex-col gap-3 overflow-hidden rounded-2xl bg-[#0F1F3D] p-5 shadow-sm transition-shadow hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 sm:flex-row sm:items-center sm:justify-between ${className}`}
    >
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-[radial-gradient(circle_at_10%_20%,rgba(249,115,22,0.35),transparent_50%),radial-gradient(circle_at_90%_80%,rgba(22,163,74,0.35),transparent_50%)]"
      ></div>
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-orange-500 via-white to-green-600"
      ></div>

      <div className="relative z-10">
        <Text variant="h4" weight="bold" className="text-white">
          Meet <span className="italic text-orange-400">Saransh</span>
        </Text>
        <Text variant="small" className="mt-1 text-white/80">
          The news your representatives show up in — summarised from verified
          sources.
        </Text>
      </div>

      <span className="relative z-10 inline-flex shrink-0 items-center gap-2 rounded-lg bg-white/10 px-4 py-2 text-sm font-semibold text-white ring-1 ring-white/25 transition-colors group-hover:bg-white/20">
        Read the news
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 7l5 5m0 0l-5 5m5-5H6"
          />
        </svg>
      </span>
    </m.a>
  );
}
