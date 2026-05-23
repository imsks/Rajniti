/**
 * Unit tests for SEO site helpers.
 */

describe("getSiteUrl", () => {
    beforeEach(() => {
        jest.resetModules()
    })

    it("uses NEXT_PUBLIC_SITE_URL when set", async () => {
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com/"
        const { getSiteUrl } = await import("@/lib/seo/site")
        expect(getSiteUrl()).toBe("https://rajniti.example.com")
    })

    it("falls back to NEXTAUTH_URL", async () => {
        delete process.env.NEXT_PUBLIC_SITE_URL
        process.env.NEXTAUTH_URL = "https://auth.example.com/"
        const { getSiteUrl } = await import("@/lib/seo/site")
        expect(getSiteUrl()).toBe("https://auth.example.com")
    })

    it("strips trailing slash", async () => {
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com///"
        const { getSiteUrl } = await import("@/lib/seo/site")
        expect(getSiteUrl()).toBe("https://rajniti.example.com//")
    })
})

describe("buildDefaultOg", () => {
    beforeEach(() => {
        jest.resetModules()
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com"
    })

    it("includes default OG image", async () => {
        const { buildDefaultOg } = await import("@/lib/seo/site")
        const og = buildDefaultOg()
        expect(og?.images).toEqual([
            { url: "https://rajniti.example.com/og-default.png", alt: "Rajniti" },
        ])
    })
})
