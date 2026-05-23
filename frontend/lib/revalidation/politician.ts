/** ISR window for politician profile pages and API fetches (seconds). */
export const POLITICIAN_REVALIDATE_SECONDS = 3600

/** Runtime override for fetch cache duration (page segment export must stay static). */
export function getPoliticianRevalidateSeconds(): number {
    const fromEnv = Number(process.env.POLITICIAN_REVALIDATE_SECONDS)
    return Number.isFinite(fromEnv) && fromEnv > 0
        ? fromEnv
        : POLITICIAN_REVALIDATE_SECONDS
}

/** Cache tag for on-demand revalidation of a politician profile. */
export function politicianRevalidationTag(segment: string): string {
    return `politician-${segment.trim().toLowerCase()}`
}

/** Public profile path for a URL segment (slug or id). */
export function politicianProfilePath(segment: string): string {
    return `/politician/${encodeURIComponent(segment.trim())}`
}
