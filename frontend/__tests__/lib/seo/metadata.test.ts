/**
 * Unit tests for SEO metadata builders.
 */

import type { Politician } from "@/types/politician"

const politician: Politician = {
    id: "ef8a4654-1d09-4a06-bae7-14377bc08387",
    name: "NARENDRA MODI",
    slug: "narendra-modi",
    state: "Gujarat",
    constituency: "Varanasi",
    type: "MP",
    political_background: {
        elections: [{ year: 2024, type: "LS", state: "UP", constituency: "Varanasi", party: "BJP", status: "WON" }],
    },
}

describe("buildPoliticianMetadata", () => {
    beforeEach(() => {
        jest.resetModules()
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com"
    })

    it("uses preferred slug in canonical URL", async () => {
        const { buildPoliticianMetadata } = await import("@/lib/seo/metadata")
        const meta = buildPoliticianMetadata(politician)
        expect(meta.alternates?.canonical).toBe(
            "https://rajniti.example.com/politician/narendra-modi"
        )
    })

    it("includes title with name and constituency", async () => {
        const { buildPoliticianMetadata } = await import("@/lib/seo/metadata")
        const meta = buildPoliticianMetadata(politician)
        expect(meta.title).toContain("NARENDRA MODI")
        expect(meta.title).toContain("Varanasi")
    })
})

describe("buildPageMetadata", () => {
    beforeEach(() => {
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com"
    })

    it("builds canonical for directory pages", async () => {
        const { buildPageMetadata } = await import("@/lib/seo/metadata")
        const meta = buildPageMetadata({
            title: "All Indian MPs & MLAs",
            description: "Browse politicians",
            path: "/politicians",
        })
        expect(meta.alternates?.canonical).toBe("https://rajniti.example.com/politicians")
    })
})
