/**
 * Unit tests for sitemap builders.
 */

describe("sitemap-builders", () => {
    beforeEach(() => {
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com"
    })

    it("computePoliticianSitemapChunkCount rounds up", async () => {
        const { computePoliticianSitemapChunkCount } = await import("@/lib/seo/sitemap-builders")
        expect(computePoliticianSitemapChunkCount(0)).toBe(0)
        expect(computePoliticianSitemapChunkCount(1)).toBe(1)
        expect(computePoliticianSitemapChunkCount(1000)).toBe(1)
        expect(computePoliticianSitemapChunkCount(1001)).toBe(2)
    })

    it("buildStaticSitemapEntries excludes dashboard", async () => {
        const { buildStaticSitemapEntries } = await import("@/lib/seo/sitemap-builders")
        const entries = buildStaticSitemapEntries()
        const urls = entries.map((e) => e.url)
        expect(urls).toContain("https://rajniti.example.com/politicians")
        expect(urls).not.toContain("https://rajniti.example.com/dashboard")
    })

    it("buildPoliticianSitemapChunk uses slug URLs", async () => {
        const { buildPoliticianSitemapChunk } = await import("@/lib/seo/sitemap-builders")
        const entries = buildPoliticianSitemapChunk(
            [{ slug: "narendra-modi", type: "MP" }],
            0
        )
        expect(entries[0].url).toBe("https://rajniti.example.com/politician/narendra-modi")
    })
})
