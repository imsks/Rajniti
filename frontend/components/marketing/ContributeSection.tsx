"use client";

import Text from "@/components/ui/Text";
import Link from "@/components/ui/Link";
import Button from "@/components/ui/Button";
import Image from "next/image";
import { m } from "framer-motion";
import { useAnalytics } from "@/hooks/useAnalytics";

export default function ContributeSection() {
  const { trackEvent } = useAnalytics();

  return (
    <section
      id="contribute"
      className="py-20 bg-[#162844] dark:bg-gray-950 text-white"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <m.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <Text variant="h1" className="text-white mb-4">
            Help Us Enrich{" "}
            <span className="text-orange-400 italic">Profiles</span>
          </Text>
          <Text variant="body" className="text-orange-100 max-w-3xl mx-auto">
            Many politician profiles are missing education, family, and criminal
            record details. Your contributions make democracy more transparent!
          </Text>
        </m.div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <m.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
            className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
          >
            <div className="text-3xl mb-3">
              <Image
                src="/logo/ContributeData.svg"
                alt="Contribute Logo"
                width={40}
                height={40}
                className="h-10 w-10"
              />
            </div>
            <Text variant="h4" weight="bold" className="text-white mb-2">
              Contribute Data
            </Text>
            <Text variant="body" className="text-orange-100 mb-4">
              Found a politician with missing info? Open an issue with the
              details and we&apos;ll update the profile.
            </Text>
            <div className="border-t border-white/20 my-4"></div>
            <Link
              href="https://github.com/imsks/rajniti/issues"
              external
              onClick={() =>
                trackEvent("contribute_click", {
                  contribute_type: "data",
                  page_location: "home_contribute",
                })
              }
              className="inline-flex items-center gap-2 text-[#0F1F3D] font-bold hover:underline"
            >
              Open an Issue
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Link>
          </m.div>

          <m.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
            className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
          >
            <div className="text-3xl mb-3">
              <Image
                src="/logo/Contribute.svg"
                alt="Contribute Logo"
                width={40}
                height={40}
                className="h-10 w-10"
              />
            </div>
            <Text variant="h4" weight="bold" className="text-white mb-2">
              Contribute Code
            </Text>
            <Text variant="body" className="text-orange-100 mb-4">
              Help improve the scraper, add new state MLAs, or enhance the UI.
              All contributions are welcome, big or small!
            </Text>
            <div className="border-t border-white/20 "></div>
            <Link
              href="https://github.com/imsks/rajniti/fork"
              external
              onClick={() =>
                trackEvent("contribute_click", {
                  contribute_type: "code",
                  page_location: "home_contribute",
                })
              }
              className="inline-flex items-center gap-2 text-[#FFD700] font-bold hover:underline mt-4 "
            >
              Fork &amp; Contribute
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Link>
          </m.div>
        </div>

        <m.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-12"
        >
          <Button
            href="/politicians"
            size="lg"
            onClick={() =>
              trackEvent("cta_click", {
                cta_name: "explore_politicians",
                cta_url: "/politicians",
                page_location: "home_contribute",
              })
            }
            className="inline-flex items-center gap-3 bg-orange-600 text-white font-semibold px-6 py-3 rounded-lg border-2 border-orange-600  hover:text-white shadow-[0_8px_30px_rgba(249,115,22,0.2)]  hover:-translate-y-0.5 transition-all duration-300"
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
        </m.div>
      </div>
    </section>
  );
}
