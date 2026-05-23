/**
 * Unit tests for OG image helpers.
 */

describe("buildOgImages", () => {
    beforeEach(() => {
        jest.resetModules()
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com"
    })

    it("returns photo when provided", async () => {
        const { buildOgImages } = await import("@/lib/seo/images")
        expect(buildOgImages("https://example.com/photo.jpg", "Modi")).toEqual([
            { url: "https://example.com/photo.jpg", alt: "Modi" },
        ])
    })

    it("falls back to default OG image", async () => {
        const { buildOgImages } = await import("@/lib/seo/images")
        expect(buildOgImages(null)).toEqual([
            { url: "https://rajniti.example.com/og-default.png", alt: "Rajniti" },
        ])
    })
})
