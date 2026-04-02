import type { MetadataRoute } from "next"
import { getPoliticianIdsForSitemap } from "@/lib/api/politicians-server"
import { getSiteUrl } from "@/lib/seo/site"

/** Regenerate sitemap periodically instead of at build time (large API payload). */
export const revalidate = 3600

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const base = getSiteUrl()
    const now = new Date()

    const staticPaths: { path: string; priority: number; changeFrequency: MetadataRoute.Sitemap[0]["changeFrequency"] }[] =
        [
            { path: "", priority: 1, changeFrequency: "weekly" },
            { path: "/contributors", priority: 0.8, changeFrequency: "monthly" },
            { path: "/dashboard", priority: 0.9, changeFrequency: "weekly" },
        ]

    const staticEntries: MetadataRoute.Sitemap = staticPaths.map(
        ({ path, priority, changeFrequency }) => ({
            url: `${base}${path}`,
            lastModified: now,
            changeFrequency,
            priority,
        })
    )

    const politicianParams = await getPoliticianIdsForSitemap()
    const politicianEntries: MetadataRoute.Sitemap = politicianParams.map(({ id }) => ({
        url: `${base}/politician/${encodeURIComponent(id)}`,
        lastModified: now,
        changeFrequency: "monthly",
        priority: 0.7,
    }))

    return [...staticEntries, ...politicianEntries]
}
