/**
 * Unit tests for PoliticiansDirectory utility functions.
 */

import {
    buildPoliticiansTitle,
    buildSearchResultsLine,
} from "@/components/politicians/PoliticiansDirectory"

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
