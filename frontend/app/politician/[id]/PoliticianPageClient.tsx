"use client";

import { useEffect, useRef, useState } from "react";
import NextImage from "next/image";
import {
  AlertTriangle,
  UserPlus,
  BarChart2,
  Scale,
  Landmark,
  GraduationCap,
  Users,
  MessageSquare,
  Trophy,
  CalendarCheck,
  HelpCircle,
  Mail,
  Phone,
  MapPin,
  Clock,
  Share2,
  Check,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { CitationLink } from "@/components/CitationLink";
import { Footer, Navbar } from "@/components/layout";
import Button from "@/components/ui/Button";
import Text from "@/components/ui/Text";
import Image from "@/components/ui/Image";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useDeferredMount } from "@/hooks/useDeferredMount";
import PoliticianPageAnalytics from "./PoliticianPageAnalytics";
import { toTitleCase } from "@/lib/politicianUtils";
import type { Politician, Citation, CitationSource } from "@/types/politician";

// ── Types ──────────────────────────────────────────────────────────────────

export type PoliticianPageClientProps = {
  politician: Politician;
  routeSegment: string;
};

const SECTION_IDS = [
  "performance",
  "criminal",
  "history",
  "education",
  "family",
  "contact",
] as const;
type SectionId = (typeof SECTION_IDS)[number];

// ── Social brand SVG icons ─────────────────────────────────────────────────

const brandIconProps = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "currentColor",
  "aria-hidden": true,
} as const;

function IconX() {
  return (
    <svg {...brandIconProps}>
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.45-6.231Zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77Z" />
    </svg>
  );
}

function IconFacebook() {
  return (
    <svg {...brandIconProps}>
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073Z" />
    </svg>
  );
}

function IconInstagram() {
  return (
    <svg {...brandIconProps}>
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069ZM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0Zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324ZM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881Z" />
    </svg>
  );
}

function IconLinkedIn() {
  return (
    <svg {...brandIconProps}>
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286ZM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065Zm1.782 13.019H3.555V9h3.564v11.452ZM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003Z" />
    </svg>
  );
}

function IconYouTube() {
  return (
    <svg {...brandIconProps}>
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814ZM9.545 15.568V8.432L15.818 12l-6.273 3.568Z" />
    </svg>
  );
}

function IconGlobe() {
  return (
    <svg
      {...brandIconProps}
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10Z" />
    </svg>
  );
}

// ── National and State average constants ──────────────────────────────────────────────
// Approximate 17th Lok Sabha session averages — used for performance bar context.
const NATIONAL_AVG = { attendance: 85, questions: 103, debates: 20 } as const;
const STATE_AVG = { attendance: 84, questions: 79, debates: 14 } as const;

// ── Helpers ────────────────────────────────────────────────────────────────

function isFullUuid(value: string) {
  return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(
    value,
  );
}

function extractSlugAndOptionalUuid(input: string) {
  if (isFullUuid(input)) {
    return {
      slug: null as string | null,
      uuid: input,
      uuidShort: null as string | null,
    };
  }
  const shortMatch = input.match(/-([0-9a-fA-F]{8})$/);
  if (shortMatch) {
    return {
      slug: input.slice(0, -shortMatch[0].length),
      uuid: null as string | null,
      uuidShort: shortMatch[1].toLowerCase(),
    };
  }
  return {
    slug: input,
    uuid: null as string | null,
    uuidShort: null as string | null,
  };
}

/** Formats ISO timestamp as "Updated Xd ago" relative string. */
function formatUpdatedAt(updatedAt?: string | null): string | null {
  if (!updatedAt) return null;
  const diffMs = Date.now() - new Date(updatedAt).getTime();
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (days === 0) return "Updated today";
  if (days < 30) return `Updated ${days}d ago`;
  const months = Math.floor(days / 30);
  return `Updated ${months}mo ago`;
}

function formatSource(source?: CitationSource | null): string {
  const map: Partial<Record<CitationSource, string>> = {
    ECI: "ECI",
    MYNETA: "MyNeta",
    GOV_WEBSITE: "Gov",
    NEWS: "News",
    OTHERS: "Source",
  };
  return source ? (map[source] ?? source) : "Source";
}

// ── Scroll spy ─────────────────────────────────────────────────────────────

function useScrollSpy(): SectionId {
  const [active, setActive] = useState<SectionId>("performance");
  useEffect(() => {
    function update() {
      const offset = 130;
      let current: SectionId = "performance";
      for (const id of SECTION_IDS) {
        const el = document.getElementById(`section-${id}`);
        if (el && el.getBoundingClientRect().top <= offset) current = id;
      }
      setActive(current);
    }
    window.addEventListener("scroll", update, { passive: true });
    update();
    return () => window.removeEventListener("scroll", update);
  }, []);
  return active;
}

function scrollToSection(id: SectionId) {
  const el = document.getElementById(`section-${id}`);
  if (!el) return;
  const top = el.getBoundingClientRect().top + window.scrollY - 120;
  window.scrollTo({ top, behavior: "smooth" });
}

// ── Fade-in wrapper ────────────────────────────────────────────────────────

function useInView(threshold = 0.1) {
  const ref = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setInView(true);
          obs.disconnect();
        }
      },
      { threshold },
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, inView };
}

// ── Section card ───────────────────────────────────────────────────────────

