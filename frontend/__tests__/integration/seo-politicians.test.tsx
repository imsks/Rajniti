/**
 * Integration tests for SEO directory rendering (SSR data mocked).
 */

import { render, screen } from "@testing-library/react"
import renderPoliticiansDirectory from "@/lib/politicians/directory-page"
import { fetchPoliticianCatalog } from "@/lib/api/politicians-catalog-server"

jest.mock("@/lib/api/politicians-catalog-server", () => ({
    fetchPoliticianCatalog: jest.fn().mockResolvedValue({
        total: 1,
        page: 1,
        per_page: 48,
        politicians: [
            {
                id: "abc-123",
                slug: "narendra-modi",
                name: "NARENDRA MODI",
                type: "MP",
                state: "Uttar Pradesh",
                constituency: "Varanasi",
                photo: null,
            },
        ],
    }),
    fetchStates: jest.fn().mockResolvedValue(["Uttar Pradesh", "Gujarat"]),
    fetchParties: jest
        .fn()
        .mockResolvedValue(["Bharatiya Janata Party", "Indian National Congress"]),
    catalogToPolitician: jest.requireActual("@/lib/api/politicians-catalog-server")
        .catalogToPolitician,
}))

jest.mock("@/components/layout/Navbar", () => ({
    __esModule: true,
    default: () => <nav data-testid="navbar">Navbar</nav>,
}))

const mockedFetchCatalog = fetchPoliticianCatalog as jest.MockedFunction<typeof fetchPoliticianCatalog>

describe("SEO politicians directory", () => {
    beforeEach(() => {
        process.env.NEXT_PUBLIC_SITE_URL = "https://rajniti.example.com"
        mockedFetchCatalog.mockResolvedValue({
            total: 1,
            page: 1,
            per_page: 48,
            politicians: [
                {
                    id: "abc-123",
                    slug: "narendra-modi",
                    name: "NARENDRA MODI",
                    type: "MP",
                    state: "Uttar Pradesh",
                    constituency: "Varanasi",
                    photo: null,
                },
            ],
        })
    })

    it("renders politician names as crawlable links", async () => {
        const ui = await renderPoliticiansDirectory({ page: 1, filters: {} })
        render(ui)
        expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
            /All Indian MPs & MLAs/i
        )
        expect(screen.getByRole("link", { name: /NARENDRA MODI/i })).toHaveAttribute(
            "href",
            "/politician/narendra-modi"
        )
    })

    it("includes ItemList JSON-LD script", async () => {
        const ui = await renderPoliticiansDirectory({ page: 1, filters: {} })
        const { container } = render(ui)
        const scripts = container.querySelectorAll('script[type="application/ld+json"]')
        const combined = Array.from(scripts)
            .map((s) => s.textContent ?? "")
            .join(" ")
        expect(combined).toContain("ItemList")
        expect(combined).toContain("BreadcrumbList")
    })

    it("keeps canonical H1 and shows results line on search", async () => {
        mockedFetchCatalog.mockResolvedValueOnce({
            total: 17,
            page: 1,
            per_page: 48,
            politicians: [
                {
                    id: "abc-123",
                    slug: "amit-shah",
                    name: "AMIT SHAH",
                    type: "MP",
                    state: "Gujarat",
                    constituency: "Gandhinagar",
                    photo: null,
                },
            ],
        })

        const ui = await renderPoliticiansDirectory({ page: 1, filters: { q: "Shah" } })
        render(ui)

        // H1 should stay canonical - NOT "Search: Shah"
        expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
            /All Indian MPs & MLAs/i
        )
        expect(screen.getByRole("heading", { level: 1 })).not.toHaveTextContent(
            /Search:/i
        )

        // "Showing results for" line should appear
        expect(screen.getByText(/Showing 17 results for "Shah"/i)).toBeInTheDocument()
    })

    it("does not show results line when no search query", async () => {
        const ui = await renderPoliticiansDirectory({ page: 1, filters: {} })
        render(ui)

        expect(screen.queryByText(/Showing .* results for/i)).not.toBeInTheDocument()
    })
})
