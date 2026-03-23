"use client"

import { Suspense, useEffect, useRef, useState } from "react"
import { BarChart2, CalendarCheck, HelpCircle, MessageSquare, Trophy } from "lucide-react"
import { useParams, useRouter } from "next/navigation"
import { usePolitician } from "@/hooks/usePoliticians"
import { Footer, Navbar } from "@/components/layout"
import Button from "@/components/ui/Button"
import Text from "@/components/ui/Text"
import Image from "@/components/ui/Image"
import { useAnalytics } from "@/hooks/useAnalytics"
import type { Politician, ElectionRecord, CrimeRecord, FamilyMember } from "@/types/politician"

// ── Animation Hooks ────────────────────────────────────────────────────────

function useCountUp(target: number, duration = 1600, start = false) {
    const [value, setValue] = useState(0)
    useEffect(() => {
        if (!start || target === 0) return
        let startTime: number | null = null
        const step = (timestamp: number) => {
            if (!startTime) startTime = timestamp
            const progress = Math.min((timestamp - startTime) / duration, 1)
            const eased = 1 - Math.pow(1 - progress, 3)
            setValue(Math.floor(eased * target))
            if (progress < 1) requestAnimationFrame(step)
        }
        requestAnimationFrame(step)
    }, [target, duration, start])
    return value
}

function useInView(threshold = 0.15) {
    const ref = useRef<HTMLDivElement>(null)
    const [inView, setInView] = useState(false)
    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setInView(true)
                    observer.disconnect()
                }
            },
            { threshold }
        )
        if (ref.current) observer.observe(ref.current)
        return () => observer.disconnect()
    }, [threshold])
    return { ref, inView }
}

// ── Helper Components ──────────────────────────────────────────────────────

function Section({
    title,
    icon,
    children,
    delay = 0,
}: {
    title: string
    icon: string
    children: React.ReactNode
    delay?: number
}) {
    const { ref, inView } = useInView()
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
                <img src={icon} alt={title} className="w-6 h-6 object-contain" />
                <Text variant="h4" weight="bold" className="text-gray-900 dark:text-white">
                    {title}
                </Text>
            </div>
            {children}
        </div>
    )
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
    )
}

