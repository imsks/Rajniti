import type { Politician } from "@/types/politician"
import { getPoliticianProfileSegment } from "@/lib/politicianUtils"

const UUID_RE =
    /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/

export function isFullUuid(value: string): boolean {
    return UUID_RE.test(value.trim())
}

/** Preferred public path for a politician profile (slug-first). */
export function getPreferredPoliticianPath(politician: Politician): string {
    const segment = getPoliticianProfileSegment(politician)
    return `/politician/${encodeURIComponent(segment)}`
}

/** Whether the incoming URL segment should redirect to the preferred slug path. */
export function shouldRedirectToCanonical(
    segment: string,
    politician: Politician
): boolean {
    const preferred = getPoliticianProfileSegment(politician)
    const normalized = segment.trim()
    if (normalized === preferred) return false
    // Redirect UUID or slug+short-id variants to canonical slug
    return isFullUuid(normalized) || normalized !== preferred
}