function SectionCard({
  id,
  analyticsSection,
  children,
}: {
  id: SectionId;
  analyticsSection?: string;
  children: React.ReactNode;
}) {
  const { ref, inView } = useInView();
  return (
    <div
      id={`section-${id}`}
      ref={ref}
      data-analytics-section={analyticsSection}
      className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden mb-4 hover:shadow-md transition-shadow"
      style={{
        opacity: inView ? 1 : 0,
        transform: inView ? "translateY(0)" : "translateY(20px)",
        transition: "opacity 0.45s ease, transform 0.45s ease",
      }}
    >
      {children}
    </div>
  );
}

// SectionHeader uses the same /logo/ images as before, with an optional descriptive count label
function SectionHeader({
  logoSrc,
  title,
  countLabel,
}: {
  logoSrc: string;
  title: string;
  countLabel?: string; // e.g. "10 cases", "4 terms", "8 qualifications", "6 members"
}) {
  return (
    <div className="flex items-center gap-2.5 px-5 pt-5 pb-4 border-b border-gray-100 dark:border-gray-800">
      <NextImage
        src={logoSrc}
        alt=""
        width={24}
        height={24}
        className="object-contain opacity-75 shrink-0 dark:invert"
      />
      <Text
        variant="h4"
        weight="bold"
        className="text-gray-900 dark:text-white text-[16px]"
      >
        {title}
      </Text>
      {countLabel && (
        <span className="text-xs text-gray-500 dark:text-gray-500 font-normal">
          {countLabel}
        </span>
      )}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="px-5 py-8 text-center space-y-2">
      <Text variant="small" className="text-gray-400 dark:text-gray-500 block">
        {message}
      </Text>
      <a
        href="https://github.com/imsks/rajniti/issues/new"
        target="_blank"
        rel="noopener noreferrer"
        className="group inline-flex items-center gap-1 text-xs text-orange-600 dark:text-orange-400 hover:underline font-semibold"
      >
        Help us add this info
        <svg
          className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5"
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
      </a>
    </div>
  );
}

// ── Section Tab Navigation ─────────────────────────────────────────────────

const TAB_META: Record<SectionId, { label: string; icon: React.ReactNode }> = {
  performance: { label: "Performance", icon: <BarChart2 size={15} /> },
  criminal: { label: "Criminal", icon: <Scale size={15} /> },
  history: { label: "History", icon: <Landmark size={15} /> },
  education: { label: "Education", icon: <GraduationCap size={15} /> },
  family: { label: "Family", icon: <Users size={15} /> },
  contact: { label: "Contact", icon: <Mail size={15} /> },
};