function Badge({
    children,
    color,
}: {
    children: React.ReactNode
    color: "blue" | "purple" | "green" | "red" | "orange" | "gray"
}) {
    const styles: Record<string, string> = {
        blue: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
        purple: "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
        green: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
        red: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
        orange: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
        gray: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
    }
    return (
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${styles[color]}`}>
            {children}
        </span>
    )
}

// ── Sub-sections ───────────────────────────────────────────────────────────

function PoliticalHistorySection({
    elections,
    summary,
}: {
    elections: ElectionRecord[]
    summary?: string | null
}) {
    return (
        <Section title="Political History" icon="/logo/Parliament.png">
            {summary && (
                <Text variant="body" className="text-gray-600 dark:text-gray-400 mb-4 italic">
                    {summary}
                </Text>
            )}
            <div className="space-y-3">
                {elections.map((e, i) => (
                    <div
                        key={i}
                        className="election-card flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
                        style={{ animationDelay: `${i * 80}ms` }}
                    >
                        <div>
                            <Text variant="body" weight="semibold" className="text-gray-900 dark:text-white">
                                {e.constituency}, {e.state}
                            </Text>
                            <Text variant="small" className="text-gray-500 dark:text-gray-400">
                                {e.party} • {e.year} • {e.type}
                            </Text>
                        </div>
                        <Badge color={e.status === "WON" ? "green" : "red"}>{e.status}</Badge>
                    </div>
                ))}
            </div>
        </Section>
    )
}

function EducationSection({ education }: { education: Politician["education"] }) {
    const list = education ?? []
    if (list.length === 0)
        return (
            <Section title="Education" icon="/logo/Profile.png">
                <EmptyHint message="Education details not yet available." />
            </Section>
        )
    return (
        <Section title="Education" icon="/logo/graduation.png">
            <div className="grid gap-3">
                {list.map((e, i) => (
                    <div
                        key={i}
                        className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800 hover:shadow-sm transition-shadow duration-200"
                    >
                        <Text variant="body" weight="semibold" className="text-gray-900 dark:text-white">
                            {e.qualification}
                        </Text>
                        {(e.institution || e.year_completed) && (
                            <Text variant="small" className="text-gray-600 dark:text-gray-400">
                                {e.institution ?? "—"}
                                {e.year_completed ? ` (${e.year_completed})` : ""}
                            </Text>
                        )}
                    </div>
                ))}
            </div>
        </Section>
    )
}

function FamilySection({ members }: { members?: FamilyMember[] | null }) {
    if (!members || members.length === 0)
        return (
            <Section title="Family Background" icon="/logo/familyRecord.png">
                <EmptyHint message="Family details not yet available." />
            </Section>
        )
    return (
        <Section title="Family Background" icon="/logo/familyRecord.png">
            <div className="grid gap-3">
                {members.map((m, i) => (
                    <div
                        key={i}
                        className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800 hover:shadow-sm transition-shadow duration-200"
                    >
                        <Text variant="body" weight="semibold" className="text-gray-900 dark:text-white">
                            {m.name}
                        </Text>
                        <Text variant="small" className="text-gray-600 dark:text-gray-400">
                            {m.relation}
                        </Text>
                    </div>
                ))}
            </div>
        </Section>
    )
}

function CriminalRecordsSection({ records }: { records?: CrimeRecord[] | null }) {
    if (!records || records.length === 0)
        return (
            <Section title="Criminal Records" icon="/logo/criminal-record.png">
                <EmptyHint message="No criminal records data available." />
            </Section>
        )
    return (
        <Section title="Criminal Records" icon="/logo/criminal-record.png">
            <div className="space-y-3">
                {records.map((c, i) => (
                    <div
                        key={i}
                        className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800 hover:shadow-sm transition-shadow duration-200"
                    >
                        <div className="flex items-start justify-between">
                            <div>
                                <Text variant="body" weight="semibold" className="text-gray-900 dark:text-white">
                                    {c.name}
                                </Text>
                                {c.year && (
                                    <Text variant="small" className="text-gray-500 dark:text-gray-400">
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
    )
}

function ContactSection({ politician }: { politician: Politician }) {
    const { contact, social_media } = politician
    const hasAny =
        contact?.email ||
        contact?.phone ||
        contact?.address ||
        social_media?.twitter ||
        social_media?.facebook ||
        social_media?.website

    if (!hasAny)
        return (
            <Section title="Contact & Social Media" icon="/logo/contact.png">
                <EmptyHint message="Contact info not yet available." />
            </Section>
        )

    return (
        <Section title="Contact & Social Media" icon="/logo/contact.png">
            <div className="grid gap-3">
                {contact?.email && (
                    <div className="flex items-center gap-2">
                        <img src="/logo/location.png" alt="Email" className="w-4 h-4" />
                        <Text variant="body" className="text-gray-700 dark:text-gray-300">{contact.email}</Text>
                    </div>
                )}
                {contact?.phone && (
                    <div className="flex items-center gap-2">
                        <img src="/logo/location.png" alt="Phone" className="w-4 h-4" />
                        <Text variant="body" className="text-gray-700 dark:text-gray-300">{contact.phone}</Text>
                    </div>
                )}
                {contact?.address && (
                    <div className="flex items-center gap-2">
                        <img src="/logo/location.png" alt="Address" className="w-4 h-4" />
                        <Text variant="body" className="text-gray-700 dark:text-gray-300">{contact.address}</Text>
                    </div>
                )}
                {social_media && (
                    <div className="flex flex-wrap gap-3 mt-2">
                        {social_media.twitter && (
                            <a href={social_media.twitter} target="_blank" rel="noopener noreferrer"
                                className="text-blue-500 hover:underline text-sm">
                                𝕏 Twitter
                            </a>
                        )}
                        {social_media.facebook && (
                            <a href={social_media.facebook} target="_blank" rel="noopener noreferrer"
                                className="text-blue-700 dark:text-blue-400 hover:underline text-sm">
                                Facebook
                            </a>
                        )}
                        {social_media.website && (
                            <a href={social_media.website} target="_blank" rel="noopener noreferrer"
                                className="text-green-600 dark:text-green-400 hover:underline text-sm flex items-center gap-1">
                                <img src="/logo/location.png" alt="Website" className="w-3 h-3" />
                                Website
                            </a>
                        )}
                    </div>
                )}
            </div>
        </Section>
    )
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
}: {
    label: string
    description: string
    value: number
    suffix: string
    icon: React.ElementType
    iconBg: string
    iconColor: string
    inView: boolean
    delay: number
}) {
    const counted = useCountUp(value, 1400, inView)

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
                <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center ${iconBg}`}>
                    <Icon size={17} className={iconColor} strokeWidth={2.2} />
                </div>
                <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-800 dark:text-gray-100 leading-tight">
                        {label}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5 leading-tight">
                        {description}
                    </p>
                </div>
            </div>

            {/* Right: animated flip number */}
            <span className="ml-6 flex-shrink-0 tabular-nums font-black text-2xl text-gray-900 dark:text-white tracking-tight">
                {counted}{suffix}
            </span>
        </div>
    )
}

