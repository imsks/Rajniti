/**
 * Unit tests for politician canonical helpers.
 */

import type { Politician } from "@/types/politician"

const politician: Politician = {
    id: "ef8a4654-1d09-4a06-bae7-14377bc08387",
    name: "NARENDRA MODI",
    slug: "narendra-modi",
    state: "Gujarat",
    constituency: "Varanasi",
    type: "MP",
    political_background: { elections: [] },
}

describe("politician-canonical", () => {
    it("isFullUuid detects UUID segments", async () => {
        const { isFullUuid } = await import("@/lib/seo/politician-canonical")
        expect(isFullUuid("ef8a4654-1d09-4a06-bae7-14377bc08387")).toBe(true)
        expect(isFullUuid("narendra-modi")).toBe(false)
    })

    it("getPreferredPoliticianPath prefers slug", async () => {
        const { getPreferredPoliticianPath } = await import("@/lib/seo/politician-canonical")
        expect(getPreferredPoliticianPath(politician)).toBe("/politician/narendra-modi")
    })

    it("shouldRedirectToCanonical for UUID segment", async () => {
        const { shouldRedirectToCanonical } = await import("@/lib/seo/politician-canonical")
        expect(
            shouldRedirectToCanonical("ef8a4654-1d09-4a06-bae7-14377bc08387", politician)
        ).toBe(true)
        expect(shouldRedirectToCanonical("narendra-modi", politician)).toBe(false)
    })
})

describe("slugify", () => {
    it("slugifySegment normalizes state names", async () => {
        const { slugifySegment, resolveStateFromSlug } = await import("@/lib/seo/slugify")
        expect(slugifySegment("Maharashtra")).toBe("maharashtra")
        expect(resolveStateFromSlug("maharashtra", ["Maharashtra", "Gujarat"])).toBe("Maharashtra")
    })
})
