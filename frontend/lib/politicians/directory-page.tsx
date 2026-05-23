import type { Metadata } from "next"
import Navbar from "@/components/layout/Navbar"
import JsonLd from "@/components/seo/JsonLd"
import PublicPoliticianCard from "@/components/politicians/PublicPoliticianCard"
import {
    PER_PAGE,
    PoliticiansFiltersBar,
    PoliticiansPagination,
    PoliticiansStateLinks,
    buildPoliticiansDescription,
    buildPoliticiansPath,
    buildPoliticiansTitle,
    getPaginationAlternates,
    type PoliticiansListFilters,
} from "@/components/politicians/PoliticiansDirectory"
import {
    catalogToPolitician,
    fetchPoliticianCatalog,
    fetchStates,
} from "@/lib/api/politicians-catalog-server"
import { buildItemListJsonLd, buildBreadcrumbJsonLd } from "@/lib/seo/json-ld"
import { buildPageMetadata } from "@/lib/seo/metadata"
import { getPoliticianProfileHref } from "@/lib/politicianUtils"

export const dynamic = "force-dynamic"

interface PageProps {
    page?: number
    filters?: PoliticiansListFilters
}

async function renderPoliticiansDirectory({ page = 1, filters = {} }: PageProps) {
    const catalog = await fetchPoliticianCatalog({
        page,
        perPage: PER_PAGE,
        type: filters.type,
        state: filters.state,
        q: filters.q,
    })

    const totalPages = Math.max(1, Math.ceil(catalog.total / PER_PAGE))
    const states = filters.stateSlug ? [] : await fetchStates()

    const title = buildPoliticiansTitle(filters, page)
    const path = buildPoliticiansPath(page, filters)
    const { prev, next } = getPaginationAlternates(page, totalPages, filters)

    const politicians = catalog.politicians.map(catalogToPolitician)
    const itemList = politicians.map((p) => ({
        name: p.name,
        href: getPoliticianProfileHref(p),
    }))

    const breadcrumbs = [
        { name: "Home", path: "/" },
        { name: "Politicians", path: "/politicians" },
    ]
    if (filters.type === "MP") breadcrumbs.push({ name: "MPs", path: "/politicians/mp" })
    if (filters.type === "MLA") breadcrumbs.push({ name: "MLAs", path: "/politicians/mla" })
    if (filters.state && filters.stateSlug) {
        breadcrumbs.push({
            name: filters.state,
            path: `/politicians/state/${filters.stateSlug}`,
        })
    }

    return (
        <>
            <JsonLd
                data={[
                    buildBreadcrumbJsonLd(breadcrumbs),
                    buildItemListJsonLd(itemList, title),
                ]}
            />
            <Navbar sticky />
            <main className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
                    <header className="mb-8">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            {title}
                        </h1>
                        <p className="mt-2 text-gray-600 dark:text-gray-400">
                            {buildPoliticiansDescription(filters)}
                        </p>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-500">
                            {catalog.total.toLocaleString()} politicians
                        </p>
                    </header>

                    <PoliticiansFiltersBar filters={filters} states={states} />
                    {!filters.stateSlug && !filters.type && states.length > 0 && (
                        <PoliticiansStateLinks states={states} />
                    )}

                    {politicians.length === 0 ? (
                        <p className="text-gray-600 dark:text-gray-400">No politicians found.</p>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            {politicians.map((p) => (
                                <PublicPoliticianCard key={p.id} politician={p} />
                            ))}
                        </div>
                    )}

                    <PoliticiansPagination
                        page={page}
                        totalPages={totalPages}
                        filters={filters}
                    />
                </div>
            </main>
        </>
    )
}

export function buildDirectoryMetadata(
    page: number,
    filters: PoliticiansListFilters
): Metadata {
    const title = buildPoliticiansTitle(filters, page)
    const path = buildPoliticiansPath(page, filters)
    const totalPages = 1 // placeholder; prev/next set at render time via generateMetadata fetch
    return buildPageMetadata({
        title,
        description: buildPoliticiansDescription(filters),
        path,
    })
}

export async function generateDirectoryMetadata(
    page: number,
    filters: PoliticiansListFilters
): Promise<Metadata> {
    const catalog = await fetchPoliticianCatalog({
        page,
        perPage: PER_PAGE,
        type: filters.type,
        state: filters.state,
        q: filters.q,
    })
    const totalPages = Math.max(1, Math.ceil(catalog.total / PER_PAGE))
    const title = buildPoliticiansTitle(filters, page)
    const path = buildPoliticiansPath(page, filters)
    const { prev, next } = getPaginationAlternates(page, totalPages, filters)

    return buildPageMetadata({
        title,
        description: buildPoliticiansDescription(filters),
        path,
        prev,
        next,
    })
}

export default renderPoliticiansDirectory
