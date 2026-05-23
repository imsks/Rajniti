/**
 * Unit tests for JSON-LD builders.
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

describe("json-ld builders", () => {
    beforeEach(() => {
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com"
    })

    it("buildWebSiteJsonLd includes SearchAction", async () => {
        const { buildWebSiteJsonLd } = await import("@/lib/seo/json-ld")
        const data = buildWebSiteJsonLd()
        expect(data["@type"]).toBe("WebSite")
        expect(data.potentialAction).toMatchObject({
            "@type": "SearchAction",
        })
    })

    it("buildPersonJsonLd uses canonical path", async () => {
        const { buildPersonJsonLd } = await import("@/lib/seo/json-ld")
        const data = buildPersonJsonLd(politician, "/politician/narendra-modi")
        expect(data.url).toBe("https://rajniti.example.com/politician/narendra-modi")
        expect(data.name).toBe("NARENDRA MODI")
    })

    it("buildItemListJsonLd lists items with positions", async () => {
        const { buildItemListJsonLd } = await import("@/lib/seo/json-ld")
        const data = buildItemListJsonLd(
            [{ name: "Modi", href: "/politician/narendra-modi" }],
            "MPs"
        )
        expect(data.numberOfItems).toBe(1)
        expect(data.itemListElement).toHaveLength(1)
    })

    it("buildBreadcrumbJsonLd builds ordered breadcrumbs", async () => {
        const { buildBreadcrumbJsonLd } = await import("@/lib/seo/json-ld")
        const data = buildBreadcrumbJsonLd([
            { name: "Home", path: "/" },
            { name: "Politicians", path: "/politicians" },
        ])
        expect(data.itemListElement).toHaveLength(2)
    })
})