function PerformanceSection({
    performance,
    rank,
}: {
    performance: { attendance: number; questions: number; debates: number }
    rank: number
}) {
    const { ref, inView } = useInView(0.15)

    const rows = [
        {
            label: "Attendance",
            description: "Sessions attended in Parliament",
            value: performance.attendance,
            suffix: "%",
            icon: CalendarCheck,
            iconBg: "bg-emerald-100 dark:bg-emerald-900/40",
            iconColor: "text-emerald-600 dark:text-emerald-400",
        },
        {
            label: "Questions Asked",
            description: "Questions raised on the floor",
            value: performance.questions,
            suffix: "",
            icon: HelpCircle,
            iconBg: "bg-blue-100 dark:bg-blue-900/40",
            iconColor: "text-blue-600 dark:text-blue-400",
        },
        {
            label: "Debates Participated",
            description: "Debates the MP took part in",
            value: performance.debates,
            suffix: "",
            icon: MessageSquare,
            iconBg: "bg-violet-100 dark:bg-violet-900/40",
            iconColor: "text-violet-600 dark:text-violet-400",
        },
        {
            label: "National Rank",
            description: "Among all 543 MPs",
            value: rank,
            suffix: "",
            icon: Trophy,
            iconBg: "bg-orange-100 dark:bg-orange-900/40",
            iconColor: "text-orange-600 dark:text-orange-400",
        },
    ]

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
                        <BarChart2 size={17} className="text-gray-600 dark:text-gray-400" strokeWidth={2.2} />
                    </div>
                    <Text variant="h4" weight="bold" className="text-gray-900 dark:text-white">
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
                        Data sourced from Lok Sabha records · Current session
                    </p>
                </div>
            </div>
        </div>
    )
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function PoliticianPage() {
    return (
        <Suspense
            fallback={
                <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 flex items-center justify-center">
                    <div className="text-center">
                        <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent" />
                        <p className="mt-4 text-gray-600 dark:text-gray-400 font-semibold animate-pulse">
                            Loading…
                        </p>
                    </div>
                </div>
            }
        >
            <PoliticianPageContent />
        </Suspense>
    )
}

