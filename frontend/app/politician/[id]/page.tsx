"use client"

import { Suspense, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { usePolitician } from "@/hooks/usePoliticians"
import { Footer, Navbar } from "@/components/layout"
import Button from "@/components/ui/Button"
import Text from "@/components/ui/Text"
import Image from "@/components/ui/Image"
import { useAnalytics } from "@/hooks/useAnalytics"
import type { Politician, ElectionRecord, CrimeRecord, FamilyMember } from "@/types/politician"

// ── Helper components ─────────────────────────────────────────────────────

function Section({
    title,
    icon,
    children,
}: {
    title: string
    icon: string
    children: React.ReactNode
}) {
    return (
        <div className='bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6'>
            <div className='flex items-center gap-3 mb-4'>
                <img src={icon} alt={title} className='w-6 h-6 object-contain' />
                <Text variant='h4' weight='bold' className='text-gray-900 dark:text-white'>
                    {title}
                </Text>
            </div>
            {children}
        </div>
    )
}

function EmptyHint({ message }: { message: string }) {
    return (
        <div className='bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border border-dashed border-gray-300 dark:border-gray-600 text-center'>
            <Text variant='small' className='text-gray-400 dark:text-gray-500'>
                {message}
            </Text>
            <a
                href='https://github.com/imsks/rajniti/issues/new'
                target='_blank'
                rel='noopener noreferrer'
                className='inline-block mt-2 text-xs text-orange-600 hover:underline font-semibold'>
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
        blue: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
        purple: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
        green: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
        red: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
        orange: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
        gray: "bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
    }
    return (
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${styles[color]}`}>
            {children}
        </span>
    )
}

// ── Sub-sections ──────────────────────────────────────────────────────────

function PoliticalHistorySection({
    elections,
    summary,
}: {
    elections: ElectionRecord[]
    summary?: string | null
}) {
    return (
        <Section title='Political History' icon='/logo/Parliament.png'>
            {summary && (
                <Text variant='body' className='text-gray-600 dark:text-gray-400 mb-4 italic'>
                    {summary}
                </Text>
            )}
            <div className='space-y-3'>
                {elections.map((e, i) => (
                    <div
                        key={i}
                        className='flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-700/50 dark:to-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700'>
                        <div>
                            <Text variant='body' weight='semibold' className='text-gray-900 dark:text-white'>
                                {e.constituency}, {e.state}
                            </Text>
                            <Text variant='small' className='text-gray-500 dark:text-gray-400'>
                                {e.party} • {e.year} • {e.type}
                            </Text>
                        </div>
                        <Badge color={e.status === "WON" ? "green" : "red"}>
                            {e.status}
                        </Badge>
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
            <Section title='Education' icon='/logo/Profile.png'>
                <EmptyHint message='Education details not yet available.' />
            </Section>
        )

    return (
        <Section title='Education' icon='/logo/graduation.png'>
            <div className='grid gap-3'>
                {list.map((e, i) => (
                    <div key={i} className='bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800'>
                        <Text variant='body' weight='semibold' className='text-gray-900 dark:text-white'>
                            {e.qualification}
                        </Text>
                        {(e.institution || e.year_completed) && (
                            <Text variant='small' className='text-gray-600 dark:text-gray-400'>
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
        return <Section title='Family Background' icon='/logo/familyRecord.png'><EmptyHint message='Family details not yet available.' /></Section>

    return (
        <Section title='Family Background' icon='/logo/familyRecord.png'>
            <div className='grid gap-3'>
                {members.map((m, i) => (
                    <div key={i} className='bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800'>
                        <Text variant='body' weight='semibold' className='text-gray-900 dark:text-white'>
                            {m.name}
                        </Text>
                        <Text variant='small' className='text-gray-600 dark:text-gray-400'>
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
        return <Section title='Criminal Records' icon='/logo/criminal-record.png'><EmptyHint message='No criminal records data available.' /></Section>

    return (
        <Section title='Criminal Records' icon='/logo/criminal-record.png'>
            <div className='space-y-3'>
                {records.map((c, i) => (
                    <div key={i} className='bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800'>
                        <div className='flex items-start justify-between'>
                            <div>
                                <Text variant='body' weight='semibold' className='text-gray-900 dark:text-white'>
                                    {c.name}
                                </Text>
                                {c.year && (
                                    <Text variant='small' className='text-gray-500 dark:text-gray-400'>
                                        Year: {c.year}
                                    </Text>
                                )}
                            </div>
                            {c.type && <Badge color='red'>{c.type}</Badge>}
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
        contact?.email || contact?.phone || contact?.address ||
        social_media?.twitter || social_media?.facebook || social_media?.website

    if (!hasAny)
        return <Section title='Contact & Social Media' icon='/logo/contact.png'><EmptyHint message='Contact info not yet available.' /></Section>

    return (
        <Section title='Contact & Social Media' icon='/logo/contact.png'>
            <div className='grid gap-3'>
                {contact?.email && (
                    <div className='flex items-center gap-2'>
                        <img src='/logo/location.png' alt='Email' className='w-4 h-4' />
                        <Text variant='body' className='text-gray-700 dark:text-gray-300'>{contact.email}</Text>
                    </div>
                )}
                {contact?.phone && (
                    <div className='flex items-center gap-2'>
                        <img src='/logo/location.png' alt='Phone' className='w-4 h-4' />
                        <Text variant='body' className='text-gray-700 dark:text-gray-300'>{contact.phone}</Text>
                    </div>
                )}
                {contact?.address && (
                    <div className='flex items-center gap-2'>
                        <img src='/logo/location.png' alt='Address' className='w-4 h-4' />
                        <Text variant='body' className='text-gray-700 dark:text-gray-300'>{contact.address}</Text>
                    </div>
                )}
                {social_media && (
                    <div className='flex flex-wrap gap-3 mt-2'>
                        {social_media.twitter && (
                            <a href={social_media.twitter} target='_blank' rel='noopener noreferrer' className='text-blue-500 hover:underline text-sm'>𝕏 Twitter</a>
                        )}
                        {social_media.facebook && (
                            <a href={social_media.facebook} target='_blank' rel='noopener noreferrer' className='text-blue-700 hover:underline text-sm'>Facebook</a>
                        )}
                        {social_media.website && (
                            <a href={social_media.website} target='_blank' rel='noopener noreferrer' className='text-green-600 hover:underline text-sm flex items-center gap-1'>
                                <img src='/logo/location.png' alt='Website' className='w-3 h-3' />
                                Website
                            </a>
                        )}
                    </div>
                )}
            </div>
        </Section>
    )
}

// ── Main Page ─────────────────────────────────────────────────────────────

export default function PoliticianPage() {
    return (
        <Suspense fallback={
            <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900 flex items-center justify-center'>
                <div className='inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent'></div>
            </div>
        }>
            <PoliticianPageContent />
        </Suspense>
    )
}

function isFullUuid(value: string) {
    return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(
        value
    )
}

function extractSlugAndOptionalUuid(input: string) {
    // Supports:
    // - UUID: /politician/<full-uuid>
    // - Slug: /politician/<slug>
    // - Slug + short suffix: /politician/<slug>-8fba2f3f
    if (isFullUuid(input)) {
        return { slug: null as string | null, uuid: input, uuidShort: null as string | null }
    }

    const shortMatch = input.match(/-([0-9a-fA-F]{8})$/)
    if (shortMatch) {
        return {
            slug: input.slice(0, -(shortMatch[0].length)),
            uuid: null as string | null,
            uuidShort: shortMatch[1].toLowerCase(),
        }
    }

    return { slug: input, uuid: null as string | null, uuidShort: null as string | null }
}

function PoliticianPageContent() {
    const params = useParams()
    const router = useRouter()
    const { trackEvent } = useAnalytics()
    const slugOrId = params.id as string
    const { slug: routeSlug, uuidShort: routeUuidShort } = extractSlugAndOptionalUuid(slugOrId)

    const { politician, loading, error } = usePolitician(slugOrId)

    useEffect(() => {
        if (!politician) return
        const latestElection = politician.political_background.elections?.[0]
        trackEvent('politician_profile_view', {
            politician_id: politician.id,
            politician_name: politician.name,
            politician_type: politician.type as "MP" | "MLA",
            party: latestElection?.party ?? "—",
            state: politician.state,
            constituency: politician.constituency,
            route_slug: routeSlug,
            route_uuid_short: routeUuidShort,
        })
    }, [politician, trackEvent, routeSlug, routeUuidShort])

    useEffect(() => {
        if (error) trackEvent('error_view', { error_type: error === "Politician not found" ? 'not_found' : 'api', error_message: error, page_location: 'politician_detail' })
    }, [error, trackEvent])

    if (loading) {
        return (
            <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900 flex items-center justify-center'>
                <div className='text-center'>
                    <div className='inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent'></div>
                    <p className='mt-4 text-gray-600 dark:text-gray-400 font-semibold'>Loading…</p>
                </div>
            </div>
        )
    }

    if (error || !politician) {
        return (
            <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900 flex items-center justify-center p-4'>
                <div className='bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full border-l-4 border-red-500'>
                    <div className='flex items-center gap-3 mb-4'>
                        <div className='text-red-500 text-3xl'>⚠️</div>
                        <Text variant='h4' weight='bold' className='text-gray-900 dark:text-white'>
                            Error
                        </Text>
                    </div>
                    <Text variant='body' className='text-gray-600 dark:text-gray-400 mb-4'>
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
    const latestElection = p.political_background.elections?.[0]
    const party = latestElection?.party ?? "—"
    const isMp = p.type === "MP"

    return (
        <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900'>
            <Navbar variant='dashboard' sticky={true} />

            <div className='mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8'>
                {/* Back */}
                <div className='mb-6'>
                    <Button onClick={() => router.back()} variant='secondary' size='sm'>
                        ← Back
                    </Button>
                </div>

                {/* Hero Card */}
                <div className='bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 border border-gray-200 dark:border-gray-700 mb-6'>
                    <div className='flex flex-col md:flex-row gap-6 items-start'>
                        {p.photo ? (
                            <Image
                                src={p.photo}
                                alt={p.name}
                                width={128}
                                height={128}
                                className='w-32 h-32 rounded-2xl object-cover border-4 border-orange-200 dark:border-orange-800 flex-shrink-0'
                            />
                        ) : (
                            <div className='w-32 h-32 rounded-2xl bg-gradient-to-br from-orange-100 to-orange-200 dark:from-orange-900/30 dark:to-orange-800/30 flex items-center justify-center flex-shrink-0 border-4 border-orange-200 dark:border-orange-800'>
                                <img src='/logo/Parliament.png' alt='Politician' className='w-16 h-16 object-contain' />
                            </div>
                        )}

                        <div className='flex-1'>
                            <div className='flex items-center gap-3 mb-2'>
                                <Text variant='h2' weight='bold' className='text-gray-900 dark:text-white'>
                                    {p.name}
                                </Text>
                                <Badge color={isMp ? "blue" : "purple"}>
                                    {p.type}
                                </Badge>
                            </div>

                            <div className='space-y-1.5'>
                                <div className='flex items-center gap-2'>
                                    <img src='/logo/Parliament.png' alt='Party' className='w-4 h-4 object-contain opacity-60' />
                                    <Text variant='body' className='text-gray-700 dark:text-gray-300'>
                                        <span className='font-semibold'>Party:</span> {party}
                                    </Text>
                                </div>
                                <div className='flex items-center gap-2'>
                                    <img src='/logo/Assembly.png' alt='Constituency' className='w-4 h-4 object-contain opacity-60' />
                                    <Text variant='body' className='text-gray-700 dark:text-gray-300'>
                                        <span className='font-semibold'>Constituency:</span>{" "}
                                        {p.constituency}
                                    </Text>
                                </div>
                                <div className='flex items-center gap-2'>
                                    <img src='/logo/location.png' alt='State' className='w-4 h-4 object-contain opacity-60' />
                                    <Text variant='body' className='text-gray-700 dark:text-gray-300'>
                                        <span className='font-semibold'>State:</span>{" "}
                                        {p.state}
                                    </Text>
                                </div>
                            </div>
                        </div>
                    </div>

                    {p.notes && (
                        <div className='mt-4 pt-4 border-t border-gray-100 dark:border-gray-700'>
                            <Text variant='small' className='text-gray-500 dark:text-gray-400 italic'>
                                📝 {p.notes}
                            </Text>
                        </div>
                    )}
                </div>

                {/* Sections */}
                <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
                    <div className='lg:col-span-2'>
                        <PoliticalHistorySection
                            elections={p.political_background.elections}
                            summary={p.political_background.summary}
                        />
                    </div>

                    <EducationSection education={p.education} />

                    <FamilySection members={p.family_background} />

                    <CriminalRecordsSection records={p.criminal_records} />

                    <ContactSection politician={p} />

                    {/* Contribute CTA */}
                    <div className='lg:col-span-2 bg-gradient-to-r from-orange-500 to-orange-600 dark:from-orange-600 dark:to-orange-700 rounded-2xl p-6 text-center text-white mb-8'>
                        <Text variant='h4' weight='bold' className='text-white mb-2'>
                            Know more about {p.name}?
                        </Text>
                        <Text variant='body' className='text-orange-100 mb-4'>
                            Help us enrich this profile with accurate education, family,
                            criminal records, and contact information.
                        </Text>
                        <Button
                            href={`https://github.com/imsks/rajniti/issues/new?title=Enrich+${encodeURIComponent(p.name)}&body=Politician+ID:+${encodeURIComponent(p.id)}%0A%0APlease+add+details+below:`}
                            external
                            onClick={() => trackEvent('contribute_click', { contribute_type: 'info', politician_id: p.id, page_location: 'politician_detail' })}
                            className='bg-white text-orange-600 py-2 px-4 rounded-lg hover:bg-gray-50 border-none shadow-lg'
                            size='md'>
                            Contribute Info →
                        </Button>
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    )
}
