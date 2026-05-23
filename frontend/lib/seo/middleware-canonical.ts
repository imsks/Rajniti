import type { NextRequest } from "next/server"
import { NextResponse } from "next/server"
import { isFullUuid } from "@/lib/seo/politician-canonical"

/**
 * Redirect UUID profile URLs to canonical slug URLs (301).
 * Returns null when no redirect is needed.
 */
export async function resolvePoliticianCanonicalRedirect(
    req: NextRequest
): Promise<NextResponse | null> {
    const match = req.nextUrl.pathname.match(/^\/politician\/([^/]+)$/)
    if (!match) return null

    const segment = decodeURIComponent(match[1])
    if (!isFullUuid(segment)) return null

    const apiUrl = `${req.nextUrl.origin}/api/v1/politicians/${encodeURIComponent(segment)}`

    try {
        const res = await fetch(apiUrl, {
            headers: { Accept: "application/json" },
        })
        if (!res.ok) return null

        const json = (await res.json()) as {
            success?: boolean
            data?: { slug?: string }
        }
        const slug = json?.data?.slug?.trim()
        if (!slug || slug === segment) return null

        const url = req.nextUrl.clone()
        url.pathname = `/politician/${encodeURIComponent(slug)}`
        return NextResponse.redirect(url, 301)
    } catch {
        return null
    }
}
