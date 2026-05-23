import type { MetadataRoute } from "next"
import { fetchSitemapEntries } from "@/lib/api/politicians-catalog-server"
import {
    buildPoliticianSitemapChunk,
    buildStaticSitemapEntries,
    generatePoliticianSitemapIds,
} from "@/lib/seo/sitemap-builders"

/** Regenerate sitemap periodically instead of at build time (large API payload). */
export const revalidate = 3600

export async function generateSitemaps() {
    const entries = await fetchSitemapEntries()
    return [{ id: 0 }, ...generatePoliticianSitemapIds(entries.length)]
}

export default async function sitemap({
    id,
}: {
    id: number
}): Promise<MetadataRoute.Sitemap> {
    if (id === 0) {
        return buildStaticSitemapEntries()
    }

    const entries = await fetchSitemapEntries()
    return buildPoliticianSitemapChunk(entries, id - 1)
}
