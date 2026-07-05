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
    party?: string | null
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
    parties?: string[]
}

async function safeJson<T>(res: Response): Promise<T | null> {
    try {
        return (await res.json()) as T
    } catch {
        return null
    }
}

async function safeFetch(url: string): Promise<Response | null> {
    try {
        return await fetch(url, { cache: "no-store" })
    } catch {
        return null
    }
}

export async function fetchPoliticianCatalog(
    params: CatalogParams = {}
): Promise<CatalogResponse> {
    const empty: CatalogResponse = { total: 0, page: 1, per_page: 48, politicians: [] }

    const search = new URLSearchParams()
    if (params.page) search.set("page", String(params.page))
    if (params.perPage) search.set("per_page", String(params.perPage))
    if (params.type) search.set("type", params.type)
    if (params.state) search.set("state", params.state)
    if (params.q) search.set("q", params.q)
    if (params.parties && params.parties.length > 0) {
        search.set("party", params.parties.join(","))
    }

    const qs = search.toString()
    const url = `${getApiBaseUrl({ forServer: true })}/politicians/catalog${qs ? `?${qs}` : ""}`

    const res = await safeFetch(url)
    if (!res?.ok) return empty

    const json = await safeJson<{ success?: boolean; data?: CatalogResponse }>(res)
    if (!json?.success || !json.data) return empty
    return json.data
}

export async function fetchSitemapEntries(): Promise<SitemapEntry[]> {
    const url = `${getApiBaseUrl({ forServer: true })}/politicians/sitemap-entries`
    const res = await safeFetch(url)
    if (!res?.ok) return []

    const json = await safeJson<{
        success?: boolean
        data?: { entries?: SitemapEntry[] }
    }>(res)
    if (!json?.success || !json.data?.entries) return []
    return json.data.entries
}

export async function fetchStates(): Promise<string[]> {
    const url = `${getApiBaseUrl({ forServer: true })}/states`
    const res = await safeFetch(url)
    if (!res?.ok) return []

    const json = await safeJson<{ success?: boolean; data?: { states?: string[] } }>(res)
    if (!json?.success || !json.data?.states) return []
    return json.data.states
}

export async function fetchParties(): Promise<string[]> {
    const url = `${getApiBaseUrl({ forServer: true })}/parties`
    const res = await safeFetch(url)
    if (!res?.ok) return []

    const json = await safeJson<{ success?: boolean; data?: { parties?: string[] } }>(res)
    if (!json?.success || !json.data?.parties) return []
    return json.data.parties
}

/** Map catalog record to Politician shape for shared card/link helpers. */
export function catalogToPolitician(entry: CatalogPolitician): Politician {
    // Carry party via a minimal synthetic election so getParty()/getPartyInitial()
    // keep working off the standard Politician shape.
    const elections = entry.party
        ? [
              {
                  year: 0,
                  type: entry.type,
                  state: entry.state,
                  constituency: entry.constituency,
                  party: entry.party,
                  status: "",
              },
          ]
        : []
    return {
        id: entry.id,
        slug: entry.slug,
        name: entry.name,
        type: entry.type,
        state: entry.state,
        constituency: entry.constituency,
        photo: entry.photo,
        political_background: { elections },
    }
}
