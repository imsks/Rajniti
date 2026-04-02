import { Suspense } from "react"
import { notFound } from "next/navigation"
import type { Metadata } from "next"
import PoliticianPageClient from "./PoliticianPageClient"
import {
    fetchPoliticianBySegment,
    getStaticPoliticianParams,
} from "@/lib/api/politicians-server"
import { getSiteUrl, SITE_NAME } from "@/lib/seo/site"
import { getParty } from "@/lib/politicianUtils"
import type { Politician } from "@/types/politician"

/** Pre-render all profile URLs at build time; data is fixed until the next deploy. */
export const dynamic = "force-static"
export const dynamicParams = true

export async function generateStaticParams() {
    return getStaticPoliticianParams()
}

function buildPoliticianDescription(p: Politician): string {
    const party = getParty(p)
    return `${p.name} (${p.type}) — ${p.constituency}, ${p.state}. Party: ${party}. Profile on ${SITE_NAME}: political history, education, performance, and more.`
}

function PoliticianJsonLd({
    politician: p,
    canonicalPath,
}: {
    politician: Politician
    canonicalPath: string
}) {
    const base = getSiteUrl()
    const url = `${base}${canonicalPath}`
    const party = getParty(p)
    const record: Record<string, unknown> = {
        "@context": "https://schema.org",
        "@type": "Person",
        name: p.name,
        url,
        jobTitle: p.type === "MP" ? "Member of Parliament" : "Member of Legislative Assembly",
        homeLocation: {
            "@type": "Place",
            name: `${p.constituency}, ${p.state}, India`,
        },
    }
    if (p.photo) record.image = p.photo
    if (party && party !== "—") {
        record.memberOf = { "@type": "Organization", name: party }
    }
    return (
        <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(record) }}
        />
    )
}

export async function generateMetadata({
    params,
}: {
    params: Promise<{ id: string }>
}): Promise<Metadata> {
    const { id } = await params
    const politician = await fetchPoliticianBySegment(id)
    if (!politician) {
        return { title: "Politician not found", robots: { index: false, follow: false } }
    }

    const title = `${politician.name} — ${politician.type} · ${politician.constituency}`
    const description = buildPoliticianDescription(politician)
    const path = `/politician/${encodeURIComponent(id)}`
    const canonical = `${getSiteUrl()}${path}`

    return {
        title,
        description,
        alternates: { canonical },
        openGraph: {
            title,
            description,
            url: canonical,
            type: "profile",
            siteName: SITE_NAME,
            locale: "en_IN",
            ...(politician.photo
                ? {
                      images: [
                          {
                              url: politician.photo,
                              alt: politician.name,
                          },
                      ],
                  }
                : {}),
        },
        twitter: {
            card: "summary_large_image",
            title,
            description,
            ...(politician.photo ? { images: [politician.photo] } : {}),
        },
        robots: { index: true, follow: true },
    }
}

export default async function PoliticianPage({
    params,
}: {
    params: Promise<{ id: string }>
}) {
    const { id } = await params
    const politician = await fetchPoliticianBySegment(id)
    if (!politician) notFound()

    const path = `/politician/${encodeURIComponent(id)}`

    return (
        <>
            <PoliticianJsonLd politician={politician} canonicalPath={path} />
            <Suspense
                fallback={
                    <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 flex items-center justify-center">
                        <div className="text-center">
                            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent" />
                            <p className="mt-4 text-gray-600 dark:text-gray-400 font-semibold">
                                Loading…
                            </p>
                        </div>
                    </div>
                }
            >
                <PoliticianPageClient politician={politician} routeSegment={id} />
            </Suspense>
        </>
    )
}
