/**
 * Unit tests for OG image helpers.
 */

import type { Politician } from "@/types/politician"

const politician: Politician = {
    id: "ef8a4654-1d09-4a06-bae7-14377bc08387",
    name: "NARENDRA MODI",
    slug: "narendra-modi",
    state: "Uttar Pradesh",
    constituency: "Varanasi",
    type: "MP",
    political_background: { elections: [] },
}

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

describe("buildPoliticianOgImages", () => {
    beforeEach(() => {
        jest.resetModules()
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com"
    })

    it("uses generated opengraph-image route instead of raw photo URL", async () => {
        const { buildPoliticianOgImages, buildPoliticianTwitterImages } =
            await import("@/lib/seo/images")
        expect(buildPoliticianOgImages(politician)).toEqual([
            {
                url: "https://rajniti.example.com/politician/narendra-modi/opengraph-image",
                alt: "NARENDRA MODI",
            },
        ])
        expect(buildPoliticianTwitterImages(politician)).toEqual([
            "https://rajniti.example.com/politician/narendra-modi/opengraph-image",
        ])
    })
})
