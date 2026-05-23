import { getSiteUrl } from "@/lib/seo/site"
import { getPreferredPoliticianPath } from "@/lib/seo/politician-canonical"
import type { Politician } from "@/types/politician"

export const DEFAULT_OG_IMAGE_PATH = "/og-default.png"

export function getDefaultOgImageUrl(): string {
    return `${getSiteUrl()}${DEFAULT_OG_IMAGE_PATH}`
}

export function buildOgImages(photo?: string | null, alt = "Rajniti") {
    if (photo?.trim()) {
        return [{ url: photo, alt }]
    }
    return [{ url: getDefaultOgImageUrl(), alt }]
}

export function buildTwitterImages(photo?: string | null): string[] {
    if (photo?.trim()) return [photo]
    return [getDefaultOgImageUrl()]
}

/** OG image URL for a politician profile (generated opengraph-image route). */
export function buildPoliticianOgImageUrl(politician: Politician): string {
    const path = getPreferredPoliticianPath(politician)
    return `${getSiteUrl()}${path}/opengraph-image`
}

export function buildPoliticianOgImages(politician: Politician) {
    return [{ url: buildPoliticianOgImageUrl(politician), alt: politician.name }]
}

export function buildPoliticianTwitterImages(politician: Politician): string[] {
    return [buildPoliticianOgImageUrl(politician)]
}
