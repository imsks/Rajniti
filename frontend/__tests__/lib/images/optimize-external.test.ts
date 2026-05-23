import {
    isExternalImageUrl,
    isOptimizableExternalUrl,
    shouldUseUnoptimizedImage,
} from "@/lib/images/optimize-external"

describe("isExternalImageUrl", () => {
    it("returns true for http and https URLs", () => {
        expect(isExternalImageUrl("https://results.eci.gov.in/photo.jpg")).toBe(true)
        expect(isExternalImageUrl("http://example.com/a.png")).toBe(true)
    })

    it("returns false for relative paths", () => {
        expect(isExternalImageUrl("/logo/Parliament.png")).toBe(false)
    })
})

describe("isOptimizableExternalUrl", () => {
    it("allows ECI politician photo hosts", () => {
        expect(
            isOptimizableExternalUrl(
                "https://results.eci.gov.in/uploads4/candprofile/2024/PC/E24/S01/NAREN-2024-12699.jpg"
            )
        ).toBe(true)
        expect(isOptimizableExternalUrl("https://eci.gov.in/files/photo.jpg")).toBe(true)
    })

    it("rejects unknown external hosts", () => {
        expect(isOptimizableExternalUrl("https://example.com/photo.jpg")).toBe(false)
    })

    it("rejects invalid URLs", () => {
        expect(isOptimizableExternalUrl("not-a-url")).toBe(false)
    })

    it("rejects relative paths", () => {
        expect(isOptimizableExternalUrl("/default-avatar.png")).toBe(false)
    })
})

describe("shouldUseUnoptimizedImage", () => {
    it("optimizes allowlisted ECI URLs", () => {
        expect(
            shouldUseUnoptimizedImage(
                "https://results.eci.gov.in/uploads4/candprofile/photo.jpg"
            )
        ).toBe(false)
    })

    it("skips optimization for unknown external URLs", () => {
        expect(shouldUseUnoptimizedImage("https://cdn.example.com/photo.jpg")).toBe(true)
    })

    it("optimizes local paths", () => {
        expect(shouldUseUnoptimizedImage("/default-avatar.png")).toBe(false)
    })

    it("respects explicit unoptimized override", () => {
        expect(
            shouldUseUnoptimizedImage(
                "https://results.eci.gov.in/photo.jpg",
                true
            )
        ).toBe(true)
        expect(
            shouldUseUnoptimizedImage("https://cdn.example.com/photo.jpg", false)
        ).toBe(false)
    })
})
