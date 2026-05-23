/**
 * Unit tests for politicians catalog server client.
 */

import { createMockResponse } from "../../../jest.setup"

describe("fetchPoliticianCatalog", () => {
    beforeEach(() => {
        jest.resetModules()
        process.env.API_URL = "http://test-api:8000/api/v1"
        ;(global.fetch as jest.Mock).mockReset()
    })

    it("returns catalog data on success", async () => {
        ;(global.fetch as jest.Mock).mockResolvedValueOnce(
            createMockResponse({
                success: true,
                data: {
                    total: 100,
                    page: 1,
                    per_page: 48,
                    politicians: [
                        {
                            id: "abc",
                            slug: "test-politician",
                            name: "TEST",
                            type: "MP",
                            state: "Gujarat",
                            constituency: "Test",
                        },
                    ],
                },
            })
        )
        const { fetchPoliticianCatalog } = await import("@/lib/api/politicians-catalog-server")
        const result = await fetchPoliticianCatalog({ page: 1, perPage: 48 })
        expect(result.total).toBe(100)
        expect(result.politicians).toHaveLength(1)
        expect(String((global.fetch as jest.Mock).mock.calls[0][0])).toContain(
            "/politicians/catalog"
        )
    })

    it("returns empty catalog on API failure", async () => {
        ;(global.fetch as jest.Mock).mockResolvedValueOnce(
            createMockResponse({ success: false }, false, 500)
        )
        const { fetchPoliticianCatalog } = await import("@/lib/api/politicians-catalog-server")
        const result = await fetchPoliticianCatalog()
        expect(result.politicians).toEqual([])
    })

    it("returns empty catalog on network error", async () => {
        ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error("fetch failed"))
        const { fetchPoliticianCatalog } = await import("@/lib/api/politicians-catalog-server")
        const result = await fetchPoliticianCatalog()
        expect(result.politicians).toEqual([])
        expect(result.total).toBe(0)
    })
})

describe("fetchSitemapEntries", () => {
    beforeEach(() => {
        jest.resetModules()
        process.env.API_URL = "http://test-api:8000/api/v1"
        ;(global.fetch as jest.Mock).mockReset()
    })

    it("returns sitemap entries on success", async () => {
        ;(global.fetch as jest.Mock).mockResolvedValueOnce(
            createMockResponse({
                success: true,
                data: { entries: [{ slug: "narendra-modi", type: "MP" }] },
            })
        )
        const { fetchSitemapEntries } = await import("@/lib/api/politicians-catalog-server")
        const entries = await fetchSitemapEntries()
        expect(entries).toEqual([{ slug: "narendra-modi", type: "MP" }])
    })
})
