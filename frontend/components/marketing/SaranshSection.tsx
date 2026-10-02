"use client";

import Text from "@/components/ui/Text";
// import Button from "@/components/ui/Button";
import Link from "@/components/ui/Link";
import { m } from "framer-motion";
import { useAnalytics } from "@/hooks/useAnalytics";
import { SARANSH_URL } from "@/lib/constants/saransh";
export { SARANSH_URL } from "@/lib/constants/saransh";

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
      className="relative overflow-hidden border-t border-gray-100 bg-white py-20 dark:border-gray-800 dark:bg-gray-900"
    >
      {/* Soft tricolour blobs, same pattern as the hero */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 overflow-hidden"
      >
        <div className="absolute right-100 top-5 h-80 w-80 rounded-full bg-orange-300/20 blur-3xl dark:bg-orange-500/20"></div>
        <div className="absolute -right-1 bottom-0 h-80 w-80 rounded-full bg-green-300/20 blur-3xl dark:bg-blue-500/20"></div>
      </div>

      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <m.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="grid items-center gap-12 lg:grid-cols-2"
        >
          <div>
            <div className="mb-4 inline-flex items-center gap-3 text-sm uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">
              <span className="h-px w-8 bg-orange-400"></span>
              The other half
              <span className="h-px w-8 bg-green-500"></span>
            </div>

            <Text
              variant="h2"
              weight="bold"
              className="mb-4 text-3xl text-[#0F1F3D] sm:text-4xl dark:text-white"
            >
              Meet{" "}
              <span className="italic text-orange-600 dark:text-orange-400">
                Saransh
              </span>
            </Text>

            <Text
              variant="body"
              className="mb-8 max-w-xl text-gray-600 dark:text-gray-300"
            >
              Rajniti tracks what your representatives promised. Saransh reports
              the news those promises turn up in — summarised from verified
              sources, with attribution you can check. Same civic-accountability
              project, two halves.
            </Text>

            <Link
              href={SARANSH_URL}
              external
              onClick={trackClick}
              variant="default"
              className="inline-flex items-center gap-2 font-medium hover:underline text-sm"
            >
              Read the news on Saransh
              <span aria-hidden="true">&rarr;</span>
            </Link>
          </div>

          <div className="flex flex-col items-stretch gap-4 sm:flex-row sm:items-center sm:justify-center lg:justify-end">
            <div className="flex-1 rounded-2xl border border-black/10 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
              <div className="text-xs uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">
                Promises
              </div>
              <div className="mt-2 font-serif text-2xl font-bold text-[#0F1F3D] dark:text-white">
                Raj<span className="text-orange-600">niti</span>
              </div>
              <Text
                variant="small"
                className="mt-2 text-gray-500 dark:text-gray-400"
              >
                What your representatives promised
              </Text>
            </div>

            <span
              aria-hidden="true"
              className="mx-auto flex h-9 w-9 shrink-0 items-center justify-center text-gray-500 dark:text-gray-400"
            >
              +
            </span>

            <a
              href={SARANSH_URL}
              target="_blank"
              rel="noopener noreferrer"
              onClick={trackClick}
              className="group flex-1 rounded-2xl border border-black/10 bg-white p-6 transition-shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:border-gray-700 dark:bg-gray-800 dark:focus:ring-offset-gray-900"
            >
              <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">
                News
              </div>
              <div className="mt-2 font-serif text-2xl font-bold text-[#0F1F3D] dark:text-white">
                Saransh
              </div>
              <Text
                variant="small"
                className="mt-2 text-gray-500 dark:text-gray-400"
              >
                What the news says about them
              </Text>
            </a>
          </div>
        </m.div>
      </div>
    </section>
  );
}
