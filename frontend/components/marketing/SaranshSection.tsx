"use client";

import Text from "@/components/ui/Text";
import Button from "@/components/ui/Button";
import { m } from "framer-motion";
import { useAnalytics } from "@/hooks/useAnalytics";

/** Saransh frontend URL — env-driven so the destination can change without a redeploy. */
export const SARANSH_URL =
  process.env.NEXT_PUBLIC_SARANSH_URL || "https://saransh-app.vercel.app";

export default function SaranshSection() {
  const { trackEvent } = useAnalytics();

  const trackClick = () =>
    trackEvent("saransh_click", {
      link_url: SARANSH_URL,
      page_location: "home_saransh",
    });

  return (
    <section
      id="saransh"
      className="py-20 bg-white dark:bg-gray-900 relative overflow-hidden"
    >
      <div className="absolute -top-24 -right-24 w-80 h-80 bg-orange-200/20 dark:bg-orange-900/10 rounded-full blur-3xl"></div>

      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 relative z-10">
        <m.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="rounded-2xl border border-gray-100 dark:border-gray-700 bg-gray-50/70 dark:bg-gray-800 shadow-xl overflow-hidden"
        >
          <div className="h-1.5 bg-gradient-to-r from-orange-500 via-white to-green-600"></div>

          <div className="p-8 sm:p-12 text-center">
            <div className="inline-flex items-center gap-3 text-sm uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400 mb-4">
              <span className="h-px w-8 bg-orange-400"></span>
              The other half
              <span className="h-px w-8 bg-green-500"></span>
            </div>

            <Text
              variant="h2"
              weight="bold"
              className="text-2xl sm:text-3xl text-[#0F1F3D] dark:text-white mb-4"
            >
              Meet <span className="text-orange-600 italic">Saransh</span>
            </Text>

            <Text
              variant="body"
              className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-8"
            >
              Rajniti tracks what your representatives promised. Saransh reports
              the news those promises turn up in — summarised from verified
              sources, with attribution you can check. Same civic-accountability
              project, two halves.
            </Text>

            <Button
              href={SARANSH_URL}
              external
              size="lg"
              onClick={trackClick}
              className="inline-flex items-center gap-3"
              rightIcon={
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
                </svg>
              }
            >
              Read the news on Saransh
            </Button>
          </div>
        </m.div>
      </div>
    </section>
  );
}
