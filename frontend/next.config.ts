import path from "path"
import type { NextConfig } from "next"

/** Origin for /api/v1 rewrites (host only, no /api/v1 suffix). */
function resolveApiRewriteOrigin(): string {
    const raw =
        process.env.API_REWRITE_TARGET ||
        process.env.API_URL ||
        process.env.NEXT_PUBLIC_API_URL ||
        "http://127.0.0.1:8000/api/v1"
    return raw.replace(/\/api\/v1\/?$/, "").replace(/\/$/, "")
}

const apiRewriteOrigin = resolveApiRewriteOrigin()

const nextConfig: NextConfig = {
    // Pin project root for Turbopack (avoids multi-lockfile workspace confusion)
    turbopack: {
        root: path.join(__dirname),
    },
    // Environment variables
    env: {
        NEXT_PUBLIC_API_URL:
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
    },

    // Proxy API through Next so SSR works in Docker (web container → rajniti-api)
    async rewrites() {
        return [
            {
                source: "/api/v1/:path*",
                destination: `${apiRewriteOrigin}/api/v1/:path*`,
            },
        ]
    },

    // Image optimization — allowlist known politician photo hosts (ECI)
    images: {
        remotePatterns: [
            {
                protocol: "https",
                hostname: "results.eci.gov.in",
                pathname: "/**",
            },
            {
                protocol: "https",
                hostname: "eci.gov.in",
                pathname: "/**",
            },
            {
                protocol: "https",
                hostname: "avatars.githubusercontent.com",
                pathname: "/**",
            },
        ],
    },

    // Disable scroll restoration
    experimental: {
        scrollRestoration: false,
        optimizePackageImports: ["lucide-react"],
    },
}

export default nextConfig
