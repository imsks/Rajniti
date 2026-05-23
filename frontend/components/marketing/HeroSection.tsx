"use client";

import Text from "@/components/ui/Text";
import Button from "@/components/ui/Button";
import { motion } from "framer-motion";
import { useAnalytics } from "@/hooks/useAnalytics";

const round = (n: number) => Math.round(n * 10000) / 10000;
const CHAKRA_LINES = Array.from({ length: 24 }, (_, i) => {
  const rad = (((i * 360) / 24) * Math.PI) / 180;
  return {
    x1: round(12 + Math.cos(rad) * 3),
    y1: round(12 + Math.sin(rad) * 3),
    x2: round(12 + Math.cos(rad) * 10),
    y2: round(12 + Math.sin(rad) * 10),
  };
});

export default function HeroSection() {
  const { trackEvent } = useAnalytics();

  return (
    <section className="relative z-2 overflow-hidden py-20 sm:py-32">
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute -left-20 -top-16 h-64 w-64 rounded-full bg-orange-300/20 blur-3xl dark:bg-orange-500/20"></div>
        <div className="absolute -right-28 top-8 h-96 w-96 rounded-full bg-green-300/20 blur-3xl dark:bg-blue-500/20"></div>
      </div>
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:grid lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center lg:gap-8 lg:px-8 xl:gap-12">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8 flex justify-start"
          >
            <div className="rounded-full bg-linear-to-r from-orange-500 via-white to-green-500 p-0.5 shadow-lg">
              <div className="flex items-center gap-2 rounded-full bg-white px-6 py-2.5 dark:bg-slate-900/90">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" fill="#FF9933" />
                  <circle cx="12" cy="12" r="6.5" fill="#F5F5F5" />
                  <circle cx="12" cy="12" r="3" fill="#138808" />
                  <circle cx="12" cy="12" r="1.5" fill="#000080" />
                </svg>
                <span className="text-sm font-semibold bg-linear-to-r from-orange-600 via-gray-700 to-green-600 bg-clip-text text-transparent dark:from-orange-300 dark:via-slate-100 dark:to-emerald-300">
                  Built for the Indian Democracy
                </span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <h1 className="font-serif text-[44px] sm:text-[56px] lg:text-[80px] font-semibold leading-[1.08] tracking-[-0.02em] text-[#0F1F3D] text-left mb-4 dark:text-slate-100">
              Know Your{" "}
              <span className="text-orange-600 italic dark:text-orange-400">
                Elected
              </span>
              <br />
              Representatives
            </h1>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Text
              variant="body"
              className="max-w-xl text-gray-600 dark:text-slate-300 mb-8 text-left text-base sm:text-lg"
            >
              Rajniti is an open-source platform to explore Indian MPs and
              MLAs — their political history, education, family background,
              criminal records, and more. All free and community-driven.
            </Text>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-start items-start w-full"
          >
            <div className="shadow-[0_8px_30px_rgba(249,115,22,0.25)] w-full sm:w-auto">
              <Button
                href="/politicians"
                size="lg"
                className="w-full sm:w-auto"
                onClick={() =>
                  trackEvent("cta_click", {
                    cta_name: "explore_politicians",
                    cta_url: "/politicians",
                    page_location: "home_hero",
                  })
                }
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
                Explore Politicians
              </Button>
            </div>

            <Button
              href="https://github.com/imsks/rajniti"
              external
              variant="secondary"
              size="lg"
              className="w-full sm:w-auto"
              onClick={() =>
                trackEvent("external_link_click", {
                  link_text: "View on GitHub",
                  link_url: "https://github.com/imsks/rajniti",
                  page_location: "home_hero",
                })
              }
              leftIcon={
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    fillRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                    clipRule="evenodd"
                  />
                </svg>
              }
            >
              View on GitHub
            </Button>
          </motion.div>
        </div>

        {/* Ashoka Chakra */}
        <motion.svg
          className="pointer-events-none mx-auto mt-12 h-75 w-75 origin-center text-blue-800 sm:h-100 sm:w-100 lg:mt-0 lg:h-104 lg:w-104 xl:h-120 xl:w-120 dark:text-blue-400 dark:drop-shadow-[0_0_24px_rgba(96,165,250,0.32)]"
          viewBox="0 0 24 24"
          aria-hidden="true"
          fill="none"
          animate={{ rotate: 360 }}
          transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
          style={{ willChange: "transform" }}
        >
          <circle cx="12" cy="12" r="1.5" fill="currentColor" />
          {CHAKRA_LINES.map((line, i) => (
            <line
              key={i}
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke="currentColor"
              strokeWidth="0.5"
            />
          ))}
          <circle
            cx="12"
            cy="12"
            r="10"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
          />
        </motion.svg>
      </div>
    </section>
  );
}
