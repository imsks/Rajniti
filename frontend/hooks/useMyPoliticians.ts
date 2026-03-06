"use client"

import { useState, useEffect, useCallback } from "react"
import type { Politician } from "@/types/politician"
import {
    getMyPoliticianIds,
    setMyPoliticianIds,
    type MyPoliticianIds,
} from "@/lib/myPoliticiansStorage"

const API = `${process.env.NEXT_PUBLIC_API_URL}`

/** Pure: find politician by id in list; returns undefined if not found. */
export function findPoliticianById(
    list: Politician[],
    id: string | null
): Politician | undefined {
    if (!id) return undefined
    return list.find((p) => p.id === id)
}

/** Fetch a single politician by id (for when not in list). */
async function fetchPoliticianById(id: string): Promise<Politician | null> {
    try {
        const res = await fetch(`${API}/politicians/${encodeURIComponent(id)}`)
        const json = await res.json()
        if (json.success && json.data) return json.data as Politician
    } catch {
        // ignore
    }
    return null
}

export function useMyPoliticians(allPoliticians: Politician[]) {
    const [ids, setIds] = useState<MyPoliticianIds>(() =>
        typeof window === "undefined" ? { mpId: null, mlaId: null } : getMyPoliticianIds()
    )
    const [fetchedMP, setFetchedMP] = useState<Politician | null>(null)
    const [fetchedMLA, setFetchedMLA] = useState<Politician | null>(null)

    // Sync from localStorage on mount (e.g. another tab changed it)
    useEffect(() => {
        setIds(getMyPoliticianIds())
    }, [])

    const resolveMP = useCallback((): Politician | null => {
        const fromList = findPoliticianById(allPoliticians, ids.mpId)
        if (fromList) return fromList
        if (ids.mpId && fetchedMP?.id === ids.mpId) return fetchedMP
        return null
    }, [allPoliticians, ids.mpId, fetchedMP])

    const resolveMLA = useCallback((): Politician | null => {
        const fromList = findPoliticianById(allPoliticians, ids.mlaId)
        if (fromList) return fromList
        if (ids.mlaId && fetchedMLA?.id === ids.mlaId) return fetchedMLA
        return null
    }, [allPoliticians, ids.mlaId, fetchedMLA])

    // When ids point to missing politicians in list, fetch once
    useEffect(() => {
        if (!ids.mpId) {
            setFetchedMP(null)
            return
        }
        if (findPoliticianById(allPoliticians, ids.mpId)) {
            setFetchedMP(null)
            return
        }
        let cancelled = false
        fetchPoliticianById(ids.mpId).then((p) => {
            if (!cancelled) setFetchedMP(p)
        })
        return () => {
            cancelled = true
        }
    }, [ids.mpId, allPoliticians])

    useEffect(() => {
        if (!ids.mlaId) {
            setFetchedMLA(null)
            return
        }
        if (findPoliticianById(allPoliticians, ids.mlaId)) {
            setFetchedMLA(null)
            return
        }
        let cancelled = false
        fetchPoliticianById(ids.mlaId).then((p) => {
            if (!cancelled) setFetchedMLA(p)
        })
        return () => {
            cancelled = true
        }
    }, [ids.mlaId, allPoliticians])

    const myMP = resolveMP()
    const myMLA = resolveMLA()

    const setMyMP = useCallback((politician: Politician | null) => {
        const next = {
            mpId: politician?.id ?? null,
            mlaId: ids.mlaId,
        }
        setMyPoliticianIds(next)
        setIds(next)
        if (!politician) setFetchedMP(null)
    }, [ids.mlaId])

    const setMyMLA = useCallback((politician: Politician | null) => {
        const next = {
            mpId: ids.mpId,
            mlaId: politician?.id ?? null,
        }
        setMyPoliticianIds(next)
        setIds(next)
        if (!politician) setFetchedMLA(null)
    }, [ids.mpId])

    const clearSlot = useCallback((slot: "mp" | "mla") => {
        if (slot === "mp") setMyMP(null)
        else setMyMLA(null)
    }, [setMyMP, setMyMLA])

    return { myMP, myMLA, setMyMP, setMyMLA, clearSlot }
}
