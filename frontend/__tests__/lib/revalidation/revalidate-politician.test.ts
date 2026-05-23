jest.mock("next/cache", () => ({
    revalidateTag: jest.fn(),
    revalidatePath: jest.fn(),
}))

import { revalidatePath, revalidateTag } from "next/cache"
import {
    isAuthorizedRevalidationRequest,
    parseRevalidatePoliticianSegment,
    revalidatePoliticianProfile,
} from "@/lib/revalidation/revalidate-politician"

const mockRevalidateTag = revalidateTag as jest.Mock
const mockRevalidatePath = revalidatePath as jest.Mock

describe("parseRevalidatePoliticianSegment", () => {
    it("accepts segment, slug, or id", () => {
        expect(parseRevalidatePoliticianSegment({ slug: "narendra-modi" })).toBe(
            "narendra-modi"
        )
        expect(parseRevalidatePoliticianSegment({ segment: "abc" })).toBe("abc")
        expect(parseRevalidatePoliticianSegment({ id: "uuid" })).toBe("uuid")
    })

    it("returns null when missing", () => {
        expect(parseRevalidatePoliticianSegment({})).toBeNull()
    })
})

describe("isAuthorizedRevalidationRequest", () => {
    it("requires matching secret", () => {
        expect(isAuthorizedRevalidationRequest("secret", "secret")).toBe(true)
        expect(isAuthorizedRevalidationRequest("secret", "wrong")).toBe(false)
        expect(isAuthorizedRevalidationRequest(undefined, "secret")).toBe(false)
    })
})

describe("revalidatePoliticianProfile", () => {
    beforeEach(() => {
        jest.clearAllMocks()
    })

    it("revalidates tag and path", () => {
        const result = revalidatePoliticianProfile("narendra-modi")
        expect(result).toEqual({
            tag: "politician-narendra-modi",
            path: "/politician/narendra-modi",
        })
        expect(mockRevalidateTag).toHaveBeenCalledWith("politician-narendra-modi", "max")
        expect(mockRevalidatePath).toHaveBeenCalledWith("/politician/narendra-modi")
    })
})
