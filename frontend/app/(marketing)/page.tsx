"use client";
import PreambleSection from "@/components/PreambleSection";
import { Navbar, Footer } from "@/components/layout";
import Text from "@/components/ui/Text";
import Link from "@/components/ui/Link";
import Button from "@/components/ui/Button";
import Image from "next/image";
import { motion } from "framer-motion";
import { useEffect, Suspense } from "react";
import { useAnalytics } from "@/hooks/useAnalytics";
import contributors from "@/data/contributors.json";

export default function Home() {
  return (
    <Suspense>
      <HomeContent />
    </Suspense>
  );
}

function HomeContent() {
  const { trackEvent } = useAnalytics();

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: "auto",
    });

    if ("scrollRestoration" in history) {
      history.scrollRestoration = "manual";
    }

    return () => {
      if ("scrollRestoration" in history) {
        history.scrollRestoration = "auto";
      }
    };
  }, []);

  return (
    <div className="min-h-screen overflow-x-hidden bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-[#070b16] dark:via-[#0b1324] dark:to-[#101a32]">
      <Navbar variant="default" />

      {/* Hero Section */}
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
                  href="/dashboard"
                  size="lg"
                  className="w-full sm:w-auto"
                  onClick={() =>
                    trackEvent("cta_click", {
                      cta_name: "explore_politicians",
                      cta_url: "/dashboard",
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

          {/* Ashoka Chakra - On mobile below, on desktop right-aligned */}
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
            {Array.from({ length: 24 }).map((_, i) => {
              const angle = (i * 360) / 24;
              const rad = (angle * Math.PI) / 180;
              const x1 = 12 + Math.cos(rad) * 3;
              const y1 = 12 + Math.sin(rad) * 3;
              const x2 = 12 + Math.cos(rad) * 10;
              const y2 = 12 + Math.sin(rad) * 10;
              return (
                <line
                  key={i}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="currentColor"
                  strokeWidth="0.5"
                />
              );
            })}
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

      {/* What You Can Find */}
      <section id="about" className="py-20 bg-white dark:bg-gray-900">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <div className="flex items-center justify-center gap-3 text-md font-semibold text-orange-600 mb-4 uppercase tracking-wider">
              <div className="w-8 h-0.5 border-t-2  border-orange-600"></div>
              What You&apos;ll Find
            </div>
            <h2 className="text-xl md:text-4xl lg:text-5xl font-serif font-bold text-[#0F1F3D] dark:text-white mb-6">
              Transparency for Every{" "}
              <span className="text-orange-600 italic">Citizen</span>
            </h2>
            <Text
              variant="body"
              className="text-gray-600 dark:text-gray-400 max-w-3xl mx-auto"
            >
              We&apos;re building the most transparent and comprehensive
              database of Indian elected representatives.
            </Text>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, delay: 0.1 }}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
              className="rounded-2xl p-8 border border-black/10 dark:border-gray-700"
            >
              <div className="text-4xl mb-4">
                <Image
                  src="/logo/parliament.png"
                  alt="Parliament Logo"
                  width={40}
                  height={40}
                  className="h-10 w-10"
                />
              </div>
              <Text
                variant="h4"
                weight="bold"
                className="text-[#0F1F3D] dark:text-white mb-3"
              >
                Members of Parliament
              </Text>
              <Text variant="body" color="muted">
                Browse all winning Lok Sabha MPs — their party, constituency,
                state, and election history.
              </Text>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, delay: 0.2 }}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
              className=" rounded-2xl p-8 border border-black/10 dark:border-gray-700"
            >
              <div className="text-4xl mb-4">
                <Image
                  src="/logo/Assembly.png"
                  alt="State Assembly Logo"
                  width={40}
                  height={40}
                  className="h-10 w-10"
                />
              </div>
              <Text
                variant="h4"
                weight="bold"
                className="text-[#0F1F3D] dark:text-white mb-3"
              >
                State Assembly MLAs
              </Text>
              <Text variant="body" color="muted">
                Explore elected MLAs from state assemblies across India with
                detailed political backgrounds.
              </Text>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, delay: 0.3 }}
              whileHover={{ y: -8, transition: { duration: 0.2 } }}
              className=" rounded-2xl p-8 border border-black/10 dark:border-gray-700"
            >
              <div className="text-4xl mb-4">
                <Image
                  src="/logo/Profile.png"
                  alt="Rich Profile Logo"
                  width={36}
                  height={36}
                  className="h-9 w-9"
                />
              </div>
              <Text
                variant="h4"
                weight="bold"
                className="text-[#0F1F3D] dark:text-white mb-3 "
              >
                Rich Profiles
              </Text>
              <Text variant="body" color="muted">
                Education, family, criminal records, social media, and more —
                enriched with community contributions.
              </Text>
            </motion.div>
          </div>
        </div>
      </section>

      {/* We The People of India - Preamble Section */}
      <PreambleSection />

      {/* Contribute Section */}
      <section
        id="contribute"
        className="py-20 bg-[#162844] dark:bg-gray-950 text-white"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
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
              Many politician profiles are missing education, family, and
              criminal record details. Your contributions make democracy more
              transparent!
            </Text>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
              whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <div className="text-3xl mb-3">
                <Image
                  src="/logo/ContributeData.png"
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
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.3 }}
              whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <div className="text-3xl mb-3">
                <Image
                  src="/logo/Contribute.png"
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
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-center mt-12"
          >
            <Button
              href="/dashboard"
              size="lg"
              onClick={() =>
                trackEvent("cta_click", {
                  cta_name: "explore_politicians",
                  cta_url: "/dashboard",
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
          </motion.div>
        </div>
      </section>

      {/* Top Contributors Preview */}
      <section id="contributors" className="py-20 bg-white dark:bg-gray-900">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <motion.div
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
          </motion.div>

          <div className="flex flex-wrap justify-center gap-6">
            {contributors.slice(0, 6).map((c, i) => (
              <motion.a
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
              </motion.a>
            ))}
          </div>

          <motion.div
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
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
