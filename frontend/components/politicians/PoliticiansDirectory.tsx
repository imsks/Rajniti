import Link from "next/link"
import { getSiteUrl } from "@/lib/seo/site"
import { slugifySegment } from "@/lib/seo/slugify"

export const PER_PAGE = 48

export interface PoliticiansListFilters {
    type?: "MP" | "MLA"
    state?: string
    stateSlug?: string
    q?: string
}

export function buildPoliticiansPath(
    page: number,
    filters: PoliticiansListFilters = {}
): string {
    const { type, stateSlug, q } = filters

    let base = "/politicians"
    if (type === "MP") base = "/politicians/mp"
    else if (type === "MLA") base = "/politicians/mla"
    else if (stateSlug) base = `/politicians/state/${encodeURIComponent(stateSlug)}`

    if (page > 1) base = `${base}/page/${page}`

    const params = new URLSearchParams()
    if (q?.trim()) params.set("q", q.trim())
    const qs = params.toString()
    return qs ? `${base}?${qs}` : base
}

export function buildPoliticiansTitle(
    filters: PoliticiansListFilters,
    page: number
): string {
    let title = "All Indian MPs & MLAs"
    if (filters.type === "MP") title = "Lok Sabha MPs"
    else if (filters.type === "MLA") title = "Vidhan Sabha MLAs"
    else if (filters.state) title = `${filters.state} MPs & MLAs`
    if (filters.q?.trim()) title = `Search: ${filters.q.trim()}`
    if (page > 1) title = `${title} — Page ${page}`
    return title
}

export function buildPoliticiansDescription(filters: PoliticiansListFilters): string {
    if (filters.type === "MP") {
        return "Browse all Lok Sabha Members of Parliament in India — constituency, state, and party on Rajniti."
    }
    if (filters.type === "MLA") {
        return "Browse all Vidhan Sabha Members of Legislative Assembly in India — constituency, state, and party on Rajniti."
    }
    if (filters.state) {
        return `Browse MPs and MLAs from ${filters.state} — profiles, party affiliation, and constituency details on Rajniti.`
    }
    return "Browse all Indian MPs and MLAs — search by name, filter by state or type. Open data on Rajniti."
}

interface PoliticiansPaginationProps {
    page: number
    totalPages: number
    filters: PoliticiansListFilters
}

export function PoliticiansPagination({
    page,
    totalPages,
    filters,
}: PoliticiansPaginationProps) {
    if (totalPages <= 1) return null

    const prevPath = page > 1 ? buildPoliticiansPath(page - 1, filters) : null
    const nextPath = page < totalPages ? buildPoliticiansPath(page + 1, filters) : null

    return (
        <nav
            className="flex items-center justify-between mt-8 pt-6 border-t border-orange-100 dark:border-gray-700"
            aria-label="Pagination"
        >
            {prevPath ? (
                <Link
                    href={prevPath}
                    className="px-4 py-2 rounded-lg border border-orange-200 dark:border-gray-600 text-orange-700 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-gray-800 transition"
                >
                    Previous
                </Link>
            ) : (
                <span />
            )}
            <span className="text-sm text-gray-600 dark:text-gray-400">
                Page {page} of {totalPages}
            </span>
            {nextPath ? (
                <Link
                    href={nextPath}
                    className="px-4 py-2 rounded-lg border border-orange-200 dark:border-gray-600 text-orange-700 dark:text-orange-400 hover:bg-orange-50 dark:hover:bg-gray-800 transition"
                >
                    Next
                </Link>
            ) : (
                <span />
            )}
        </nav>
    )
}

interface PoliticiansFiltersBarProps {
    filters: PoliticiansListFilters
    states: string[]
}

export function PoliticiansFiltersBar({ filters }: PoliticiansFiltersBarProps) {
    const q = filters.q ?? ""

    return (
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <form action="/politicians" method="get" className="flex-1 flex gap-2">
                <input
                    type="search"
                    name="q"
                    defaultValue={q}
                    placeholder="Search by name…"
                    className="flex-1 px-4 py-2 rounded-lg border border-orange-200 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                    aria-label="Search politicians by name"
                />
                <button
                    type="submit"
                    className="px-6 py-2 rounded-lg font-medium cursor-pointer bg-orange-600 text-white hover:bg-orange-700 transition"
                >
                    Search
                </button>
            </form>
            <div className="flex flex-wrap gap-2">
                <Link
                    href="/politicians"
                    className={`px-5 py-4 rounded-full ${
                        !filters.type && !filters.stateSlug
                            ? "border dark:border-orange-600 font-bold text-orange-600"
                            : "text-orange-600 border border-orange-600 dark:bg-gray-800 dark:text-orange-600"
                    }`}
                >
                    All
                </Link>
                <Link
                    href="/politicians/mp"
                    className={`p-4 rounded-full ${
                        filters.type === "MP"
                            ? "bg-orange-500 font-bold text-white"
                            : "bg-orange-100 text-orange-800 dark:bg-gray-800 dark:text-orange-300"
                    }`}
                >
                    MPs
                </Link>
                <Link
                    href="/politicians/mla"
                    className={`px-3 py-4 rounded-full ${
                        filters.type === "MLA"
                            ? "bg-green-600 font-bold text-white"
                            : "bg-green-100 text-green-800 dark:bg-gray-800 dark:text-green-300"
                    }`}
                >
                    MLAs
                </Link>
            </div>
        </div>
    )
}

export function PoliticiansStateLinks({ states }: { states: string[] }) {
    const topStates = states.slice(0, 12)
    return (
        <div className="mb-8">
            <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Browse by state
            </h2>
            <div className="flex flex-wrap gap-2">
                {topStates.map((state) => (
                    <Link
                        key={state}
                        href={`/politicians/state/${slugifySegment(state)}`}
                        className="px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 hover:bg-orange-100 dark:hover:bg-orange-900/30 transition"
                    >
                        {state}
                    </Link>
                ))}
            </div>
        </div>
    )
}

export function getPaginationAlternates(
    page: number,
    totalPages: number,
    filters: PoliticiansListFilters
): { prev?: string; next?: string } {
    const base = getSiteUrl()
    const result: { prev?: string; next?: string } = {}
    if (page > 1) result.prev = `${base}${buildPoliticiansPath(page - 1, filters)}`
    if (page < totalPages) result.next = `${base}${buildPoliticiansPath(page + 1, filters)}`
    return result
}
