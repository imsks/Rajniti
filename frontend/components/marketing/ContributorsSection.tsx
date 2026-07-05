"use client";

import Text from "@/components/ui/Text";
import Button from "@/components/ui/Button";
import Image from "next/image";
import { m } from "framer-motion";
import { useAnalytics } from "@/hooks/useAnalytics";
import contributors from "@/data/contributors.json";

export default function ContributorsSection() {
  const { trackEvent } = useAnalytics();

  return (
    <section id="contributors" className="py-20 bg-white dark:bg-gray-900">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <m.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 text-md font-semibold text-orange-600 mb-4 uppercase tracking-wider">
            <div className="w-8 h-0.5 border-t-2 border-orange-600" />
            Community
          </div>
          <h2 className="text-xl md:text-4xl lg:text-5xl font-serif font-bold text-[#0F1F3D] dark:text-white mb-6">
            Built by{" "}
            <span className="text-orange-600 italic">Contributors</span>
          </h2>
          <Text
            variant="body"
            className="text-gray-600 dark:text-gray-400 max-w-3xl mx-auto"
          >
            Rajniti is open source and community-driven. Meet the people
            making Indian democracy more transparent.
          </Text>
        </m.div>

        <div className="flex flex-wrap justify-center gap-6">
          {contributors.slice(0, 6).map((c, i) => (
            <m.a
              key={c.login}
              href={c.html_url}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              whileHover={{ y: -6, transition: { duration: 0.2 } }}
              className="flex flex-col items-center gap-3 rounded-2xl border border-black/10 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 w-36 text-center hover:shadow-lg transition-shadow"
            >
              <Image
                src={c.avatar_url}
                alt={c.login}
                width={64}
                height={64}
                className="rounded-full"
              />
              <Text
                variant="small"
                weight="semibold"
                className="text-[#0F1F3D] dark:text-white truncate w-full"
              >
                {c.login}
              </Text>
              <Text variant="caption" color="muted">
                {c.contributions} commit{c.contributions !== 1 ? "s" : ""}
              </Text>
            </m.a>
          ))}
        </div>

        <m.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="text-center mt-10"
        >
          <Button
            href="/contributors"
            variant="secondary"
            size="lg"
            onClick={() =>
              trackEvent("cta_click", {
                cta_name: "view_all_contributors",
                cta_url: "/contributors",
                page_location: "home_contributors",
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
            View All Contributors
          </Button>
        </m.div>
      </div>
    </section>
  );
}
