import type { Politician } from "@/types/politician"

/** Path segment for `/politician/[slug]` — prefers API slug, falls back to id. */
export function getPoliticianProfileSegment(p: Politician): string {
    const slug = p.slug?.trim()
    if (slug) return slug
    return p.id
}

/** Full href for a politician profile (slug when available). */
export function getPoliticianProfileHref(p: Politician): string {
    return `/politician/${encodeURIComponent(getPoliticianProfileSegment(p))}`
}

/** Pure: get the latest (first) party name from political background. */
export function getParty(p: Politician): string {
    const elections = p.political_background?.elections ?? []
    return elections.length > 0 ? elections[0].party : "—"
}

/** Pure: short party abbreviation for avatar. */
export function getPartyInitial(p: Politician): string {
    const party = getParty(p)
    if (party === "—") return "?"
    const words = party.split(" ").filter((w) => w.length > 2)
    return words
        .slice(0, 3)
        .map((w) => w[0])
        .join("")
        .toUpperCase()
}
