"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import type { Politician, ElectionType } from "@/types/politician"

const API = `${process.env.NEXT_PUBLIC_API_URL}`

// ─────────────────────────────────────────────────────────────────────────────
// usePoliticians — fetch all politicians once, derive everything client-side
// ─────────────────────────────────────────────────────────────────────────────

export function usePoliticians(type?: ElectionType) {
    const [all, setAll] = useState<Politician[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchAll = useCallback(async () => {
        try {
            setLoading(true)
            const params = new URLSearchParams({ limit: "1000" })
            if (type) params.set("type", type)

            const res = await fetch(`${API}/politicians?${params}`)
            const json = await res.json()

            if (json.success) {
                setAll(json.data?.politicians ?? [])
                setError(null)
            } else {
                setError(json.error ?? "Failed to load politicians")
            }
        } catch {
            setError("Cannot connect to API")
        } finally {
            setLoading(false)
        }
    }, [type])

    useEffect(() => { fetchAll() }, [fetchAll])

    // ── Derived data (pure, no API calls) ────────────────────────────────

    const states = useMemo(
        () => [...new Set(all.map((p) => p.state).filter(Boolean))].sort(),
        [all]
    )

    const parties = useMemo(() => {
        const s = new Set<string>()
        for (const p of all) {
            for (const e of p.political_background?.elections ?? []) {
                if (e.party) s.add(e.party)
            }
        }
        return [...s].sort()
    }, [all])

    const stats = useMemo(() => {
        const byParty: Record<string, number> = {}
        for (const p of all) {
            for (const e of p.political_background?.elections ?? []) {
                if (e.party) byParty[e.party] = (byParty[e.party] ?? 0) + 1
            }
        }
        const topParties = Object.entries(byParty)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)

        return {
            total: all.length,
            totalStates: states.length,
            totalParties: parties.length,
            topParty: topParties[0]?.[0] ?? "—",
        }
    }, [all, states, parties])

    /** Client-side filter + search */
    const filter = useCallback(
        (opts: { query?: string; state?: string; party?: string }) => {
            let list = all
            const q = (opts.query ?? "").toLowerCase().trim()

            if (opts.state) {
                list = list.filter(
                    (p) => p.state.toLowerCase() === opts.state!.toLowerCase()
                )
            }

            if (opts.party) {
                const pLower = opts.party.toLowerCase()
                list = list.filter((p) =>
                    p.political_background.elections.some(
                        (e) => e.party.toLowerCase() === pLower
                    )
                )
            }

            if (q) {
                list = list.filter((p) => {
                    const haystack = [
                        p.name,
                        p.state,
                        p.constituency,
                        ...p.political_background.elections.map((e) => e.party),
                    ]
                        .join(" ")
                        .toLowerCase()
                    return haystack.includes(q)
                })
            }

            return list
        },
        [all]
    )

    return { all, loading, error, states, parties, stats, filter, refetch: fetchAll }
}

// ─────────────────────────────────────────────────────────────────────────────
// usePolitician — fetch a single politician by ID
// ─────────────────────────────────────────────────────────────────────────────

export function usePolitician(idOrSlug: string | null) {
    const [politician, setPolitician] = useState<Politician | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const isUuidLike = (v: string) =>
        /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/.test(
            v
        )

    useEffect(() => {
        if (!idOrSlug) {
            setLoading(false)
            return
        }

        const run = async () => {
            try {
                setLoading(true)
                const key = idOrSlug

                // 1) Try by slug first (SEO-friendly URL)
                try {
                    const slugRes = await fetch(
                        `${API}/politicians/slug/${encodeURIComponent(key)}`
                    )
                    const slugJson = await slugRes.json()
                    if (slugRes.ok && slugJson?.success && slugJson?.data) {
                        setPolitician(slugJson.data as Politician)
                        setError(null)
                        return
                    }
                } catch {
                    // ignore slug errors; we'll fall back below if possible
                }

                // 2) Fallback to UUID-based URL for backward compatibility
                if (isUuidLike(key)) {
                    const res = await fetch(`${API}/politicians/${encodeURIComponent(key)}`)
                    const json = await res.json()
                    if (json.success && json.data) {
                        setPolitician(json.data as Politician)
                        setError(null)
                    } else {
                        setError(json.error ?? "Politician not found")
                    }
                    return
                }

                setError("Politician not found")
            } catch {
                setError("Cannot connect to API")
            } finally {
                setLoading(false)
            }
        }

        run()
    }, [idOrSlug])

    return { politician, loading, error }
}
