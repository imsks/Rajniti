import {
    POLITICIAN_REVALIDATE_SECONDS,
    politicianProfilePath,
    politicianRevalidationTag,
} from "@/lib/revalidation/politician"

describe("politicianRevalidationTag", () => {
    it("normalizes segment to lowercase tag", () => {
        expect(politicianRevalidationTag("Narendra-Modi")).toBe("politician-narendra-modi")
    })

    it("trims whitespace", () => {
        expect(politicianRevalidationTag("  narendra-modi  ")).toBe("politician-narendra-modi")
    })
})

describe("politicianProfilePath", () => {
    it("builds encoded profile path", () => {
        expect(politicianProfilePath("narendra-modi")).toBe("/politician/narendra-modi")
    })
})

describe("POLITICIAN_REVALIDATE_SECONDS", () => {
    it("defaults to 3600", () => {
        expect(POLITICIAN_REVALIDATE_SECONDS).toBe(3600)
    })
})
