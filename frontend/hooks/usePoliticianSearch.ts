"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import type { Politician } from "@/types/politician"

const API = `${process.env.NEXT_PUBLIC_API_URL}`
const DEBOUNCE_MS = 280
const MIN_QUERY_LENGTH = 2

export function usePoliticianSearch(query: string) {
    const [results, setResults] = useState<Politician[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    const search = useCallback(async (q: string) => {
        const trimmed = q.trim()
        if (trimmed.length < MIN_QUERY_LENGTH) {
            setResults([])
            setLoading(false)
            setError(null)
            return
        }
        setLoading(true)
        setError(null)
        try {
            const params = new URLSearchParams({
                q: trimmed,
                limit: "10",
            })
            const res = await fetch(`${API}/politicians/search?${params}`)
            const json = await res.json()
            if (json.success && Array.isArray(json.data?.politicians)) {
                setResults(json.data.politicians as Politician[])
            } else {
                setResults([])
            }
        } catch {
            setError("Search failed")
            setResults([])
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        const trimmed = query.trim()
        if (trimmed.length < MIN_QUERY_LENGTH) {
            setResults([])
            setLoading(false)
            setError(null)
            return
        }
        if (debounceRef.current) clearTimeout(debounceRef.current)
        debounceRef.current = setTimeout(() => {
            search(trimmed)
            debounceRef.current = null
        }, DEBOUNCE_MS)
        return () => {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current)
                debounceRef.current = null
            }
        }
    }, [query, search])

    return { results, loading, error }
}
