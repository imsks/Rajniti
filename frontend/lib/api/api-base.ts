/** Strip trailing slash from a URL string. */
function trimTrailingSlash(url: string): string {
    return url.replace(/\/$/, "")
}

function isLocalhostHostname(hostname: string): boolean {
    return (
        hostname === "localhost" ||
        hostname === "127.0.0.1" ||
        hostname === "::1" ||
        hostname === "[::1]"
    )
}

function isBrowserOnlyApiUrl(url: string): boolean {
    try {
        return isLocalhostHostname(new URL(url).hostname)
    } catch {
        return false
    }
}

/**
 * SSR fetch base via the Next.js /api/v1 rewrite (works in Docker without API_URL).
 */
function getProxiedApiBaseUrl(): string {
    const port = process.env.PORT || "3000"
    const host = process.env.HOST || "127.0.0.1"
    return `http://${host}:${port}/api/v1`
}

/**
 * Base URL for Rajniti API requests.
 * Server components prefer API_URL / INTERNAL_API_URL (Docker service hostname).
 * When only browser-local NEXT_PUBLIC_API_URL is set, SSR uses the Next /api/v1 proxy.
 * Client code uses NEXT_PUBLIC_API_URL (browser-reachable host).
 */
export function getApiBaseUrl(options?: { forServer?: boolean }): string {
    const useServerUrl =
        options?.forServer === true ||
        (options?.forServer !== false && typeof window === "undefined")

    if (useServerUrl) {
        const explicit =
            process.env.API_URL || process.env.INTERNAL_API_URL
        if (explicit) {
            return trimTrailingSlash(explicit)
        }

        const publicUrl = process.env.NEXT_PUBLIC_API_URL
        if (publicUrl && !isBrowserOnlyApiUrl(publicUrl)) {
            return trimTrailingSlash(publicUrl)
        }

        return getProxiedApiBaseUrl()
    }

    return trimTrailingSlash(
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
    )
}
