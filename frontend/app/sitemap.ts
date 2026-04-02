import type { MetadataRoute } from "next"
import { getStaticPoliticianParams } from "@/lib/api/politicians-server"
import { getSiteUrl } from "@/lib/seo/site"

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

    const politicianParams = await getStaticPoliticianParams()
    const politicianEntries: MetadataRoute.Sitemap = politicianParams.map(({ id }) => ({
        url: `${base}/politician/${encodeURIComponent(id)}`,
        lastModified: now,
        changeFrequency: "monthly",
        priority: 0.7,
    }))

    return [...staticEntries, ...politicianEntries]
}
