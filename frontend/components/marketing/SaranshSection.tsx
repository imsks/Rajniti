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
      className="relative overflow-hidden bg-[#0F1F3D] py-20 dark:bg-[#070b16]"
    >
      {/* Tricolour glow backdrop */}
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(249,115,22,0.35),transparent_45%),radial-gradient(circle_at_85%_80%,rgba(22,163,74,0.35),transparent_45%)]"
      ></div>
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-orange-500 via-white to-green-600"
      ></div>

      <div className="relative z-10 mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <m.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <div className="mb-4 inline-flex items-center gap-3 text-sm uppercase tracking-[0.2em] text-white/70">
            <span className="h-px w-8 bg-orange-400"></span>
            The other half
            <span className="h-px w-8 bg-green-500"></span>
          </div>

          <Text
            variant="h2"
            weight="bold"
            className="mb-4 text-3xl text-white sm:text-4xl"
          >
            Meet <span className="italic text-orange-400">Saransh</span>
          </Text>

          <Text
            variant="body"
            className="mx-auto mb-8 max-w-2xl text-white/80"
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
        </m.div>
      </div>
    </section>
  );
}
