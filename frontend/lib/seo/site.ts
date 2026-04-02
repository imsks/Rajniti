import type { Metadata } from "next"

/** Canonical site origin for Open Graph, canonical URLs, and sitemap. */
export function getSiteUrl(): string {
    const raw =
        process.env.NEXT_PUBLIC_SITE_URL ||
        process.env.NEXTAUTH_URL ||
        "http://localhost:3000"
    return raw.replace(/\/$/, "")
}

export const SITE_NAME = "Rajniti"

export const defaultDescription =
    "Explore Indian MPs and MLAs — political history, education, family background, criminal records, and Lok Sabha performance. Open data, community-driven."

/** Shared Open Graph / Twitter defaults; pages override title and description. */
export function buildDefaultOg(): Metadata["openGraph"] {
    const url = getSiteUrl()
    return {
        type: "website",
        locale: "en_IN",
        siteName: SITE_NAME,
        url,
    }
}

export function buildDefaultTwitter(): Metadata["twitter"] {
    return {
        card: "summary_large_image",
    }
}
