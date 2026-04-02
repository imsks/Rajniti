import type { Politician } from "@/types/politician"
import { getPoliticianProfileSegment } from "@/lib/politicianUtils"

function apiBase(): string {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
}

function isFullUuid(value: string): boolean {
    return /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(
        value
    )
}

/**
 * Full list for sitemap generation. Uses `no-store` so Next does not persist multi‑MB
 * responses in the Data Cache (avoids build/runtime cache errors on Vercel).
 */
export async function fetchPoliticiansList(): Promise<Politician[]> {
    const res = await fetch(`${apiBase()}/politicians?limit=1000`, {
        cache: "no-store",
    })
    if (!res.ok) return []
    const json = (await res.json()) as {
        success?: boolean
        data?: { politicians?: Politician[] }
    }
    if (!json.success || !json.data?.politicians) return []
    return json.data.politicians
}

/**
 * Resolve a profile URL segment to a politician (slug, UUID, or slug+short id suffix).
 * Mirrors client `usePolitician` resolution.
 */
export async function fetchPoliticianBySegment(
    segment: string
): Promise<Politician | null> {
    const API = apiBase()
    const key = segment

    try {
        const slugRes = await fetch(
            `${API}/politicians/slug/${encodeURIComponent(key)}`,
            { cache: "no-store" }
        )
        const slugJson = (await slugRes.json()) as {
            success?: boolean
            data?: Politician
        }
        if (slugRes.ok && slugJson?.success && slugJson?.data) {
            return slugJson.data
        }
    } catch {
        // fall through
    }

    if (isFullUuid(key)) {
        try {
            const res = await fetch(`${API}/politicians/${encodeURIComponent(key)}`, {
                cache: "no-store",
            })
            const json = (await res.json()) as { success?: boolean; data?: Politician }
            if (json.success && json.data) return json.data
        } catch {
            return null
        }
        return null
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
