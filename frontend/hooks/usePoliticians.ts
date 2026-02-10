"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import type { Politician, ElectionType, PoliticianStats } from "@/types/politician"

const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

// ── List politicians ──────────────────────────────────────────────────────

interface UsePoliticiansOpts {
    type?: ElectionType
    limit?: number
}

export function usePoliticians(opts: UsePoliticiansOpts = {}) {
    const [politicians, setPoliticians] = useState<Politician[]>([])
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const typeRef = useRef(opts.type)
    const limitRef = useRef(opts.limit ?? 200)

    useEffect(() => {
        typeRef.current = opts.type
        limitRef.current = opts.limit ?? 200
    }, [opts.type, opts.limit])

    const fetch_ = useCallback(async () => {
        try {
            setLoading(true)
            const params = new URLSearchParams()
            if (typeRef.current) params.set("type", typeRef.current)
            params.set("limit", String(limitRef.current))

            const response = await fetch(
                `${API_BASE_URL}/politicians?${params.toString()}`
            )
            const data = await response.json()
            if (data.success) {
                setPoliticians(data.data.politicians ?? [])
                setTotal(data.data.total ?? 0)
                setError(null)
            } else {
                setError(data.error || "Failed to load politicians")
            }
        } catch (err) {
            setError("Error connecting to API")
            console.error("Error fetching politicians:", err)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetch_()
    }, [fetch_, opts.type, opts.limit])

    return { politicians, total, loading, error, refetch: fetch_ }
}

// ── Get single politician by ID ───────────────────────────────────────────

export function usePolitician(id: string | null) {
    const [politician, setPolitician] = useState<Politician | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!id) {
            setLoading(false)
            return
        }

        const fetchPolitician = async () => {
            try {
                setLoading(true)
                const response = await fetch(
                    `${API_BASE_URL}/politicians/${encodeURIComponent(id)}`
                )
                const data = await response.json()
                if (data.success) {
                    setPolitician(data.data)
                    setError(null)
                } else {
                    setError(data.error || "Politician not found")
                }
            } catch (err) {
                setError("Error connecting to API")
                console.error("Error fetching politician:", err)
            } finally {
                setLoading(false)
            }
        }

        fetchPolitician()
    }, [id])

    return { politician, loading, error }
}

// ── Search politicians ────────────────────────────────────────────────────

export function useSearchPoliticians() {
    const [results, setResults] = useState<Politician[]>([])
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const search = useCallback(
        async (
            query: string,
            opts?: { type?: ElectionType; state?: string; party?: string; limit?: number }
        ) => {
            if (!query.trim()) {
                setResults([])
                setTotal(0)
                return
            }

            try {
                setLoading(true)
                const params = new URLSearchParams({ q: query })
                if (opts?.type) params.set("type", opts.type)
                if (opts?.state) params.set("state", opts.state)
                if (opts?.party) params.set("party", opts.party)
                params.set("limit", String(opts?.limit ?? 50))

                const response = await fetch(
                    `${API_BASE_URL}/politicians/search?${params.toString()}`
                )
                const data = await response.json()
                if (data.success) {
                    setResults(data.data.politicians ?? [])
                    setTotal(data.data.total ?? 0)
                    setError(null)
                } else {
                    setError(data.error || "Search failed")
                }
            } catch (err) {
                setError("Error connecting to API")
                console.error("Error searching politicians:", err)
            } finally {
                setLoading(false)
            }
        },
        []
    )

    const clear = useCallback(() => {
        setResults([])
        setTotal(0)
        setError(null)
    }, [])

    return { results, total, loading, error, search, clear }
}

// ── Stats ─────────────────────────────────────────────────────────────────

export function useStats(type?: ElectionType) {
    const [stats, setStats] = useState<PoliticianStats | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const fetchStats = async () => {
            try {
                setLoading(true)
                const params = new URLSearchParams()
                if (type) params.set("type", type)

                const response = await fetch(
                    `${API_BASE_URL}/stats?${params.toString()}`
                )
                const data = await response.json()
                if (data.success) {
                    setStats(data.data)
                    setError(null)
                } else {
                    setError(data.error || "Failed to load stats")
                }
            } catch (err) {
                setError("Error connecting to API")
                console.error("Error fetching stats:", err)
            } finally {
                setLoading(false)
            }
        }

        fetchStats()
    }, [type])

    return { stats, loading, error }
}

// ── States list ───────────────────────────────────────────────────────────

export function useStates(type?: ElectionType) {
    const [states, setStates] = useState<string[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStates = async () => {
            try {
                setLoading(true)
                const params = new URLSearchParams()
                if (type) params.set("type", type)

                const response = await fetch(
                    `${API_BASE_URL}/states?${params.toString()}`
                )
                const data = await response.json()
                if (data.success) {
                    setStates(data.data.states ?? [])
                }
            } catch (err) {
                console.error("Error fetching states:", err)
            } finally {
                setLoading(false)
            }
        }

        fetchStates()
    }, [type])

    return { states, loading }
}

// ── Parties list ──────────────────────────────────────────────────────────

export function usePartyList(type?: ElectionType) {
    const [parties, setParties] = useState<string[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchParties = async () => {
            try {
                setLoading(true)
                const params = new URLSearchParams()
                if (type) params.set("type", type)

                const response = await fetch(
                    `${API_BASE_URL}/parties?${params.toString()}`
                )
                const data = await response.json()
                if (data.success) {
                    setParties(data.data.parties ?? [])
                }
            } catch (err) {
                console.error("Error fetching parties:", err)
            } finally {
                setLoading(false)
            }
        }

        fetchParties()
    }, [type])

    return { parties, loading }
}
