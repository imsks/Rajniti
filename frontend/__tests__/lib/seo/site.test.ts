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

    it("falls back to VERCEL_URL and adds https:// to a bare host", async () => {
        delete process.env.NEXT_PUBLIC_SITE_URL
        delete process.env.NEXTAUTH_URL
        process.env.VERCEL_URL = "rajniti-app.vercel.app"
        const { getSiteUrl } = await import("@/lib/seo/site")
        expect(getSiteUrl()).toBe("https://rajniti-app.vercel.app")
        delete process.env.VERCEL_URL
    })

    it("defaults to localhost:3000 when nothing is set", async () => {
        delete process.env.NEXT_PUBLIC_SITE_URL
        delete process.env.NEXTAUTH_URL
        delete process.env.VERCEL_URL
        const { getSiteUrl } = await import("@/lib/seo/site")
        expect(getSiteUrl()).toBe("http://localhost:3000")
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
