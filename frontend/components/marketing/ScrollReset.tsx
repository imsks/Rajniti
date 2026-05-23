"use client"

import { useEffect } from "react"

/**
 * Tiny client component that resets scroll position on mount.
 * Extracted to keep the marketing page as a Server Component.
 */
export default function ScrollReset() {
    useEffect(() => {
        window.scrollTo({ top: 0, behavior: "auto" })

        if ("scrollRestoration" in history) {
            history.scrollRestoration = "manual"
        }

        return () => {
            if ("scrollRestoration" in history) {
                history.scrollRestoration = "auto"
            }
        }
    }, [])

    return null
}
