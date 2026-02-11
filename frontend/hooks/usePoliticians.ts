"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import type { Politician, ElectionType } from "@/types/politician"

const API = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1`

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
        } catch (err) {
            console.error('API connection failed:', err)
            setError(`Cannot connect to backend API at ${API}/politicians`)
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

export function usePolitician(id: string | null) {
    const [politician, setPolitician] = useState<Politician | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!id) { setLoading(false); return }

        const run = async () => {
            try {
                setLoading(true)
                const res = await fetch(`${API}/politicians/${encodeURIComponent(id)}`)
                const json = await res.json()
                if (json.success) {
                    setPolitician(json.data)
                    setError(null)
                } else {
                    setError(json.error ?? "Politician not found")
                }
            } catch {
                setError("Cannot connect to API")
            } finally {
                setLoading(false)
            }
        }

        run()
    }, [id])

    return { politician, loading, error }
}
