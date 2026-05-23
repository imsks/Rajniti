import { getSiteUrl } from "@/lib/seo/site"

export const DEFAULT_OG_IMAGE_PATH = "/og-default.png"

export function getDefaultOgImageUrl(): string {
    return `${getSiteUrl()}${DEFAULT_OG_IMAGE_PATH}`
}

export function buildOgImages(photo?: string | null, alt = "Rajniti") {
    if (photo?.trim()) {
        return [{ url: photo, alt }]
    }
    return [{ url: getDefaultOgImageUrl(), alt }]
}

export function buildTwitterImages(photo?: string | null): string[] {
    if (photo?.trim()) return [photo]
    return [getDefaultOgImageUrl()]
}
