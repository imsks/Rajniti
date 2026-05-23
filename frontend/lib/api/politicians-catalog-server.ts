import type { ElectionType, Politician } from "@/types/politician"
import { getApiBaseUrl } from "@/lib/api/api-base"

export interface CatalogPolitician {
    id: string
    slug?: string | null
    name: string
    type: ElectionType
    state: string
    constituency: string
    photo?: string | null
}

export interface CatalogResponse {
    total: number
    page: number
    per_page: number
    politicians: CatalogPolitician[]
}

export interface SitemapEntry {
    slug: string
    type: string
}

export interface CatalogParams {
    page?: number
    perPage?: number
    type?: ElectionType
    state?: string
    q?: string
}

async function safeJson<T>(res: Response): Promise<T | null> {
    try {
        return (await res.json()) as T
    } catch {
        return null
    }
}

export async function fetchPoliticianCatalog(
    params: CatalogParams = {}
): Promise<CatalogResponse> {
    const search = new URLSearchParams()
    if (params.page) search.set("page", String(params.page))
    if (params.perPage) search.set("per_page", String(params.perPage))
    if (params.type) search.set("type", params.type)
    if (params.state) search.set("state", params.state)
    if (params.q) search.set("q", params.q)

    const qs = search.toString()
    const url = `${getApiBaseUrl({ forServer: true })}/politicians/catalog${qs ? `?${qs}` : ""}`

    const res = await fetch(url, { cache: "no-store" })
    if (!res.ok) {
        return { total: 0, page: 1, per_page: 48, politicians: [] }
    }

    const json = await safeJson<{ success?: boolean; data?: CatalogResponse }>(res)
    if (!json?.success || !json.data) {
        return { total: 0, page: 1, per_page: 48, politicians: [] }
    }
    return json.data
}

export async function fetchSitemapEntries(): Promise<SitemapEntry[]> {
    const res = await fetch(
        `${getApiBaseUrl({ forServer: true })}/politicians/sitemap-entries`,
        { cache: "no-store" }
    )
    if (!res.ok) return []

    const json = await safeJson<{
        success?: boolean
        data?: { entries?: SitemapEntry[] }
    }>(res)
    if (!json?.success || !json.data?.entries) return []
    return json.data.entries
}

export async function fetchStates(): Promise<string[]> {
    const res = await fetch(`${getApiBaseUrl({ forServer: true })}/states`, {
        cache: "no-store",
    })
    if (!res.ok) return []

    const json = await safeJson<{ success?: boolean; data?: { states?: string[] } }>(res)
    if (!json?.success || !json.data?.states) return []
    return json.data.states
}

/** Map catalog record to Politician shape for shared card/link helpers. */
export function catalogToPolitician(entry: CatalogPolitician): Politician {
    return {
        id: entry.id,
        slug: entry.slug,
        name: entry.name,
        type: entry.type,
        state: entry.state,
        constituency: entry.constituency,
        photo: entry.photo,
        political_background: { elections: [] },
    }
}
