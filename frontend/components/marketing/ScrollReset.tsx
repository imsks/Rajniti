"use client"

import { useEffect } from "react"
import { useScrollDepth } from "@/hooks/useScrollDepth"
import { useTimeOnPage } from "@/hooks/useTimeOnPage"

/**
 * Tiny client component that resets scroll position on mount and wires up
 * page-level analytics hooks (scroll depth + time on page) for the home page.
 * Extracted to keep the marketing page as a Server Component.
 */
export default function ScrollReset() {
    useScrollDepth("home")
    useTimeOnPage("home")

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
