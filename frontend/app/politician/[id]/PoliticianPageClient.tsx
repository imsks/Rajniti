"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import NextImage from "next/image";
import {
  AlertTriangle,
  BarChart2,
  CalendarCheck,
  HelpCircle,
  Mail,
  MapPin,
  MessageSquare,
  Phone,
  Trophy,
  UserPlus,
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
import type {
  Politician,
  ElectionRecord,
  CrimeRecord,
  FamilyMember,
  Citation,
} from "@/types/politician";

// ── Animation Hooks ────────────────────────────────────────────────────────

function useCountUp(target: number, duration = 1600, start = false) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (!start || target === 0) return;
    let startTime: number | null = null;
    let raf = 0;
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.floor(eased * target));
      if (progress < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration, start]);
  return value;
}

function useInView(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [threshold]);
  return { ref, inView };
}

// ── Shared style maps (module scope — created once, not per render) ──────────

const BADGE_STYLES = {
  blue: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  purple:
    "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
  green: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  red: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  orange:
    "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  gray: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
} as const;

type BadgeColor = keyof typeof BADGE_STYLES;

// ── Inline brand icons (no extra dependency) ─────────────────────────────────
// Single-path SVGs use currentColor so each link controls its own colour.

const brandIconProps = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "currentColor",
  "aria-hidden": true,
} as const;

function XIcon() {
  return (
    <svg {...brandIconProps}>
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.45-6.231Zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77Z" />
    </svg>
  );
}

function FacebookIcon() {
  return (
    <svg {...brandIconProps}>
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073Z" />
    </svg>
  );
}

function InstagramIcon() {
  return (
    <svg {...brandIconProps}>
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069ZM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0Zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324ZM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881Z" />
    </svg>
  );
}

function LinkedInIcon() {
  return (
    <svg {...brandIconProps}>
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286ZM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065Zm1.782 13.019H3.555V9h3.564v11.452ZM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003Z" />
    </svg>
  );
}

function YouTubeIcon() {
  return (
    <svg {...brandIconProps}>
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814ZM9.545 15.568V8.432L15.818 12l-6.273 3.568Z" />
    </svg>
  );
}

