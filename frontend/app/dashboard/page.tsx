"use client";

import { Suspense, useState, useMemo, useEffect } from "react";
import dynamic from "next/dynamic";
import { m } from "framer-motion";
import { Footer, Navbar } from "@/components/layout";
import Button from "@/components/ui/Button";
import Text from "@/components/ui/Text";
import Pagination from "@/components/ui/Pagination";
import PoliticianCard from "@/components/PoliticianCard";
import PoliticianCardWrapper from "@/components/PoliticianCardWrapper";
import { usePoliticians } from "@/hooks/usePoliticians";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useScrollDepth } from "@/hooks/useScrollDepth";
import OnboardingGate from "@/components/auth/OnboardingGate";
import Image from "next/image";

// Lazy-load heavy sub-component (has its own framer-motion + search logic)
const MyPoliticiansSection = dynamic(
  () => import("@/components/MyPoliticiansSection"),
  { ssr: false },
);

type Tab = "ALL" | "MP" | "MLA";

export default function Dashboard() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900 flex items-center justify-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent"></div>
        </div>
      }
    >
      <OnboardingGate redirectIfIncomplete>
        <DashboardContent />
      </OnboardingGate>
    </Suspense>
  );
}

function DashboardContent() {
  const [activeTab, setActiveTab] = useState<Tab>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [partyFilter, setPartyFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(12);
  const { trackEvent, trackSearch } = useAnalytics();
  useScrollDepth("dashboard");

  // One API call for all politicians; filter client-side by tab + search/filters
  const { all, loading, error, states, parties, stats, filter } =
    usePoliticians();

  // Filtered list — pure client-side (type from tab + query, state, party)
  const displayPoliticians = useMemo(() => {
    let list = filter({
      query: searchQuery,
      state: stateFilter,
      party: partyFilter,
    });
    if (activeTab === "MP") list = list.filter((p) => p.type === "MP");
    else if (activeTab === "MLA") list = list.filter((p) => p.type === "MLA");
    return list;
  }, [filter, searchQuery, stateFilter, partyFilter, activeTab]);

  const rankedPoliticians = useMemo(() => {
    if (!displayPoliticians.length) return [];

    // 🔥 find max values for normalization
    const maxQ = Math.max(
      ...displayPoliticians.map((p) => p.performance?.questions || 0),
      1,
    );
    const maxD = Math.max(
      ...displayPoliticians.map((p) => p.performance?.debates || 0),
      1,
    );

    return displayPoliticians
      .map((p) => {
        const perf = {
          attendance: p.performance?.attendance ?? 0,
          questions: p.performance?.questions ?? 0,
          debates: p.performance?.debates ?? 0,
        };

        // normalize (0 → 1 scale)
        const attendanceScore = perf.attendance / 100;
        const questionsScore = perf.questions / maxQ;
        const debatesScore = perf.debates / maxD;

        const score =
          attendanceScore * 0.4 + questionsScore * 0.3 + debatesScore * 0.3;

        return { ...p, score };
      })
      .sort((a, b) => b.score - a.score)
      .map((p, i) => ({ ...p, rank: i + 1 }));
  }, [displayPoliticians]);

  // Pagination calculations
  const totalPages = Math.max(
  1,
  Math.ceil(rankedPoliticians.length / itemsPerPage),
);

  // Reset invalid page automatically without effects
  const effectivePage = currentPage > totalPages ? 1 : currentPage;

  const startIndex = (effectivePage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;

  const paginatedPoliticians = rankedPoliticians.slice(
  startIndex,
  endIndex
  );

  // Scroll to top when page changes
  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }, [effectivePage]);

  // Debounced search tracking
  useEffect(() => {
    trackSearch(searchQuery, "dashboard", displayPoliticians.length);
  }, [searchQuery, trackSearch, displayPoliticians.length]);

  const hasActiveFilters = !!(searchQuery || stateFilter || partyFilter);

  // ── Render ────────────────────────────────────────────────────────────

  useEffect(() => {
    if (error) {
      trackEvent("error_view", {
        error_type: "connection",
        error_message: error,
        page_location: "dashboard",
      });
    }
  }, [error, trackEvent]);

  if (error) {
    return (
      <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full border-l-4 border-red-500">
          <div className="flex items-center gap-3 mb-4">
            <div className="text-red-500 text-3xl">⚠️</div>
            <Text
              variant="h4"
              weight="bold"
              className="text-gray-900 dark:text-white"
            >
              Connection Error
            </Text>
          </div>
          <Text
            variant="body"
            className="text-gray-600 dark:text-gray-400 mb-4"
          >
            {error}
          </Text>
          <Button onClick={() => window.location.reload()} fullWidth>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900">
      <Navbar sticky />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Your Politicians (MP + MLA slots) */}
        <MyPoliticiansSection allPoliticians={all} />

        {/* Header + Stats */}
        <m.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <Text
            variant="h2"
            weight="bold"
            className="text-gray-900 dark:text-white mb-2"
          >
            <span className="text-orange-600">Indian</span> Politicians
          </Text>
          <Text
            variant="body"
            className="text-gray-600 dark:text-gray-400 mb-6"
          >
            Browse elected MPs and MLAs. Help us enrich their profiles!
          </Text>

         
        </m.div>

        {/* Tabs */}
        <m.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex gap-2 mb-6"
        >
          {(["ALL", "MP", "MLA"] as Tab[]).map((tab, i) => (
            <m.button
              key={tab}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.4 + i * 0.1 }}
              onClick={() => {
                setActiveTab(tab);
                setSearchQuery("");
                setStateFilter("");
                setPartyFilter("");
                trackEvent("filter_apply", {
                  filter_type: "tab",
                  filter_value: tab,
                });
              }}
              className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all ${
                activeTab === tab
                  ? "bg-orange-500 text-white shadow-md"
                  : "bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:border-orange-400 dark:hover:border-orange-500 hover:text-orange-600 dark:hover:text-orange-400"
              }`}
            >
              {tab === "ALL" ? "All" : tab === "MP" ? "MPs" : "MLAs"}
            </m.button>
          ))}
        </m.div>

        {/* Search + Filters */}
        <m.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6"
        >
          <div className="flex flex-col md:flex-row gap-3">
            {/* Search input */}
            <div className="flex-1 relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                <Image
                  src="/logo/search.svg"
                  alt="Search"
                  width={20}
                  height={20}
                  className="w-5 h-5 dark:filter-[invert(0.70)_brightness(1.2)]"
                />
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name, constituency, state or party..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>

            {/* State filter */}
            <select
              value={stateFilter}
              onChange={(e) => {
                setStateFilter(e.target.value);
                if (e.target.value) {
                  trackEvent("filter_apply", {
                    filter_type: "state",
                    filter_value: e.target.value,
                  });
                }
              }}
              className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500 min-w-[180px]"
            >
              <option value="">All States</option>
              {states.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>

            {/* Party filter */}
            <select
              value={partyFilter}
              onChange={(e) => {
                setPartyFilter(e.target.value);
                if (e.target.value) {
                  trackEvent("filter_apply", {
                    filter_type: "party",
                    filter_value: e.target.value,
                  });
                }
              }}
              className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500 min-w-[180px]"
            >
              <option value="">All Parties</option>
              {parties.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>

          {/* Active filters summary */}
          {hasActiveFilters && (
            <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
              <Text
                variant="small"
                className="text-gray-500 dark:text-gray-400"
              >
                Showing {displayPoliticians.length.toLocaleString()} result
                {displayPoliticians.length !== 1 ? "s" : ""}
              </Text>
              <button
                onClick={() => {
                  setSearchQuery("");
                  setStateFilter("");
                  setPartyFilter("");
                  trackEvent("filter_clear", {});
                }}
                className="ml-2 text-xs text-orange-600 hover:underline"
              >
                Clear filters
              </button>
            </div>
          )}
        </m.div>

        {/* Loading state */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {Array.from({ length: 12 }).map((_, i) => (
              <PoliticianCardWrapper key={i} loading={true} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && displayPoliticians.length === 0 && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🔍</div>
            <Text
              variant="h4"
              weight="bold"
              className="text-gray-700 dark:text-gray-200 mb-2"
            >
              No politicians found
            </Text>
            <Text variant="body" className="text-gray-500 dark:text-gray-400">
              {hasActiveFilters
                ? "Try adjusting your search or filters."
                : "No data available yet."}
            </Text>
          </div>
        )}

        {/* Politician grid */}
        {!loading && displayPoliticians.length > 0 && (
          <>
            {/* Results info and items per page selector */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
              <Text variant="body" className="text-gray-600 dark:text-gray-400">
                Showing {startIndex + 1}-
                {Math.min(endIndex, displayPoliticians.length)} of{" "}
                {displayPoliticians.length} politicians
              </Text>
              <div className="flex items-center gap-2">
                <Text
                  variant="body"
                  className="text-gray-600 dark:text-gray-400 text-sm"
                >
                  Show:
                </Text>
                <select
                  value={itemsPerPage}
                  onChange={(e) => {
                    const val = Number(e.target.value);
                    setItemsPerPage(val);
                    trackEvent("filter_apply", {
                      filter_type: "items_per_page",
                      filter_value: String(val),
                    });
                  }}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200"
                >
                  <option value={12}>12</option>
                  <option value={24}>24</option>
                  <option value={48}>48</option>
                  <option value={96}>96</option>
                </select>
                <Text
                  variant="body"
                  className="text-gray-600 dark:text-gray-400 text-sm"
                >
                  per page
                </Text>
              </div>
            </div>

            <m.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
            >
              {paginatedPoliticians.map((p, i) => {
                const percentile = p.rank / rankedPoliticians.length;

                return (
                  <m.div
                    key={p.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: i * 0.05 }}
                  >
                    <>
                      <div className="flex items-center gap-2 mb-1">
                        <Text className="text-orange-600 font-bold">
                          #{p.rank}
                        </Text>

                        {percentile <= 0.1 && (
                          <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                            Top Performer
                          </span>
                        )}

                        {percentile > 0.1 && percentile <= 0.3 && (
                          <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                            Good
                          </span>
                        )}

                        {percentile > 0.3 && percentile <= 0.7 && (
                          <span className="text-xs bg-yellow-500 text-black px-2 py-1 rounded">
                            Average
                          </span>
                        )}

                        {percentile > 0.7 && (
                          <span className="text-xs bg-red-600 text-white px-2 py-1 rounded">
                            Low Performer
                          </span>
                        )}
                      </div>

                      <PoliticianCard politician={p} />
                    </>
                  </m.div>
                );
              })}
            </m.div>
            {/* Pagination controls */}
            <Pagination
              currentPage={effectivePage}
              totalPages={totalPages}
              onPageChange={(newPage) => {
                setCurrentPage(newPage);
                trackEvent("pagination", {
                  direction: newPage > effectivePage ? "next" : "previous",
                  page_number: newPage,
                  total_pages: totalPages,
                });
              }}
            />
          </>
        )}

        {/* Contribute CTA */}
        <m.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mt-12 bg-linear-to-r from-orange-500 to-orange-600 rounded-2xl p-8 text-center text-white"
        >
          <Text variant="h3" weight="bold" className="text-white mb-2">
            Help us build the most comprehensive politician database
          </Text>
          <Text
            variant="body"
            className="text-orange-100 mb-6 max-w-2xl mx-auto"
          >
            Many profiles are missing education, family, and criminal record
            details. You can contribute by enriching profiles or reporting
            inaccuracies.
          </Text>
          <m.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              href="https://github.com/imsks/rajniti/issues/new"
              external
              onClick={() =>
                trackEvent("contribute_click", {
                  contribute_type: "data",
                  page_location: "dashboard_cta",
                })
              }
              className="bg-white text-orange-600 py-2 px-4 rounded-lg font-semibold border-none shadow-lg"
              size="lg"
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
              Contribute on GitHub
            </Button>
          </m.div>
        </m.div>
      </div>

      <Footer />
    </div>
  );
}

// ── Tiny helper component ─────────────────────────────────────────────────

function StatCard({
  value,
  label,
  color,
}: {
  value: string;
  label: string;
  color: string;
}) {
  return (
    <m.div
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm"
    >
      <Text variant="h3" weight="bold" className={color}>
        {value}
      </Text>
      <Text variant="small" className="text-gray-500 dark:text-gray-400">
        {label}
      </Text>
    </m.div>
  );
}
