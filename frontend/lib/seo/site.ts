import type { Metadata } from "next"
import { buildOgImages, buildTwitterImages } from "@/lib/seo/images"

/** Prefix a bare host (e.g. Vercel's VERCEL_URL) with https:// if no scheme is present. */
function withScheme(url: string): string {
    return /^https?:\/\//.test(url) ? url : `https://${url}`
}

/**
 * Canonical site origin for Open Graph, canonical URLs, and sitemap.
 * Falls back through NEXT_PUBLIC_SITE_URL → NEXTAUTH_URL → VERCEL_URL → localhost,
 * so preview/production deploys resolve a canonical origin even when the explicit
 * URL vars are not set on Vercel.
 */
export function getSiteUrl(): string {
    const raw =
        process.env.NEXT_PUBLIC_SITE_URL ||
        process.env.NEXTAUTH_URL ||
        (process.env.VERCEL_URL ? withScheme(process.env.VERCEL_URL) : "") ||
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
        images: buildOgImages(),
    }
}

export function buildDefaultTwitter(): Metadata["twitter"] {
    return {
        card: "summary_large_image",
        images: buildTwitterImages(),
    }
}
