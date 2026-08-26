/**
 * Unit tests for politician directory utility functions.
 */

import {
    PER_PAGE,
    buildPoliticiansDescription,
    buildPoliticiansPath,
    buildPoliticiansTitle,
    buildSearchResultsLine,
    getPaginationAlternates,
    parsePartyParam,
} from "@/lib/politicians/directory"

describe("buildPoliticiansTitle", () => {
    it("returns default title for no filters", () => {
        expect(buildPoliticiansTitle({}, 1)).toBe("All Indian MPs & MLAs")
    })

    it("returns MP-specific title", () => {
        expect(buildPoliticiansTitle({ type: "MP" }, 1)).toBe("Lok Sabha MPs")
    })

    it("returns MLA-specific title", () => {
        expect(buildPoliticiansTitle({ type: "MLA" }, 1)).toBe("Vidhan Sabha MLAs")
    })

    it("returns state-specific title", () => {
        expect(buildPoliticiansTitle({ state: "Gujarat" }, 1)).toBe(
            "Gujarat MPs & MLAs"
        )
    })

    it("appends page number for page > 1", () => {
        expect(buildPoliticiansTitle({}, 2)).toBe("All Indian MPs & MLAs — Page 2")
    })

    it("does NOT change title for search query (keeps canonical H1)", () => {
        // This is the key change from issue #248 — H1 stays canonical
        expect(buildPoliticiansTitle({ q: "Shah" }, 1)).toBe("All Indian MPs & MLAs")
        expect(buildPoliticiansTitle({ q: "Modi" }, 1)).not.toContain("Search:")
    })

    it("combines type/state with pagination but not search query", () => {
        expect(buildPoliticiansTitle({ type: "MP", q: "Shah" }, 2)).toBe(
            "Lok Sabha MPs — Page 2"
        )
    })
})

describe("buildSearchResultsLine", () => {
    it("returns null for undefined query", () => {
        expect(buildSearchResultsLine(undefined, 100)).toBeNull()
    })

    it("returns null for empty query", () => {
        expect(buildSearchResultsLine("", 100)).toBeNull()
    })

    it("returns null for whitespace-only query", () => {
        expect(buildSearchResultsLine("   ", 100)).toBeNull()
    })

    it("returns singular form for 1 result", () => {
        expect(buildSearchResultsLine("Shah", 1)).toBe('Showing 1 result for "Shah"')
    })

    it("returns plural form for multiple results", () => {
        expect(buildSearchResultsLine("Shah", 17)).toBe('Showing 17 results for "Shah"')
    })

    it("formats large numbers with commas", () => {
        expect(buildSearchResultsLine("Modi", 1234)).toBe(
            'Showing 1,234 results for "Modi"'
        )
    })

    it("trims whitespace from query", () => {
        expect(buildSearchResultsLine("  Shah  ", 5)).toBe(
            'Showing 5 results for "Shah"'
        )
    })

    it("handles zero results", () => {
        expect(buildSearchResultsLine("xyz", 0)).toBe('Showing 0 results for "xyz"')
    })
})

describe("parsePartyParam", () => {
    it("returns undefined for missing or empty values", () => {
        expect(parsePartyParam(undefined)).toBeUndefined()
        expect(parsePartyParam("")).toBeUndefined()
        expect(parsePartyParam("  ,  ")).toBeUndefined()
    })

    it("splits and trims comma-separated party names", () => {
        expect(parsePartyParam("BJP, INC")).toEqual(["BJP", "INC"])
    })
})

describe("buildPoliticiansPath", () => {
    it("uses type-owned paths and keeps state as a query param", () => {
        expect(buildPoliticiansPath(1, { type: "MP", stateSlug: "gujarat" })).toBe(
            "/politicians/mp?state=gujarat",
        )
        expect(buildPoliticiansPath(2, { type: "MLA" })).toBe(
            "/politicians/mla/page/2",
        )
        expect(buildPoliticiansPath(1, { stateSlug: "bihar" })).toBe(
            "/politicians/state/bihar",
        )
    })

    it("appends search and party query params", () => {
        expect(
            buildPoliticiansPath(1, { q: " Shah ", parties: ["BJP", "INC"] }),
        ).toBe("/politicians?q=Shah&party=BJP%2CINC")
    })
})

describe("buildPoliticiansDescription", () => {
    it("returns type, state, and default copy", () => {
        expect(buildPoliticiansDescription({ type: "MP" })).toContain("Lok Sabha")
        expect(buildPoliticiansDescription({ type: "MLA" })).toContain("Vidhan Sabha")
        expect(buildPoliticiansDescription({ state: "Goa" })).toContain("Goa")
        expect(buildPoliticiansDescription({})).toContain("search by name")
    })
})

describe("getPaginationAlternates", () => {
    const originalSiteUrl = process.env.NEXT_PUBLIC_SITE_URL

    beforeEach(() => {
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example"
    })

    afterEach(() => {
        process.env.NEXT_PUBLIC_SITE_URL = originalSiteUrl
    })

    it("returns prev and next absolute URLs", () => {
        expect(getPaginationAlternates(2, 4, { type: "MP" })).toEqual({
            prev: "https://rajniti.example/politicians/mp",
            next: "https://rajniti.example/politicians/mp/page/3",
        })
    })

    it("omits prev on the first page", () => {
        expect(getPaginationAlternates(1, 2, {})).toEqual({
            next: "https://rajniti.example/politicians/page/2",
        })
    })
})

describe("PER_PAGE", () => {
    it("is 48", () => {
        expect(PER_PAGE).toBe(48)
    })
})
