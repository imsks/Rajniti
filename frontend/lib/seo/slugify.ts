/** Slugify a string for URL segments (state names, etc.). */
export function slugifySegment(value: string): string {
    return value
        .toLowerCase()
        .normalize("NFKD")
        .replace(/[^\w\s-]/g, "")
        .trim()
        .replace(/\s+/g, "-")
        .replace(/-+/g, "-")
}

export function resolveStateFromSlug(slug: string, states: string[]): string | null {
    const normalized = slugifySegment(slug)
    return states.find((s) => slugifySegment(s) === normalized) ?? null
}
