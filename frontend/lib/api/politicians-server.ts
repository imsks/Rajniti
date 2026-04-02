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
 * All politicians at build time (same source as the dashboard list).
 * Cached for the duration of the static generation pass.
 */
export async function fetchPoliticiansList(): Promise<Politician[]> {
    const res = await fetch(`${apiBase()}/politicians?limit=1000`, {
        // Large payload may log a Next.js Data Cache size warning; build still prerenders.
        next: { revalidate: false },
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
            { next: { revalidate: false } }
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
                next: { revalidate: false },
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

/** Route param values for `generateStaticParams` and sitemap (one per politician). */
export async function getStaticPoliticianParams(): Promise<{ id: string }[]> {
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