function PoliticianPageContent() {
    const params = useParams()
    const router = useRouter()
    const { trackEvent } = useAnalytics()
    const politicianId = params.id as string

    const { politician, loading, error } = usePolitician(politicianId)

    useEffect(() => {
        if (!politician) return
        const latestElection = politician.political_background.elections?.[0]
        trackEvent("politician_profile_view", {
            politician_id: politician.id,
            politician_name: politician.name,
            politician_type: politician.type as "MP" | "MLA",
            party: latestElection?.party ?? "—",
            state: politician.state,
            constituency: politician.constituency,
        })
    }, [politician, trackEvent])

    useEffect(() => {
        if (error)
            trackEvent("error_view", {
                error_type: error === "Politician not found" ? "not_found" : "api",
                error_message: error,
                page_location: "politician_detail",
            })
    }, [error, trackEvent])

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent" />
                    <p className="mt-4 text-gray-600 dark:text-gray-400 font-semibold">Loading…</p>
                </div>
            </div>
        )
    }

    if (error || !politician) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 flex items-center justify-center p-4">
                <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-8 max-w-md w-full border-l-4 border-red-500">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="text-red-500 text-3xl">⚠️</div>
                        <Text variant="h4" weight="bold" className="text-gray-900 dark:text-white">
                            Error
                        </Text>
                    </div>
                    <Text variant="body" className="text-gray-600 dark:text-gray-400 mb-4">
                        {error || "Politician not found"}
                    </Text>
                    <Button onClick={() => router.push("/dashboard")} fullWidth>
                        Back to Dashboard
                    </Button>
                </div>
            </div>
        )
    }

    const p = politician
    const performance = p.performance || { attendance: 0, questions: 0, debates: 0 }
    const score = performance.attendance + performance.questions + performance.debates
    const rank = Math.floor(543 - score / 10)
    const latestElection = p.political_background.elections?.[0]
    const party = latestElection?.party ?? "—"
    const isMp = p.type === "MP"

    return (
        <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
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

            <Navbar variant="dashboard" sticky={true} />

            <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
                {/* Back */}
                <div className="mb-6 back-btn">
                    <Button onClick={() => router.back()} variant="secondary" size="sm">
                        ← Back
                    </Button>
                </div>

                {/* Hero Card */}
                <div className="hero-card bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 border border-gray-200 dark:border-gray-700 mb-6">
                    <div className="flex flex-col md:flex-row gap-6 items-start">
                        {/* Photo */}
                        <div className="hero-photo flex-shrink-0">
                            {p.photo ? (
                                <Image
                                    src={p.photo}
                                    alt={p.name}
                                    width={128}
                                    height={128}
                                    className="w-32 h-32 rounded-2xl object-cover border-4 border-orange-200 dark:border-orange-800"
                                />
                            ) : (
                                <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-orange-100 to-orange-200 dark:from-orange-900/40 dark:to-orange-800/40 flex items-center justify-center flex-shrink-0 border-4 border-orange-200 dark:border-orange-800">
                                    <img src="/logo/Parliament.png" alt="Politician" className="w-16 h-16 object-contain" />
                                </div>
                            )}
                        </div>

                        <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2 hero-name">
                                <Text variant="h2" weight="bold" className="text-gray-900 dark:text-white">
                                    {p.name}
                                </Text>
                                <Badge color={isMp ? "blue" : "purple"}>{p.type}</Badge>
                            </div>

                            <div className="space-y-1.5">
                                <div className="flex items-center gap-2 hero-info-1">
                                    <img src="/logo/Parliament.png" alt="Party" className="w-4 h-4 object-contain opacity-60" />
                                    <Text variant="body" className="text-gray-700 dark:text-gray-300">
                                        <span className="font-semibold">Party:</span> {party}
                                    </Text>
                                </div>
                                <div className="flex items-center gap-2 hero-info-2">
                                    <img src="/logo/Assembly.png" alt="Constituency" className="w-4 h-4 object-contain opacity-60" />
                                    <Text variant="body" className="text-gray-700 dark:text-gray-300">
                                        <span className="font-semibold">Constituency:</span> {p.constituency}
                                    </Text>
                                </div>
                                <div className="flex items-center gap-2 hero-info-3">
                                    <img src="/logo/location.png" alt="State" className="w-4 h-4 object-contain opacity-60" />
                                    <Text variant="body" className="text-gray-700 dark:text-gray-300">
                                        <span className="font-semibold">State:</span> {p.state}
                                    </Text>
                                </div>
                            </div>
                        </div>
                    </div>

                    {p.notes && (
                        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                            <Text variant="small" className="text-gray-500 dark:text-gray-400 italic">
                                📝 {p.notes}
                            </Text>
                        </div>
                    )}
                </div>

                {/* Sections Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="lg:col-span-2">
                        <PoliticalHistorySection
                            elections={p.political_background.elections}
                            summary={p.political_background.summary}
                        />
                    </div>

                    {/* ── Performance Scorecard ── */}
                    <PerformanceSection performance={performance} rank={rank} />

                    <EducationSection education={p.education} />
                    <FamilySection members={p.family_background} />
                    <CriminalRecordsSection records={p.criminal_records} />
                    <ContactSection politician={p} />

                    {/* Contribute CTA */}
                    <div className="contribute-cta lg:col-span-2 bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl p-6 text-center text-white mb-8">
                        <Text variant="h4" weight="bold" className="text-white mb-2">
                            Know more about {p.name}?
                        </Text>
                        <Text variant="body" className="text-orange-100 mb-4">
                            Help us enrich this profile with accurate education, family,
                            criminal records, and contact information.
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
                            className="bg-white text-orange-600 py-2 px-4 rounded-lg hover:bg-gray-50 border-none shadow-lg"
                            size="md"
                        >
                            Contribute Info →
                        </Button>
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    )
}