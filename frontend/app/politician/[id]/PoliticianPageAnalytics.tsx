"use client"

import { useEffect, type RefObject } from "react"
import { useAnalytics } from "@/hooks/useAnalytics"
import { useScrollDepth } from "@/hooks/useScrollDepth"
import { useSectionTracking } from "@/hooks/useSectionTracking"
import { useTimeOnPage } from "@/hooks/useTimeOnPage"
import type { Politician } from "@/types/politician"

interface PoliticianPageAnalyticsProps {
    politician: Politician
    sectionsContainerRef: RefObject<HTMLDivElement | null>
    routeSlug: string | null
    routeUuidShort: string | null
}

/** Analytics hooks deferred until after first paint to reduce main-thread work at load. */
export default function PoliticianPageAnalytics({
    politician: p,
    sectionsContainerRef,
    routeSlug,
    routeUuidShort,
}: PoliticianPageAnalyticsProps) {
    const { trackEvent } = useAnalytics()

    useScrollDepth("politician_profile", { politician_id: p.id })
    useSectionTracking(sectionsContainerRef, { id: p.id, name: p.name })
    useTimeOnPage("politician_profile", { politician_id: p.id })

    useEffect(() => {
        const latestElection = p.political_background?.elections?.[0]
        trackEvent("politician_profile_view", {
            politician_id: p.id,
            politician_name: p.name,
            politician_type: p.type as "MP" | "MLA",
            party: latestElection?.party ?? "—",
            state: p.state,
            constituency: p.constituency,
            route_slug: routeSlug,
            route_uuid_short: routeUuidShort,
        })
    }, [p, trackEvent, routeSlug, routeUuidShort])

    return null
}
