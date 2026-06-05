import type { Metadata } from "next"
import { getParty, toTitleCase } from "@/lib/politicianUtils"
import { buildDefaultOg, buildDefaultTwitter, getSiteUrl, SITE_NAME } from "@/lib/seo/site"
import { buildOgImages, buildPoliticianOgImages, buildPoliticianTwitterImages, buildTwitterImages } from "@/lib/seo/images"
import { getPreferredPoliticianPath } from "@/lib/seo/politician-canonical"
import type { Politician } from "@/types/politician"

export function buildPoliticianDescription(p: Politician): string {
    const party = getParty(p)
    return `${toTitleCase(p.name)} (${p.type}) — ${p.constituency}, ${p.state}. Party: ${party}. Profile on ${SITE_NAME}: political history, education, performance, and more.`
}

export function buildPoliticianMetadata(politician: Politician): Metadata {
    const title = `${toTitleCase(politician.name)} — ${politician.type} · ${politician.constituency}`
    const description = buildPoliticianDescription(politician)
    const path = getPreferredPoliticianPath(politician)
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
            images: buildPoliticianOgImages(politician),
        },
        twitter: {
            card: "summary_large_image",
            title,
            description,
            images: buildPoliticianTwitterImages(politician),
        },
        robots: { index: true, follow: true },
    }
}

export interface PageMetadataOptions {
    title: string
    description: string
    path: string
    prev?: string
    next?: string
}

export function buildPageMetadata({
    title,
    description,
    path,
    prev,
    next,
}: PageMetadataOptions): Metadata {
    const canonical = `${getSiteUrl()}${path}`
    const ogTitle = `${title} | ${SITE_NAME}`

    const alternates: Metadata["alternates"] = { canonical }
    if (prev || next) {
        alternates.types = {}
        if (prev) alternates.types["application/rss+xml"] = prev
    }

    const metadata: Metadata = {
        title,
        description,
        alternates,
        openGraph: {
            ...buildDefaultOg(),
            title: ogTitle,
            description,
            url: canonical,
            images: buildOgImages(),
        },
        twitter: {
            ...buildDefaultTwitter(),
            title: ogTitle,
            description,
            images: buildTwitterImages(),
        },
        robots: { index: true, follow: true },
    }

    if (prev || next) {
        metadata.other = {}
        if (prev) metadata.other["link:prev"] = prev
        if (next) metadata.other["link:next"] = next
    }

    return metadata
}
