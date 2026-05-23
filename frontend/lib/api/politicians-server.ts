import type { Politician } from "@/types/politician"
import { getPoliticianProfileSegment } from "@/lib/politicianUtils"
import { getApiBaseUrl } from "@/lib/api/api-base"

/** Thrown when the API cannot be reached during SSR (distinct from politician not found). */
export class PoliticianApiUnreachableError extends Error {
    constructor(message = "Cannot reach Rajniti API") {
        super(message)
        this.name = "PoliticianApiUnreachableError"
    }
}

const IS_DEV = process.env.NODE_ENV === "development"

function isFullUuid(value: string): boolean {
    return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/i.test(
        value
    )
}

async function safeJson<T>(res: Response): Promise<T | null> {
    try {
        return (await res.json()) as T
    } catch {
        return null
    }
}

async function fetchPoliticianFromSlug(
    api: string,
    segment: string
): Promise<Politician | null> {
    const slugRes = await fetch(
        `${api}/politicians/slug/${encodeURIComponent(segment)}`,
        { cache: "no-store" }
    )
    const slugJson = await safeJson<{ success?: boolean; data?: Politician }>(slugRes)
    if (slugRes.ok && slugJson?.success && slugJson?.data) {
        return slugJson.data
    }
    return null
}

async function fetchPoliticianFromId(
    api: string,
    id: string
): Promise<Politician | null> {
    const res = await fetch(`${api}/politicians/${encodeURIComponent(id)}`, {
        cache: "no-store",
    })
    const json = await safeJson<{ success?: boolean; data?: Politician }>(res)
    if (json?.success && json?.data) return json.data
    return null
}

/**
 * Full list for sitemap generation. Uses `no-store` so Next does not persist multi‑MB
 * responses in the Data Cache (avoids build/runtime cache errors on Vercel).
 */
export async function fetchPoliticiansList(): Promise<Politician[]> {
    const res = await fetch(`${getApiBaseUrl({ forServer: true })}/politicians?limit=1000`, {
        cache: "no-store",
    })
    if (!res.ok) return []
    const json = await safeJson<{
        success?: boolean
        data?: { politicians?: Politician[] }
    }>(res)
    if (!json?.success || !json.data?.politicians) return []
    return json.data.politicians
}

/**
 * Resolve a profile URL segment to a politician (slug, UUID, or slug+short id suffix).
 * Mirrors client `usePolitician` resolution.
 * @throws PoliticianApiUnreachableError when the API cannot be reached
 */
export async function fetchPoliticianBySegment(
    segment: string
): Promise<Politician | null> {
    const API = getApiBaseUrl({ forServer: true })
    const key = segment.trim()
    let networkFailure = false

    try {
        const bySlug = await fetchPoliticianFromSlug(API, key)
        if (bySlug) return bySlug
    } catch {
        networkFailure = true
    }

    if (isFullUuid(key)) {
        try {
            const byId = await fetchPoliticianFromId(API, key.toLowerCase())
            if (byId) return byId
        } catch {
            networkFailure = true
        }
    }

    if (networkFailure) {
        throw new PoliticianApiUnreachableError(
            `Failed to fetch politician "${key}" from ${API}`
        )
    }

    if (IS_DEV) {
        console.warn(
            `[fetchPoliticianBySegment] No politician for segment "${key}" (API: ${API})`
        )
    }

    return null
}

/** Slug/id segments for sitemap URLs (one per politician). */
export async function getPoliticianIdsForSitemap(): Promise<{ id: string }[]> {
    const list = await fetchPoliticiansList()
    const seen = new Set<string>()
    const out: { id: string }[] = []
    for (const p of list) {
        const id = getPoliticianProfileSegment(p)
        if (seen.has(id)) continue
        seen.add(id)
        out.push({ id })
    }
    return out
}
