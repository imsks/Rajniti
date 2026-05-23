import type { MetadataRoute } from "next"
import { getSiteUrl } from "@/lib/seo/site"

export const POLITICIAN_SITEMAP_CHUNK_SIZE = 1000

export interface SitemapPoliticianEntry {
    slug: string
    type?: string
}

export function buildStaticSitemapEntries(): MetadataRoute.Sitemap {
    const base = getSiteUrl()
    const now = new Date()
    const staticPaths: {
        path: string
        priority: number
        changeFrequency: MetadataRoute.Sitemap[0]["changeFrequency"]
    }[] = [
        { path: "", priority: 1, changeFrequency: "weekly" },
        { path: "/contributors", priority: 0.8, changeFrequency: "monthly" },
        { path: "/politicians", priority: 0.9, changeFrequency: "weekly" },
        { path: "/politicians/mp", priority: 0.85, changeFrequency: "weekly" },
        { path: "/politicians/mla", priority: 0.85, changeFrequency: "weekly" },
    ]

    return staticPaths.map(({ path, priority, changeFrequency }) => ({
        url: `${base}${path}`,
        lastModified: now,
        changeFrequency,
        priority,
    }))
}

export function buildPoliticianSitemapChunk(
    entries: SitemapPoliticianEntry[],
    chunkIndex: number
): MetadataRoute.Sitemap {
    const base = getSiteUrl()
    const now = new Date()
    const start = chunkIndex * POLITICIAN_SITEMAP_CHUNK_SIZE
    const slice = entries.slice(start, start + POLITICIAN_SITEMAP_CHUNK_SIZE)

    return slice.map(({ slug }) => ({
        url: `${base}/politician/${encodeURIComponent(slug)}`,
        lastModified: now,
        changeFrequency: "monthly" as const,
        priority: 0.7,
    }))
}

export function computePoliticianSitemapChunkCount(totalEntries: number): number {
    if (totalEntries <= 0) return 0
    return Math.ceil(totalEntries / POLITICIAN_SITEMAP_CHUNK_SIZE)
}

export function generatePoliticianSitemapIds(totalEntries: number): { id: number }[] {
    const chunkCount = computePoliticianSitemapChunkCount(totalEntries)
    return Array.from({ length: chunkCount }, (_, id) => ({ id }))
}
