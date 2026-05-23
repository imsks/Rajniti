"use client"

import { useEffect, useState } from "react"

/** Delays mounting until the browser is idle (or after timeout) to defer non-critical work. */
export function useDeferredMount(timeoutMs = 2000): boolean {
    const [ready, setReady] = useState(false)

    useEffect(() => {
        const enable = () => setReady(true)

        if (typeof window !== "undefined" && "requestIdleCallback" in window) {
            const id = window.requestIdleCallback(enable, { timeout: timeoutMs })
            return () => window.cancelIdleCallback(id)
        }

        const timer = setTimeout(enable, 100)
        return () => clearTimeout(timer)
    }, [timeoutMs])

    return ready
}