function SectionTabNav({
  active,
  counts,
  onTabClick,
}: {
  active: SectionId;
  counts: Partial<Record<SectionId, number>>;
  onTabClick?: (id: SectionId) => void;
}) {
  return (
    // sticky below the navbar; NO negative margin — stays within the container width
    <div className="sticky top-16 z-20 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 mb-0">
      <div className="flex overflow-x-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        {SECTION_IDS.map((id) => {
          const { label, icon } = TAB_META[id];
          const count = counts[id];
          const isActive = id === active;
          const isRed = id === "criminal" && !!count && count > 0;
          return (
            <button
              key={id}
              onClick={() => { scrollToSection(id); onTabClick?.(id); }}
              className={`relative cursor-pointer flex items-center gap-1.5 px-3.5 py-3 text-sm whitespace-nowrap shrink-0 transition-colors ${
                isActive
                  ? "text-gray-900 dark:text-white font-medium"
                  : "text-gray-800 dark:text-gray-400 hover:text-blue-600 hover:font-medium dark:hover:text-blue-300"
              }`}
            >
              <span
                className={
                  isActive ? "text-blue-500 dark:text-blue-400" : "opacity-60"
                }
              >
                {icon}
              </span>
              {label}
              {count !== undefined && count > 0 && (
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full leading-none ${
                    isRed
                      ? "bg-red-100 text-red-700 dark:bg-red-900/70 dark:text-red-300"
                      : "bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400"
                  }`}
                >
                  {count}
                </span>
              )}
              {isActive && (
                <span className="absolute bottom-0 inset-x-0 h-0.5 bg-blue-500 dark:bg-blue-400 rounded-t-full" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Performance ────────────────────────────────────────────────────────────

function PerformanceBar({
  label,
  description,
  value,
  natAvg,
  stateAvg,
  maxValue,
  unit,
  icon: Icon,
  iconBgClass,
  iconColorClass,
  citation,
}: {
  label: string;
  description: string;
  value: number;
  natAvg: number;
  stateAvg: number;
  maxValue: number;
  unit: string;
  icon?: React.ComponentType<{ size?: number; className?: string }>;
  iconBgClass?: string;
  iconColorClass?: string;
  citation?: Citation | null;
}) {
  const { ref, inView } = useInView(0.05);
  const pct = maxValue > 0 ? Math.min((value / maxValue) * 100, 100) : 0;
  const natAvgPct = maxValue > 0 ? Math.min((natAvg / maxValue) * 100, 100) : 0;
  const stateAvgPct =
    maxValue > 0 ? Math.min((stateAvg / maxValue) * 100, 100) : 0;
  return (
    <div
      ref={ref}
      className="py-4 border-b border-gray-100 dark:border-gray-800 last:border-0"
    >
      <div className="flex items-start justify-between gap-4 mb-4">
        {/* Icon + Label + description + citation */}
        <div className="flex items-center gap-3 min-w-0">
          {Icon && (
            <div
              className={`shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${iconBgClass ?? "bg-gray-100 dark:bg-gray-800"}`}
            >
              <Icon
                size={20}
                className={iconColorClass ?? "text-gray-500 dark:text-gray-400"}
              />
            </div>
          )}
          <div className="min-w-0">
            <p className="text-gray-800 dark:text-gray-100 leading-snug font-semibold text-[15px]">
              {label}
            </p>
            <div className="flex items-center gap-1 mt-1 mb-1">
              <Text
                variant="small"
                className="text-gray-400 dark:text-gray-500 text-xs leading-none"
              >
                {description}
              </Text>
              <CitationLink citation={citation ?? null} label={label} />
            </div>
          </div>
        </div>
        {/* Value + avg */}
        <span className="shrink-0 text-xl font-bold text-gray-900 dark:text-white tabular-nums">
          {value}
          {unit}
          <span className="text-gray-400 dark:text-gray-500 font-normal text-xs">
            {" "}
            · nat {natAvg} {unit} · state {stateAvg}
            {unit}
          </span>
        </span>
      </div>
      {/* Track — no overflow-hidden so avg marker can extend beyond track height */}
      <div className="relative w-full bg-gray-100 dark:bg-gray-800 rounded-full h-1.5">
        {/* Fill */}
        <div
          className="absolute left-0 top-0 h-full bg-blue-400 dark:bg-blue-500 rounded-full transition-[width] duration-700 ease-out"
          style={{ width: inView ? `${pct}%` : "0%" }}
        />

        {/* National Avg marker */}
        <div
          className="group absolute -top-1.5 -bottom-1.5 w-1.25 rounded-full bg-orange-400 dark:bg-orange-500 transition-[left] duration-700 ease-out cursor-pointer"
          style={{ left: inView ? `${natAvgPct}%` : "0%" }}
        >
          {/* National Tooltip Container */}
          <div className="absolute bottom-full left-1/2 z-30 mb-2 -translate-x-1/2 whitespace-nowrap rounded bg-orange-50 px-2 py-1 text-xs font-semibold text-orange-600 opacity-0 transition-opacity duration-200 pointer-events-none group-hover:opacity-100 shadow-md">
            National Avg: {natAvg} {unit}
            {/* Tooltip Arrow */}
            <div className="absolute top-full left-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-0.5 bg-orange-50 rotate-45"></div>
          </div>
        </div>

        {/* State avg marker */}
        <div
          className="group absolute -top-1.5 -bottom-1.5 w-1.25 rounded-full bg-green-600 dark:bg-green-500 transition-[left] duration-700 ease-out cursor-pointer"
          style={{ left: inView ? `${stateAvgPct}%` : "0%" }}
        >
          {/* State Tooltip Container */}
          <div className="absolute bottom-full left-1/2 z-30 mb-2 -translate-x-1/2 whitespace-nowrap rounded bg-green-100 px-2 py-1 text-xs font-semibold text-green-700 opacity-0 transition-opacity duration-200 pointer-events-none group-hover:opacity-100 shadow-md">
            State Avg: {stateAvg} {unit} {/* Tooltip Arrow */}
            <div className="absolute top-full left-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-0.5 bg-green-100 rotate-45"></div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PerformanceSection({
  performance,
  hasData,
  performanceCitations,
}: {
  performance: { attendance: number; questions: number; debates: number };
  hasData: boolean;
  performanceCitations?: Politician["performance_citations"];
}) {
  const { trackEvent } = useAnalytics();
  // maxValue: larger of actual value or 1.4× national avg so both value and marker fit
  const maxQ = Math.max(performance.questions, NATIONAL_AVG.questions) * 1.4;
  const maxD = Math.max(performance.debates, NATIONAL_AVG.debates) * 1.4;

  // National rank — only meaningful when there is real data
  const score =
    performance.attendance + performance.questions + performance.debates;
  const rank = Math.max(1, Math.floor(543 - score / 10));

  return (
    <SectionCard id="performance" analyticsSection="performance">
      {/* Header with inline "vs national avg" */}
      <div className="flex items-center gap-2.5 px-5 pt-5 pb-4 border-b border-gray-100 dark:border-gray-800">
        <NextImage
          src="/logo/barChart.svg"
          alt=""
          width={24}
          height={24}
          className="object-contain opacity-75 shrink-0 dark:invert"
        />
        <Text
          variant="h4"
          weight="bold"
          className="text-gray-900 dark:text-white text-[16px]"
        >
          Performance
        </Text>
        {hasData && (
          <span className="text-xs text-gray-500 dark:text-gray-500 font-normal">
            vs national & state avg
          </span>
        )}
      </div>

      {!hasData ? (
        <div className="px-5 py-8 text-center space-y-2">
          <Text
            variant="small"
            className="text-gray-400 dark:text-gray-500 block"
          >
            Performance data not yet available for this politician.
          </Text>
          <a
            href="https://eci.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            onClick={() =>
              trackEvent("external_link_click", {
                link_text: "Check ECI website for official records",
                link_url: "https://eci.gov.in",
                page_location: "politician_profile_performance",
              })
            }
            className="group inline-flex items-center gap-1 text-xs font-semibold text-orange-600 transition-colors hover:text-orange-700 hover:underline dark:text-orange-400 dark:hover:text-orange-300"
          >
            Check ECI website for official records
            <svg
              className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5"
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
          </a>
        </div>
      ) : (
        <div className="px-5 pt-1 pb-3">
          <PerformanceBar
            label="Attendance"
            description="Sessions attended in Parliament"
            value={performance.attendance}
            natAvg={NATIONAL_AVG.attendance}
            stateAvg={STATE_AVG.attendance}
            maxValue={100}
            unit="%"
            icon={CalendarCheck}
            iconBgClass="bg-green-100 dark:bg-green-900/30"
            iconColorClass="text-green-600 dark:text-green-400"
            citation={performanceCitations?.attendance}
          />
          <PerformanceBar
            label="Questions Asked"
            description="Questions raised on the floor"
            value={performance.questions}
            natAvg={NATIONAL_AVG.questions}
            stateAvg={STATE_AVG.questions}
            maxValue={maxQ}
            unit=""
            icon={HelpCircle}
            iconBgClass="bg-blue-100 dark:bg-blue-900/30"
            iconColorClass="text-blue-600 dark:text-blue-400"
            citation={performanceCitations?.questions}
          />
          <PerformanceBar
            label="Debates Participated"
            description="Debates the candidate took part in"
            value={performance.debates}
            natAvg={NATIONAL_AVG.debates}
            stateAvg={STATE_AVG.debates}
            maxValue={maxD}
            icon={MessageSquare}
            iconBgClass="bg-purple-100 dark:bg-purple-900/30"
            iconColorClass="text-purple-600 dark:text-purple-400"
            unit=""
            citation={performanceCitations?.debates}
          />

          {/* National Rank — always shown when there is any performance data */}
          <div className="py-4 flex items-start justify-between gap-4">
            <div className="flex items-center gap-3 min-w-0">
              <div className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center bg-amber-100 dark:bg-amber-900/30">
                <Trophy
                  size={20}
                  className="text-amber-600 dark:text-amber-400"
                />
              </div>
              <div className="min-w-0">
                <p className="text-gray-800 dark:text-gray-100 leading-snug font-semibold text-[15px]">
                  National Rank
                </p>
                <Text
                  variant="small"
                  className="text-gray-400 dark:text-gray-500 text-xs mt-0.5"
                >
                  Among all Politicians
                </Text>
              </div>
            </div>
            <span className="text-2xl font-bold shrink-0 text-gray-900 dark:text-white tabular-nums">
              {rank}
            </span>
          </div>

          {/* Footer note */}

          <div className="border-t border-gray-100 dark:border-gray-800 pt-3 pb-2 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
            {/* Left Spacer to keep text perfectly centered on desktop */}
            <div className="hidden md:block w-36" />

            {/* Source Text Notice */}
            <div>
              {(performanceCitations?.attendance ||
                performanceCitations?.questions ||
                performanceCitations?.debates) && (
                <p className="text-xs text-gray-400 dark:text-gray-600 text-center pb-2 pt-2">
                  Per-metric source links appear next to descriptions where
                  available.
                </p>
              )}
            </div>

            {/* Color-Coded Markers Legend */}
            <div className="flex items-center justify-center md:justify-end gap-3 text-xs font-medium text-gray-500 dark:text-gray-400 min-w-36">
              {/* State Marker */}
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-green-600 dark:bg-green-500 shrink-0" />
                <span className="text-gray-500 dark:text-gray-400 text-[10px]">State Avg</span>
              </div>

              {/* National Marker */}
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-orange-400 dark:bg-orange-500 shrink-0" />
                <span className="text-gray-500 dark:text-gray-400 text-[10px]">National Avg</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </SectionCard>
  );
}

// ── Criminal Records ───────────────────────────────────────────────────────

const CRIME_PREVIEW = 3;

function CriminalRecordsSection({
  records,
  politicianId,
}: {
  records: Politician["criminal_records"];
  politicianId: string;
}) {
  const { trackEvent } = useAnalytics();
  const [expanded, setExpanded] = useState(false);
  const list = records ?? [];
  const visible = expanded ? list : list.slice(0, CRIME_PREVIEW);
  const hiddenCount = list.length - CRIME_PREVIEW;

  return (
    <SectionCard id="criminal" analyticsSection="criminal_records">
      <SectionHeader
        logoSrc="/logo/criminal-record.svg"
        title="Criminal records"
        countLabel={
          list.length > 0
            ? `${list.length} case${list.length !== 1 ? "s" : ""}`
            : undefined
        }
      />
      {list.length === 0 ? (
        <EmptyState message="No criminal records data available." />
      ) : (
        <>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {visible.map((c, i) => (
              <div
                key={i}
                className="px-5 py-3.5 bg-red-50/50 dark:bg-red-900/10 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <div className="flex items-start gap-2 justify-between">
                  <div className="flex items-start gap-1.5 min-w-0 flex-1">
                    <p className="text-[16px] font-semibold text-red-700 dark:text-red-300 leading-snug mb-1.5">
                      {c.name}
                    </p>
                    <CitationLink
                      citation={c.citation ?? null}
                      label={`Case: ${c.name}`}
                      className="shrink-0 mt-0.5"
                    />
                  </div>
                  {c.type && (
                    <span className="shrink-0 text-[10px] font-bold px-2 py-0.5 rounded bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 uppercase tracking-wide">
                      {c.type}
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-500 mt-1 font-medium">
                  {[c.year, c.type, formatSource(c.citation?.source)]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
              </div>
            ))}
          </div>
          {hiddenCount > 0 && (
            <div className="border-t border-dashed border-gray-200 dark:border-gray-700 px-5 py-3">
              <button
                onClick={() => {
                  const next = !expanded;
                  setExpanded(next);
                  trackEvent("section_expand", {
                    section: "criminal_records",
                    action: next ? "expand" : "collapse",
                    politician_id: politicianId,
                  });
                }}
                className="w-full text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 py-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
              >
                {expanded ? "Show less ↑" : `Show ${hiddenCount} more ↓`}
              </button>
            </div>
          )}
        </>
      )}
    </SectionCard>
  );
}

// ── Political History ──────────────────────────────────────────────────────

function PoliticalHistorySection({
  elections,
}: {
  elections: Politician["political_background"]["elections"];
  summary?: string | null;
  summaryCitation?: Citation | null;
}) {
  return (
    <SectionCard id="history" analyticsSection="political_history">
      <SectionHeader
        logoSrc="/logo/parliament_new.svg"
        title="Political History"
        countLabel={
          elections.length > 0
            ? `${elections.length} term${elections.length !== 1 ? "s" : ""}`
            : undefined
        }
      />
      {elections.length === 0 ? (
        <EmptyState message="No political history data available." />
      ) : (
        <>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {elections.map((e, i) => (
              <div
                key={i}
                className="px-5 py-3.5 flex items-center justify-between gap-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-1 flex-wrap">
                    <Text
                      variant="small"
                      weight="semibold"
                      className="text-gray-900 dark:text-white text-[15px]"
                    >
                      {e.constituency} · {e.year} · {e.type}
                    </Text>
                    <CitationLink
                      citation={e.citation ?? null}
                      label={`Election ${e.year}`}
                      className="shrink-0"
                    />
                  </div>
                  <p className="text-gray-500 dark:text-gray-400 text-[13px] font-medium mt-1">
                    {e.party}
                  </p>
                </div>
                <span
                  className={`shrink-0 px-3 py-1 rounded-lg text-xs font-bold ${
                    e.status === "WON"
                      ? "bg-green-500 text-white dark:bg-green-900/40 dark:text-green-500"
                      : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300"
                  }`}
                >
                  {e.status}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </SectionCard>
  );
}

// ── Education — full-width cards with Show N more ─────────────────────────

const EDUCATION_PREVIEW = 3;

function EducationSection({
  education,
  politicianId,
}: {
  education: Politician["education"];
  politicianId: string;
}) {
  const { trackEvent } = useAnalytics();
  const [expanded, setExpanded] = useState(false);
  const list = education ?? [];
  const visible = expanded ? list : list.slice(0, EDUCATION_PREVIEW);
  const hiddenCount = list.length - EDUCATION_PREVIEW;

  return (
    <SectionCard id="education" analyticsSection="education">
      <SectionHeader
        logoSrc="/logo/graduation.svg"
        title="Education"
        countLabel={
          list.length > 0
            ? `${list.length} qualification${list.length !== 1 ? "s" : ""}`
            : undefined
        }
      />
      {list.length === 0 ? (
        <EmptyState message="Education details not yet available." />
      ) : (
        <>
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {visible.map((e, i) => (
              <div
                key={i}
                className="px-5 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <Text
                    variant="small"
                    weight="semibold"
                    className="text-gray-900 dark:text-white flex-1 text-[15px]"
                  >
                    {e.qualification}
                  </Text>
                  <CitationLink
                    citation={e.citation ?? null}
                    label={`Education: ${e.qualification}`}
                    className="shrink-0 mt-0.5"
                  />
                </div>
                {(e.institution || e.year_completed) && (
                  <p className="text-gray-500 dark:text-gray-400 text-[13px] font-medium mt-1">
                    {[
                      e.institution,
                      e.year_completed ? `(${e.year_completed})` : null,
                    ]
                      .filter(Boolean)
                      .join(" ")}
                  </p>
                )}
              </div>
            ))}
          </div>
          {hiddenCount > 0 && (
            <div className="border-t border-dashed border-gray-200 dark:border-gray-700 px-5 py-3">
              <button
                onClick={() => {
                  const next = !expanded;
                  setExpanded(next);
                  trackEvent("section_expand", {
                    section: "education",
                    action: next ? "expand" : "collapse",
                    politician_id: politicianId,
                  });
                }}
                className="w-full text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 py-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
              >
                {expanded ? "Show less ↑" : `Show ${hiddenCount} more ↓`}
              </button>
            </div>
          )}
        </>
      )}
    </SectionCard>
  );
}

// ── Family — 2-col grid ────────────────────────────────────────────────────

function FamilySection({
  members,
}: {
  members: Politician["family_background"];
}) {
  const list = members ?? [];
  return (
    <SectionCard id="family" analyticsSection="family">
      <SectionHeader
        logoSrc="/logo/familyRecord.svg"
        title="Family Background"
        countLabel={
          list.length > 0
            ? `${list.length} member${list.length !== 1 ? "s" : ""}`
            : undefined
        }
      />
      {list.length === 0 ? (
        <EmptyState message="Family details not yet available." />
      ) : (
        <div
          className={`p-5 grid gap-3 ${list.length === 1 ? "grid-cols-1" : "grid-cols-1 sm:grid-cols-2"}`}
        >
          {list.map((m, i) => (
            <div
              key={i}
              className="bg-orange-50 dark:bg-yellow-900/15 rounded-xl p-4 border border-orange-100 dark:border-yellow-800/60"
            >
              <div className="flex items-start gap-1">
                <Text
                  variant="small"
                  weight="semibold"
                  className="text-gray-900 dark:text-white flex-1 text-[15px] capitalize"
                >
                  {toTitleCase(m.name)}
                </Text>
                <CitationLink
                  citation={m.citation ?? null}
                  label={`Family: ${m.name}`}
                  className="shrink-0"
                />
              </div>
              <p className="text-gray-500 dark:text-gray-400 text-[13px] font-medium mt-1 capitalize">
                {m.relation}
              </p>
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  );
}

// ── Contact — icons + circular social buttons ──────────────────────────────

function ContactSection({ politician }: { politician: Politician }) {
  const { trackEvent } = useAnalytics();
  const { contact, social_media, contact_citations } = politician;

  const contactRows = [
    {
      key: "email",
      Icon: Mail,
      value: contact?.email,
      citation: contact_citations?.email,
    },
    {
      key: "phone",
      Icon: Phone,
      value: contact?.phone,
      citation: contact_citations?.phone,
    },
    {
      key: "address",
      Icon: MapPin,
      value: contact?.address,
      citation: contact_citations?.address,
    },
  ].filter((r) => r.value) as {
    key: string;
    Icon: typeof Mail;
    value: string;
    citation: Citation | null | undefined;
  }[];

  const socialLinks = [
    {
      key: "twitter",
      href: social_media?.twitter,
      label: "X (Twitter)",
      Icon: IconX,
      hover:
        "hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black",
    },
    {
      key: "facebook",
      href: social_media?.facebook,
      label: "Facebook",
      Icon: IconFacebook,
      hover: "hover:bg-blue-600 hover:text-white",
    },
    {
      key: "instagram",
      href: social_media?.instagram,
      label: "Instagram",
      Icon: IconInstagram,
      hover: "hover:bg-pink-600 hover:text-white",
    },
    {
      key: "linkedin",
      href: social_media?.linkedin,
      label: "LinkedIn",
      Icon: IconLinkedIn,
      hover: "hover:bg-blue-700 hover:text-white",
    },
    {
      key: "youtube",
      href: social_media?.youtube,
      label: "YouTube",
      Icon: IconYouTube,
      hover: "hover:bg-red-600 hover:text-white",
    },
    {
      key: "website",
      href: social_media?.website,
      label: "Website",
      Icon: IconGlobe,
      hover: "hover:bg-green-600 hover:text-white",
    },
  ].filter((s) => s.href);

  const hasAny = contactRows.length > 0 || socialLinks.length > 0;

  return (
    <SectionCard id="contact" analyticsSection="contact">
      <SectionHeader
        logoSrc="/logo/contact.svg"
        title="Contact & Social Media"
      />
      {!hasAny ? (
        <EmptyState message="Contact info not yet available." />
      ) : (
        <div className="px-5 py-2">
          {/* Contact rows with icons — center-aligned so icon never floats */}
          {contactRows.map(({ key, Icon, value, citation }) => (
            <div
              key={key}
              className={`flex gap-3 py-3 border-b border-gray-100 dark:border-gray-800 last:border-0 ${
                key === "address" ? "items-start" : "items-center"
              }`}
            >
              <Icon
                size={14}
                className={`text-gray-400 shrink-0 ${key === "address" ? "mt-0.5" : ""}`}
              />
              <Text
                variant="small"
                className="text-gray-700 dark:text-gray-300 flex-1 break-all"
              >
                {value}
              </Text>
              <CitationLink
                citation={citation ?? null}
                label={key}
                className="shrink-0"
              />
            </div>
          ))}

          {/* Social circular icon buttons */}
          {socialLinks.length > 0 && (
            <div
              className={`flex flex-wrap gap-2 py-3 ${contactRows.length > 0 ? "border-t border-gray-100 dark:border-gray-800" : ""}`}
            >
              {socialLinks.map(({ key, label, Icon, href, hover }) => (
                <div key={key} className="flex items-center gap-1">
                  <a
                    href={href!}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={label}
                    title={label}
                    onClick={() =>
                      trackEvent("external_link_click", {
                        link_text: label,
                        link_url: href!,
                        page_location: "politician_profile_contact",
                      })
                    }
                    className={`w-9 h-9 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-600 dark:text-gray-300 transition-colors ${hover}`}
                  >
                    <Icon />
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </SectionCard>
  );
}

// ── Know More / CTA ────────────────────────────────────────────────────────

function KnowMoreSection({
  name,
  onReportClick,
  contributeHref,
  onContributeClick,
}: {
  name: string;
  onReportClick: () => void;
  contributeHref: string;
  onContributeClick: () => void;
}) {
  return (
    <div
      data-analytics-section="contribute_cta"
      className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-5 mb-4 shadow-sm"
    >
      <Text
        variant="h4"
        weight="bold"
        className="text-gray-900 dark:text-white mb-0.5"
      >
        Know more about {toTitleCase(name)}?
      </Text>
      <Text variant="small" className="text-gray-500 dark:text-gray-400 mb-4">
        Help us enrich this profile with accurate information.
      </Text>
      <div className="grid gap-3 sm:grid-cols-2">
        {/* Report — neutral, no flashy hover */}
        <div className="flex flex-col rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/60 p-4 hover:border-orange-200 dark:hover:border-orange-400/50 hover:bg-orange-50/30 dark:hover:bg-orange-900/10 transition-colors">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/40 flex items-center justify-center shrink-0">
              <AlertTriangle
                size={14}
                className="text-orange-600 dark:text-orange-400"
              />
            </div>
            <Text
              variant="small"
              weight="semibold"
              className="text-gray-900 dark:text-white"
            >
              Found an issue?
            </Text>
          </div>
          <Text
            variant="small"
            className="text-gray-600 dark:text-gray-300 mb-4 flex-1 leading-relaxed"
          >
            Flag incorrect or missing profile details to help keep this page
            accurate.
          </Text>
          <button
            onClick={onReportClick}
            className="self-start px-4 py-2 text-sm font-semibold rounded-lg border border-orange-600 text-orange-700 dark:text-orange-400 dark:border-orange-400 bg-white dark:bg-gray-800 hover:bg-red-100 hover:text-red-700 hover:border hover:border-red-600 dark:hover:bg-red-900/30 dark:hover:border dark:hover:border-red-600 dark:hover:text-white transition-colors"
          >
            Report Inaccuracy
          </button>
        </div>
        {/* Contribute — muted orange, not gradient */}
        <div className="flex flex-col rounded-xl border border-orange-200 dark:border-yellow-800 bg-orange-50 dark:bg-yellow-900/15 p-4 hover:bg-orange-100/60 dark:hover:bg-orange-900/25 hover:border-orange-300 dark:hover:border-yellow-700 transition-colors">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/40 flex items-center justify-center shrink-0">
              <UserPlus
                size={14}
                className="text-orange-600 dark:text-orange-400"
              />
            </div>
            <Text
              variant="small"
              weight="semibold"
              className="text-gray-900 dark:text-white"
            >
              Contribute Info
            </Text>
          </div>
          <Text
            variant="small"
            className="text-gray-600 dark:text-gray-300 mb-4 flex-1 leading-relaxed"
          >
            Add verified education, family, criminal, or contact details for
            this politician.
          </Text>
          <a
            href={contributeHref}
            target="_blank"
            rel="noopener noreferrer"
            onClick={onContributeClick}
            className="self-start px-4 py-2 text-sm font-semibold rounded-lg bg-orange-500 hover:bg-orange-600 text-white transition-colors"
          >
            Contribute Info
          </a>
        </div>
      </div>
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────

export default function PoliticianPageClient({
  politician: p,
  routeSegment,
}: PoliticianPageClientProps) {
  const router = useRouter();
  const { trackEvent } = useAnalytics();
  const analyticsReady = useDeferredMount();
  const sectionsContainerRef = useRef<HTMLDivElement>(null);
  const activeSection = useScrollSpy();
  const [shareState, setShareState] = useState<"idle" | "copied" | "error">("idle");
  const shareTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Clean up the revert timer on unmount so we never set state on an unmounted component.
  useEffect(() => {
    return () => {
      if (shareTimerRef.current) clearTimeout(shareTimerRef.current);
    };
  }, []);

  const { slug: routeSlug, uuidShort: routeUuidShort } =
    extractSlugAndOptionalUuid(routeSegment);

  const elections = p.political_background?.elections ?? [];
  const latestElection = elections[0];
  const party = latestElection?.party ?? "—";
  const isMp = p.type === "MP";
  const performance = p.performance ?? {
    attendance: 0,
    questions: 0,
    debates: 0,
  };
  const hasPerformanceData =
    performance.attendance > 0 ||
    performance.questions > 0 ||
    performance.debates > 0;
  const summary = p.political_background?.summary;

  const tabCounts: Partial<Record<SectionId, number>> = {
    criminal: p.criminal_records?.length ?? 0,
    history: elections.length,
    education: p.education?.length ?? 0,
    family: p.family_background?.length ?? 0,
  };

  const handleShare = async () => {
    if (shareTimerRef.current) clearTimeout(shareTimerRef.current);

    const name = toTitleCase(p.name);
    const url = typeof window !== "undefined" ? window.location.href : "";
    const shareText = `Check out ${name}'s record on Rajniti: ${url}`;

    try {
      if (typeof navigator !== "undefined" && navigator.share) {
        // Native share sheet (mobile browsers)
        await navigator.share({ title: `${name} on Rajniti`, text: shareText, url });
        trackEvent("profile_share", {
          method: "native_share",
          politician_id: p.id,
          politician_name: name,
        });
      } else {
        // Clipboard fallback (desktop)
        await navigator.clipboard.writeText(shareText);
        setShareState("copied");
        trackEvent("profile_share", {
          method: "clipboard",
          politician_id: p.id,
          politician_name: name,
        });
        shareTimerRef.current = setTimeout(() => setShareState("idle"), 2000);
      }
    } catch (err) {
      // Silently ignore user dismissing the native share tray
      if (err instanceof Error && err.name === "AbortError") return;
      // Clipboard write failed — show brief error state
      setShareState("error");
      shareTimerRef.current = setTimeout(() => setShareState("idle"), 2000);
    }
  };

  const buildReportIssueUrl = () => {
    const pageUrl = typeof window !== "undefined" ? window.location.href : "";
    const title = `Report Inaccuracy: ${toTitleCase(p.name)}`;
    const body = `## Politician Information\n\nName: ${toTitleCase(p.name)}\nPolitician ID: ${p.id}\nProfile URL: ${pageUrl}\n\n## What is incorrect?\n\nDescribe the incorrect or missing information here.\n\n## Suggested correction\n\nAdd the correct information here.\n\n## Additional Notes\n\nOptional notes/screenshots.`;
    return `https://github.com/imsks/rajniti/issues/new?${new URLSearchParams({ title, body })}`;
  };

  const handleReportClick = () => {
    trackEvent("report_inaccuracy_click", {
      politician_id: p.id,
      politician_name: toTitleCase(p.name),
    });
    window.open(buildReportIssueUrl(), "_blank", "noopener,noreferrer");
  };

  const contributeHref = `https://github.com/imsks/rajniti/issues/new?title=${encodeURIComponent(`Enrich ${toTitleCase(p.name)}`)}&body=${encodeURIComponent(`Politician ID: ${p.id}\n\nPlease add details below:`)}`;

  const handleContributeClick = () => {
    trackEvent("contribute_click", {
      contribute_type: "info",
      politician_id: p.id,
      page_location: "politician_detail",
    });
  };

  return (
    <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
      {analyticsReady && (
        <PoliticianPageAnalytics
          politician={p}
          sectionsContainerRef={sectionsContainerRef}
          routeSlug={routeSlug}
          routeUuidShort={routeUuidShort}
        />
      )}

      <Navbar sticky />

      {/* Restore original max width */}
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Back */}
        <div className="mb-6">
          <Button
            onClick={() => router.back()}
            variant="secondary"
            size="sm"
            leftIcon={
              <svg
                className="w-4 h-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
            }
          >
            Back
          </Button>
        </div>

        {/* Hero card */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-4">
          <div className="flex flex-col sm:flex-row gap-5 items-start">
            {/* Photo */}
            <div className="shrink-0">
              {p.photo ? (
                <Image
                  src={p.photo}
                  alt={toTitleCase(p.name)}
                  width={112}
                  height={112}
                  priority
                  quality={75}
                  sizes="112px"
                  className="w-28 h-28 rounded-2xl object-cover border-4 border-orange-100 dark:border-orange-900/40"
                />
              ) : (
                <div className="w-28 h-28 rounded-2xl bg-linear-to-br from-orange-100 to-orange-200 dark:from-orange-900/40 dark:to-orange-800/40 flex items-center justify-center border-4 border-orange-100 dark:border-orange-900/40">
                  <NextImage
                    src="/logo/Parliament.svg"
                    alt=""
                    width={56}
                    height={56}
                    className="w-14 h-14 object-contain"
                  />
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              {/* Top row: name + badge on the left, share button pinned to the right */}
              <div className="flex items-start justify-between gap-3">
                {/* Name + badge — wraps naturally on long names, never pushes the button down */}
                <div className="flex items-center gap-2.5 mb-1.5 flex-wrap min-w-0">
                  <Text
                    variant="h2"
                    weight="bold"
                    className="text-gray-900 dark:text-white leading-tight"
                  >
                    {toTitleCase(p.name)}
                  </Text>
                  <span
                    className={`shrink-0 px-2.5 py-0.5 rounded-full text-xs font-bold ${
                      isMp
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
                        : "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300"
                    }`}
                  >
                    {p.type}
                  </span>
                </div>

                {/* Share — circular icon button, always top-right, never wraps */}
                <button
                  onClick={handleShare}
                  aria-label={
                    shareState === "copied"
                      ? "Link copied to clipboard"
                      : shareState === "error"
                      ? "Failed to copy — try again"
                      : "Share this politician profile"
                  }
                  className={`shrink-0 w-9 h-9 rounded-full flex items-center justify-center
                    transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1
                    focus:ring-orange-300 dark:focus:ring-orange-600 cursor-pointer
                    ${
                      shareState === "copied"
                        ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
                        : shareState === "error"
                        ? "bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-300"
                        : " bg-orange-500/20 hover:bg-orange-600/80 text-orange-500 dark:hover:bg-orange-600 dark:hover:text-text-white hover:text-orange-50 transition-colors"
                    }`}
                >
                  {shareState === "copied" ? (
                    <Check size={16} className="stroke-2"/>
                  ) : shareState === "error" ? (
                    <AlertTriangle size={16} className="stroke-2" />
                  ) : (
                    <Share2 size={16} className="stroke-2" />
                  )}
                </button>
              </div>

              {/* Compact single-line: Constituency · State · Party */}
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {toTitleCase(p.constituency)} · {p.state} · {party}
              </p>

              {/* Updated chip */}
              {p.updated_at && formatUpdatedAt(p.updated_at) && (
                <div className="mt-3">
                  <span className="inline-flex items-center gap-1 text-xs text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 rounded-full px-2.5 py-1">
                    <Clock size={11} />
                    {formatUpdatedAt(p.updated_at)}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Summary spans full card width — below both photo and name */}
          {summary && (
            <p className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
              {summary}
            </p>
          )}
        </div>

        {/* Sticky section tab nav — no gap between it and sections */}
        <SectionTabNav
          active={activeSection}
          counts={tabCounts}
          onTabClick={(id) =>
            trackEvent("profile_tab_click", {
              tab_name: id,
              politician_id: p.id,
              politician_name: toTitleCase(p.name),
            })
          }
        />

        {/* All sections — ref for analytics IntersectionObserver */}
        <div ref={sectionsContainerRef} className="pt-4">
          <PerformanceSection
            performance={performance}
            hasData={hasPerformanceData}
            performanceCitations={p.performance_citations}
          />
          <CriminalRecordsSection records={p.criminal_records} politicianId={p.id} />
          <PoliticalHistorySection
            elections={elections}
            summary={p.political_background?.summary}
            summaryCitation={p.political_background?.summary_citation}
          />
          <EducationSection education={p.education} politicianId={p.id} />
          <FamilySection members={p.family_background} />
          <ContactSection politician={p} />
          <KnowMoreSection
            name={p.name}
            onReportClick={handleReportClick}
            contributeHref={contributeHref}
            onContributeClick={handleContributeClick}
          />
        </div>
      </div>

      <Footer />
    </div>
  );
}