function GlobeIcon() {
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

// ── Helper Components ──────────────────────────────────────────────────────

function Section({
  title,
  icon,
  children,
  delay = 0,
}: {
  title: string;
  icon: string;
  children: React.ReactNode;
  delay?: number;
}) {
  const { ref, inView } = useInView();
  return (
    <div
      ref={ref}
      className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6 transition-shadow duration-300 hover:shadow-md"
      style={{
        opacity: inView ? 1 : 0,
        transform: inView ? "translateY(0)" : "translateY(32px)",
        transition: `opacity 0.55s ease ${delay}ms, transform 0.55s ease ${delay}ms, box-shadow 0.3s ease`,
      }}
    >
      <div className="flex items-center gap-3 mb-4">
        <NextImage
          src={icon}
          alt={title}
          width={24}
          height={24}
          className="w-6 h-6 object-contain dark:brightness-0 dark:invert"
        />
        <Text
          variant="h4"
          weight="bold"
          className="text-gray-900 dark:text-white"
        >
          {title}
        </Text>
      </div>
      {children}
    </div>
  );
}

function EmptyHint({ message }: { message: string }) {
  return (
    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-dashed border-gray-300 dark:border-gray-600 text-center">
      <Text variant="small" className="text-gray-400 dark:text-gray-500">
        {message}
      </Text>
      <a
        href="https://github.com/imsks/rajniti/issues/new"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block mt-2 text-xs text-orange-600 dark:text-orange-400 hover:underline font-semibold"
      >
        Help us add this info →
      </a>
    </div>
  );
}

function Badge({
  children,
  color,
}: {
  children: React.ReactNode;
  color: BadgeColor;
}) {
  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-bold ${BADGE_STYLES[color]}`}
    >
      {children}
    </span>
  );
}

// ── Sub-sections ───────────────────────────────────────────────────────────

function PoliticalHistorySection({
  elections,
  summary,
  summaryCitation,
}: {
  elections: ElectionRecord[];
  summary?: string | null;
  summaryCitation?: Citation | null;
}) {
  return (
    <Section title="Political History" icon="/logo/parliament_new.svg">
      {summary && (
        <div className="flex items-start gap-1 mb-4">
          <Text
            variant="body"
            className="text-gray-600 dark:text-gray-400 italic flex-1"
          >
            {summary}
          </Text>
          <CitationLink
            citation={summaryCitation ?? null}
            label="Political summary"
          />
        </div>
      )}
      <div className="space-y-3">
        {elections.map((e, i) => (
          <div
            key={i}
            className="election-card flex items-center justify-between bg-linear-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
            style={{ animationDelay: `${i * 80}ms` }}
          >
            <div className="flex items-start gap-2 min-w-0">
              <div className="min-w-0">
                <Text
                  variant="body"
                  weight="semibold"
                  className="text-gray-900 dark:text-white"
                >
                  {e.constituency}, {e.state}
                </Text>
                <Text
                  variant="small"
                  className="text-gray-500 dark:text-gray-400"
                >
                  {e.party} • {e.year} • {e.type}
                </Text>
              </div>
              <CitationLink
                citation={e.citation}
                label={`Election ${e.year} ${e.constituency}`}
                className="shrink-0 mt-0.5"
              />
            </div>
            <Badge color={e.status === "WON" ? "green" : "red"}>
              {e.status}
            </Badge>
          </div>
        ))}
      </div>
    </Section>
  );
}

function EducationSection({
  education,
}: {
  education: Politician["education"];
}) {
  const list = education ?? [];
  if (list.length === 0) {
    return (
      <Section title="Education" icon="/logo/Profile.svg">
        <EmptyHint message="Education details not yet available." />
      </Section>
    );
  }
  return (
    <Section title="Education" icon="/logo/graduation.svg">
      <div className="grid gap-3">
        {list.map((e, i) => (
          <div
            key={i}
            className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800 hover:shadow-sm transition-shadow duration-200"
          >
            <div className="flex items-center gap-1">
              <Text
                variant="body"
                weight="semibold"
                className="text-gray-900 dark:text-white"
              >
                {e.qualification}
              </Text>
              <CitationLink
                citation={e.citation}
                label={`Education: ${e.qualification}`}
              />
            </div>
            {(e.institution || e.year_completed) && (
              <Text
                variant="small"
                className="text-gray-600 dark:text-gray-400"
              >
                {e.institution ?? "—"}
                {e.year_completed ? ` (${e.year_completed})` : ""}
              </Text>
            )}
          </div>
        ))}
      </div>
    </Section>
  );
}

function FamilySection({ members }: { members?: FamilyMember[] | null }) {
  if (!members || members.length === 0) {
    return (
      <Section title="Family Background" icon="/logo/familyRecord.svg">
        <EmptyHint message="Family details not yet available." />
      </Section>
    );
  }
  return (
    <Section title="Family Background" icon="/logo/familyRecord.svg">
      <div className="grid gap-3">
        {members.map((m, i) => (
          <div
            key={i}
            className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800 hover:shadow-sm transition-shadow duration-200"
          >
            <div className="flex items-center gap-1">
              <Text
                variant="body"
                weight="semibold"
                className="text-gray-900 dark:text-white"
              >
                {m.name}
              </Text>
              <CitationLink citation={m.citation} label={`Family: ${m.name}`} />
            </div>
            <Text variant="small" className="text-gray-600 dark:text-gray-400">
              {m.relation}
            </Text>
          </div>
        ))}
      </div>
    </Section>
  );
}

function CriminalRecordsSection({
  records,
}: {
  records?: CrimeRecord[] | null;
}) {
  if (!records || records.length === 0) {
    return (
      <Section title="Criminal Records" icon="/logo/criminal-record.svg">
        <EmptyHint message="No criminal records data available." />
      </Section>
    );
  }
  return (
    <Section title="Criminal Records" icon="/logo/criminal-record.svg">
      <div className="space-y-3">
        {records.map((c, i) => (
          <div
            key={i}
            className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800 hover:shadow-sm transition-shadow duration-200"
          >
            <div className="flex items-start gap-1 justify-between flex-1">
              <div>
                <div className="flex items-center gap-1">
                  <Text
                    variant="body"
                    weight="semibold"
                    className="text-gray-900 dark:text-white"
                  >
                    {c.name}
                  </Text>
                  <CitationLink
                    citation={c.citation}
                    label={`Case: ${c.name}`}
                  />
                </div>
                {c.year && (
                  <Text
                    variant="small"
                    className="text-gray-500 dark:text-gray-400"
                  >
                    Year: {c.year}
                  </Text>
                )}
              </div>
              {c.type && <Badge color="red">{c.type}</Badge>}
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
}

function ContactSection({ politician }: { politician: Politician }) {
  const { contact, social_media, contact_citations } = politician;
  const hasAny =
    contact?.email ||
    contact?.phone ||
    contact?.address ||
    social_media?.twitter ||
    social_media?.facebook ||
    social_media?.instagram ||
    social_media?.linkedin ||
    social_media?.youtube ||
    social_media?.website;

  if (!hasAny) {
    return (
      <Section title="Contact & Social Media" icon="/logo/contact.svg">
        <EmptyHint message="Contact info not yet available." />
      </Section>
    );
  }

  return (
    <Section title="Contact & Social Media" icon="/logo/contact.svg">
      <div className="grid gap-3">
        {contact?.email && (
          <div className="flex items-center gap-2">
            <Mail
              size={16}
              className="shrink-0 text-gray-400 dark:text-gray-500"
            />
            <Text variant="body" className="text-gray-700 dark:text-gray-300">
              {contact.email}
            </Text>
            <CitationLink citation={contact_citations?.email} label="Email" />
          </div>
        )}
        {contact?.phone && (
          <div className="flex items-center gap-2">
            <Phone
              size={16}
              className="shrink-0 text-gray-400 dark:text-gray-500"
            />
            <Text variant="body" className="text-gray-700 dark:text-gray-300">
              {contact.phone}
            </Text>
            <CitationLink citation={contact_citations?.phone} label="Phone" />
          </div>
        )}
        {contact?.address && (
          <div className="flex items-center gap-2">
            <MapPin
              size={16}
              className="shrink-0 text-gray-400 dark:text-gray-500"
            />
            <Text
              variant="body"
              className="text-gray-700 dark:text-gray-300 text-sm"
            >
              {contact.address}
            </Text>
            <CitationLink
              citation={contact_citations?.address}
              label="Address"
            />
          </div>
        )}
        {social_media && (
          <div className="flex flex-wrap items-center gap-2 mt-2">
            {(
              [
                {
                  key: "twitter",
                  href: social_media.twitter,
                  label: "X (Twitter)",
                  Icon: XIcon,
                  hover:
                    "hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black",
                },
                {
                  key: "facebook",
                  href: social_media.facebook,
                  label: "Facebook",
                  Icon: FacebookIcon,
                  hover: "hover:bg-blue-600 hover:text-white",
                },
                {
                  key: "instagram",
                  href: social_media.instagram,
                  label: "Instagram",
                  Icon: InstagramIcon,
                  hover: "hover:bg-pink-600 hover:text-white",
                },
                {
                  key: "linkedin",
                  href: social_media.linkedin,
                  label: "LinkedIn",
                  Icon: LinkedInIcon,
                  hover: "hover:bg-blue-700 hover:text-white",
                },
                {
                  key: "youtube",
                  href: social_media.youtube,
                  label: "YouTube",
                  Icon: YouTubeIcon,
                  hover: "hover:bg-red-600 hover:text-white",
                },
                {
                  key: "website",
                  href: social_media.website,
                  label: "Website",
                  Icon: GlobeIcon,
                  hover: "hover:bg-green-600 hover:text-white",
                },
              ] as const
            )
              .filter((s) => Boolean(s.href))
              .map(({ key, href, label, Icon, hover }) => (
                <a
                  key={key}
                  href={href as string}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  title={label}
                  className={`flex h-9 w-9 items-center justify-center rounded-full bg-gray-100 text-gray-600 transition-colors dark:bg-gray-800 dark:text-gray-300 ${hover}`}
                >
                  <Icon />
                </a>
              ))}
          </div>
        )}
      </div>
    </Section>
  );
}

// ── Performance Scorecard ──────────────────────────────────────────────────

function ScoreRow({
  label,
  description,
  value,
  suffix,
  icon: Icon,
  iconBg,
  iconColor,
  inView,
  delay,
  citation,
}: {
  label: string;
  description: string;
  value: number;
  suffix: string;
  icon: React.ElementType;
  iconBg: string;
  iconColor: string;
  inView: boolean;
  delay: number;
  citation?: Citation | null;
}) {
  const counted = useCountUp(value, 1400, inView);

  return (
    <div
      className="flex items-center justify-between py-4 px-1 group"
      style={{
        opacity: inView ? 1 : 0,
        transform: inView ? "translateX(0)" : "translateX(-20px)",
        transition: `opacity 0.5s ease ${delay}ms, transform 0.5s ease ${delay}ms`,
      }}
    >
      {/* Left: icon + label + description */}
      <div className="flex items-center gap-3 min-w-0">
        <div
          className={`shrink-0 w-9 h-9 rounded-xl flex items-center justify-center ${iconBg}`}
        >
          <Icon size={17} className={iconColor} strokeWidth={2.2} />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-gray-800 dark:text-gray-100 leading-tight">
            {label}
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5 leading-tight flex items-center gap-1">
            {description}
            <CitationLink
              citation={citation}
              label={label}
              className="inline"
            />
          </p>
        </div>
      </div>

      {/* Right: animated count number */}
      <span className="ml-6 shrink-0 tabular-nums font-black text-2xl text-gray-900 dark:text-white tracking-tight">
        {counted}
        {suffix}
      </span>
    </div>
  );
}

function PerformanceSection({
  performance,
  rank,
  performanceCitations,
}: {
  performance: { attendance: number; questions: number; debates: number };
  rank: number;
  performanceCitations?: Politician["performance_citations"];
}) {
  const { ref, inView } = useInView(0.15);

  // Rebuilt only when inputs change, not on every render.
  const rows = useMemo(
    () => [
      {
        label: "Attendance",
        description: "Sessions attended in Parliament",
        value: performance.attendance,
        suffix: "%",
        icon: CalendarCheck,
        iconBg: "bg-emerald-100 dark:bg-emerald-900/40",
        iconColor: "text-emerald-600 dark:text-emerald-400",
        citation: performanceCitations?.attendance,
      },
      {
        label: "Questions Asked",
        description: "Questions raised on the floor",
        value: performance.questions,
        suffix: "",
        icon: HelpCircle,
        iconBg: "bg-blue-100 dark:bg-blue-900/40",
        iconColor: "text-blue-600 dark:text-blue-400",
        citation: performanceCitations?.questions,
      },
      {
        label: "Debates Participated",
        description: "Debates the MP took part in",
        value: performance.debates,
        suffix: "",
        icon: MessageSquare,
        iconBg: "bg-violet-100 dark:bg-violet-900/40",
        iconColor: "text-violet-600 dark:text-violet-400",
        citation: performanceCitations?.debates,
      },
      {
        label: "National Rank",
        description: "Among all Politicians",
        value: rank,
        suffix: "",
        icon: Trophy,
        iconBg: "bg-orange-100 dark:bg-orange-900/40",
        iconColor: "text-orange-600 dark:text-orange-400",
        citation: null,
      },
    ],
    [performance, rank, performanceCitations],
  );

  const hasMetricCitations = Boolean(
    performanceCitations?.attendance ||
    performanceCitations?.questions ||
    performanceCitations?.debates,
  );

  return (
    <div className="lg:col-span-2" ref={ref}>
      <div
        className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6 hover:shadow-md transition-shadow duration-300"
        style={{
          opacity: inView ? 1 : 0,
          transform: inView ? "translateY(0)" : "translateY(32px)",
          transition: "opacity 0.55s ease, transform 0.55s ease",
        }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 mb-2">
          <div className="w-8 h-8 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
            <BarChart2
              size={17}
              className="text-gray-600 dark:text-gray-400"
              strokeWidth={2.2}
            />
          </div>
          <Text
            variant="h4"
            weight="bold"
            className="text-gray-900 dark:text-white"
          >
            Performance
          </Text>
        </div>

        {/* Divider */}
        <div className="h-px bg-gray-100 dark:bg-gray-800 mb-1" />

        {/* Rows */}
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {rows.map((row, i) => (
            <ScoreRow
              key={row.label}
              {...row}
              inView={inView}
              delay={100 + i * 130}
            />
          ))}
        </div>

        {/* Footer note */}
        <div
          className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800"
          style={{
            opacity: inView ? 1 : 0,
            transition: "opacity 0.5s ease 650ms",
          }}
        >
          <p className="text-xs text-gray-400 dark:text-gray-600 text-center">
            {hasMetricCitations
              ? "Per-metric source links appear next to descriptions where available."
              : "Data sourced from Lok Sabha records · Current session"}
          </p>
        </div>
      </div>
    </div>
  );
}

// ── Route-segment parsing ──────────────────────────────────────────────────

function isFullUuid(value: string) {
  return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(
    value,
  );
}

function extractSlugAndOptionalUuid(input: string) {
  // Supports:
  // - UUID: /politician/<full-uuid>
  // - Slug: /politician/<slug>
  // - Slug + short suffix: /politician/<slug>-8fba2f3f
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

// ── Main Page ──────────────────────────────────────────────────────────────

export type PoliticianPageClientProps = {
  politician: Politician;
  /** Raw `[id]` route segment (slug, UUID, or slug-short). */
  routeSegment: string;
};

export default function PoliticianPageClient({
  politician: p,
  routeSegment,
}: PoliticianPageClientProps) {
  const router = useRouter();
  const { trackEvent } = useAnalytics();
  const analyticsReady = useDeferredMount();
  const { slug: routeSlug, uuidShort: routeUuidShort } =
    extractSlugAndOptionalUuid(routeSegment);

  const sectionsContainerRef = useRef<HTMLDivElement>(null);
  const performance = p.performance || {
    attendance: 0,
    questions: 0,
    debates: 0,
  };
  const score =
    performance.attendance + performance.questions + performance.debates;
  const rank = Math.floor(543 - score / 10);
  const elections = p.political_background?.elections ?? [];
  const latestElection = elections[0];
  const party = latestElection?.party ?? "—";
  const isMp = p.type === "MP";

  const handleReportClick = () => {
    trackEvent("report_inaccuracy_click", {
      politician_id: p.id,
      politician_name: p.name,
    });
    const pageUrl = typeof window !== "undefined" ? window.location.href : "";
    const title = `Report Inaccuracy: ${p.name}`;
    const body = `## Politician Information\n\nName: ${p.name}\nPolitician ID: ${p.id}\nPage: ${pageUrl}\n\n## What is incorrect?\n\nDescribe the incorrect or missing information here.\n\n## Suggested correction\n\nAdd the correct information here.\n\n## Additional Notes\n\nOptional notes/screenshots.`;
    const params = new URLSearchParams({ title, body });
    window.open(
      `https://github.com/imsks/rajniti/issues/new?${params.toString()}`,
      "_blank",
      "noopener,noreferrer",
    );
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
      <style>{`
                @keyframes fadeSlideUp {
                    0%  { opacity: 0; transform: translateY(24px); }
                    100%{ opacity: 1; transform: translateY(0); }
                }
                @keyframes fadeIn {
                    0%  { opacity: 0; }
                    100%{ opacity: 1; }
                }
                @keyframes slideInLeft {
                    0%  { opacity: 0; transform: translateX(-20px); }
                    100%{ opacity: 1; transform: translateX(0); }
                }
                .hero-card   { animation: fadeSlideUp 0.65s cubic-bezier(0.22,1,0.36,1) both; }
                .back-btn    { animation: slideInLeft 0.45s cubic-bezier(0.22,1,0.36,1) both; }
                .hero-photo  { animation: fadeIn 0.7s ease 0.15s both; }
                .hero-name   { animation: fadeSlideUp 0.5s ease 0.25s both; }
                .hero-info-1 { animation: fadeSlideUp 0.45s ease 0.35s both; }
                .hero-info-2 { animation: fadeSlideUp 0.45s ease 0.43s both; }
                .hero-info-3 { animation: fadeSlideUp 0.45s ease 0.51s both; }
                .election-card {
                    animation: slideInLeft 0.45s cubic-bezier(0.22,1,0.36,1) both;
                    transition: box-shadow 0.25s ease, transform 0.25s ease;
                }
                .election-card:hover {
                    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
                    transform: translateX(5px);
                }
                .contribute-cta {
                    animation: fadeSlideUp 0.6s ease 0.1s both;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                .contribute-cta:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 16px 40px rgba(249,115,22,0.25);
                }
            `}</style>

      <Navbar sticky />

      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Back */}
        <div className="mb-6 back-btn">
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

        {/* Hero Card */}
        <div className="hero-card relative bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 border border-gray-200 dark:border-gray-700 mb-6">
          {p.updated_at && (
            <div className="absolute bottom-5 right-5">
              <span className="text-xs text-gray-400 dark:text-gray-500">
                Last Updated: {new Date(p.updated_at).toLocaleDateString("en-GB")}
              </span>
            </div>
          )}
          <div className="flex flex-col md:flex-row gap-6 items-start">
            {/* Photo */}
            <div className="hero-photo shrink-0">
              {p.photo ? (
                <Image
                  src={p.photo}
                  alt={p.name}
                  width={128}
                  height={128}
                  priority
                  quality={75}
                  sizes="128px"
                  className="w-32 h-32 rounded-2xl object-cover border-4 border-orange-200 dark:border-orange-800"
                />
              ) : (
                <div className="w-32 h-32 rounded-2xl bg-linear-to-br from-orange-100 to-orange-200 dark:from-orange-900/40 dark:to-orange-800/40 flex items-center justify-center shrink-0 border-4 border-orange-200 dark:border-orange-800">
                  <NextImage
                    src="/logo/parliament_new.svg"
                    alt="Politician"
                    width={64}
                    height={64}
                    className="w-16 h-16 object-contain dark:brightness-0 dark:invert"
                  />
                </div>
              )}
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2 hero-name">
                <Text
                  variant="h2"
                  weight="bold"
                  className="text-gray-900 dark:text-white"
                >
                  {p.name}
                </Text>
                <Badge color={isMp ? "blue" : "purple"}>{p.type}</Badge>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center gap-2 hero-info-1">
                  <NextImage
                    src="/logo/parliament_new.svg"
                    alt="Party"
                    width={16}
                    height={16}
                    className="w-4 h-4 object-contain opacity-60 dark:brightness-0 dark:invert"
                  />
                  <Text
                    variant="body"
                    className="text-gray-700 dark:text-gray-300"
                  >
                    <span className="font-semibold">Party:</span> {party}
                  </Text>
                </div>
                <div className="flex items-center gap-2 hero-info-2">
                  <NextImage
                    src="/logo/Assembly.svg"
                    alt="Constituency"
                    width={16}
                    height={16}
                    className="w-4 h-4 object-contain opacity-60 dark:brightness-0 dark:invert"
                  />
                  <Text
                    variant="body"
                    className="text-gray-700 dark:text-gray-300"
                  >
                    <span className="font-semibold">Constituency:</span>{" "}
                    {p.constituency}
                  </Text>
                </div>
                <div className="flex items-center gap-2 hero-info-3">
                  <NextImage
                    src="/logo/location.svg"
                    alt="State"
                    width={16}
                    height={16}
                    className="w-4 h-4 object-contain opacity-60 dark:brightness-0 dark:invert"
                  />
                  <Text
                    variant="body"
                    className="text-gray-700 dark:text-gray-300"
                  >
                    <span className="font-semibold">State:</span> {p.state}
                  </Text>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sections Grid — ref used for IntersectionObserver section tracking.
            Wrapper divs are layout/analytics only; all theming lives on the
            Section component itself so dark mode stays consistent. */}
        <div
          ref={sectionsContainerRef}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          <div
            className="lg:col-span-2"
            data-analytics-section="political_history"
          >
            <PoliticalHistorySection
              elections={elections}
              summary={p.political_background?.summary}
              summaryCitation={p.political_background?.summary_citation}
            />
          </div>

          {/* ── Performance Scorecard ── */}
          <div data-analytics-section="performance">
            <PerformanceSection
              performance={performance}
              rank={rank}
              performanceCitations={p.performance_citations}
            />
          </div>

          <div data-analytics-section="education">
            <EducationSection education={p.education} />
          </div>
          <div data-analytics-section="family">
            <FamilySection members={p.family_background} />
          </div>
          <div data-analytics-section="criminal_records">
            <CriminalRecordsSection records={p.criminal_records} />
          </div>
          <div data-analytics-section="contact">
            <ContactSection politician={p} />
          </div>

          {/* Know More About Cards */}
          <div
            data-analytics-section="contribute_cta"
            className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 mb-4 shadow-sm transition hover:shadow-md"
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <Text
                  variant="h4"
                  weight="bold"
                  className="text-gray-900 dark:text-white"
                >
                  Know more about {p.name}?
                </Text>
                <Text
                  variant="body"
                  className="text-gray-600 dark:text-gray-400 text-sm"
                >
                  Help us enrich this profile with accurate education, family,
                  criminal records, and contact information.
                </Text>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="group flex flex-col rounded-2xl border mt-6 border-orange-200 bg-orange-50/80 p-3 shadow-sm transition duration-300 hover:border-orange-300 hover:bg-orange-50 dark:border-orange-700 dark:bg-orange-950/20 dark:hover:bg-orange-900/20">
                <div className="flex items-center gap-2">
                  <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300">
                    <AlertTriangle size={16} />
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white text-lg">
                    Found an issue?
                  </span>
                </div>
                <div className="mt-2">
                  <Text
                    variant="body"
                    className="text-gray-600 dark:text-gray-400 text-sm mt-2 leading-6"
                  >
                    Flag incorrect or missing profile details and help us keep
                    this page accurate.
                  </Text>
                  <div className="cursor-pointer transition-transform duration-150 active:scale-95 mt-3">
                    <Button
                      type="button"
                      onClick={handleReportClick}
                      size="md"
                      variant="ghost"
                      className="cursor-pointer rounded-xl border-0 bg-orange-600 px-4 py-1.5 font-semibold text-white shadow-md transition hover:bg-orange-700 hover:text-orange dark:bg-orange-600 dark:text-white dark:hover:bg-orange-500"
                    >
                      Report Inaccuracy
                    </Button>
                  </div>
                </div>
              </div>

              <div className="group flex flex-col rounded-2xl mt-6 bg-linear-to-r from-orange-500 to-orange-600 dark:from-orange-600 dark:to-orange-700 p-3 shadow-lg transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_20px_48px_rgba(249,115,22,0.28)]">
                <div className="flex items-center gap-2">
                  <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-white/20 text-white dark:bg-white/10">
                    <UserPlus size={16} />
                  </div>
                  <span className="font-medium text-white text-lg">
                    Contribute Info
                  </span>
                </div>
                <div className="mt-2">
                  <Text
                    variant="body"
                    className="text-white mt-2 leading-6 text-sm"
                  >
                    Add verified education, family, criminal, or contact details
                    for this politician.
                  </Text>
                  <Button
                    href={`https://github.com/imsks/rajniti/issues/new?title=Enrich+${encodeURIComponent(p.name)}&body=Politician+ID:+${encodeURIComponent(p.id)}%0A%0APlease+add+details+below:`}
                    external
                    onClick={() =>
                      trackEvent("contribute_click", {
                        contribute_type: "info",
                        politician_id: p.id,
                        page_location: "politician_detail",
                      })
                    }
                    size="md"
                    variant="ghost"
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
                    className="rounded-xl mt-3 border-0 bg-white px-4 py-1.5 font-semibold text-orange-600 shadow-md transition hover:bg-orange-50 hover:text-orange-700 dark:bg-white dark:text-orange-600 dark:hover:bg-orange-50 sm:w-auto w-full"
                  >
                    Contribute Info
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
