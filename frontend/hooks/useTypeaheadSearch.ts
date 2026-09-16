"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { getApiBaseUrl } from "@/lib/api/api-base"
import type { Politician } from "@/types/politician"

/** Default debounce for typeahead (faster than full search). */
const DEFAULT_DEBOUNCE_MS = 300
/** Minimum non-space characters before triggering search. */
const MIN_QUERY_LENGTH = 2
/** Maximum results to show in typeahead dropdown. */
const DEFAULT_LIMIT = 8

interface UseTypeaheadSearchOptions {
    /** Debounce delay in ms (default: 300). */
    debounceMs?: number
    /** Maximum results to return (default: 8). */
    limit?: number
}

interface UseTypeaheadSearchResult {
    results: Politician[]
    loading: boolean
    error: string | null
    /** Clear results and reset state. */
    clear: () => void
}

/**
 * Hook for typeahead search with configurable debounce.
 * Fires only after ≥2 non-space characters and a debounce delay.
 */
export function useTypeaheadSearch(
    query: string,
    options?: UseTypeaheadSearchOptions,
): UseTypeaheadSearchResult {
    const apiBaseUrl = getApiBaseUrl({ forServer: false })
    const debounceMs = options?.debounceMs ?? DEFAULT_DEBOUNCE_MS
    const limit = options?.limit ?? DEFAULT_LIMIT
    const trimmedQuery = query.trim()
    const nonSpaceChars = trimmedQuery.replace(/\s/g, "").length
    const isSearchable = nonSpaceChars >= MIN_QUERY_LENGTH

    const [results, setResults] = useState<Politician[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const abortRef = useRef<AbortController | null>(null)

    const clear = useCallback(() => {
        setResults([])
        setLoading(false)
        setError(null)
        if (debounceRef.current) {
            clearTimeout(debounceRef.current)
            debounceRef.current = null
        }
        if (abortRef.current) {
            abortRef.current.abort()
            abortRef.current = null
        }
    }, [])

    const search = useCallback(
        async (q: string) => {
            // Abort any in-flight request
            if (abortRef.current) {
                abortRef.current.abort()
            }
            const controller = new AbortController()
            abortRef.current = controller

            setLoading(true)
            setError(null)

            try {
                const params = new URLSearchParams({
                    q,
                    limit: String(limit),
                })
                const res = await fetch(`${apiBaseUrl}/politicians/search?${params}`, {
                    signal: controller.signal,
                })
                if (!res.ok) {
                    throw new Error(`Search failed: ${res.status}`)
                }
                const json = await res.json()

                if (json.success && Array.isArray(json.data?.politicians)) {
                    setResults(json.data.politicians as Politician[])
                } else {
                    setResults([])
                }
            } catch (err) {
                // Ignore abort errors
                if (err instanceof Error && err.name === "AbortError") {
                    return
                }
                setError("Search failed")
                setResults([])
            } finally {
                // Only set loading to false if this is still the active request
                if (abortRef.current === controller) {
                    setLoading(false)
                }
            }
        },
        [apiBaseUrl, limit],
    )

    useEffect(() => {
        if (!isSearchable) {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current)
                debounceRef.current = null
            }
            if (abortRef.current) {
                abortRef.current.abort()
                abortRef.current = null
            }
            return
        }

        // eslint-disable-next-line react-hooks/set-state-in-effect
        setLoading(true)

        if (debounceRef.current) {
            clearTimeout(debounceRef.current)
        }

        debounceRef.current = setTimeout(() => {
            search(trimmedQuery)
            debounceRef.current = null
        }, debounceMs)

        return () => {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current)
                debounceRef.current = null
            }
        }
    }, [debounceMs, isSearchable, search, trimmedQuery])

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current)
            }
            if (abortRef.current) {
                abortRef.current.abort()
            }
        }
    }, [])

    return {
        results: isSearchable ? results : [],
        loading: isSearchable ? loading : false,
        error: isSearchable ? error : null,
        clear,
    }
}
