import path from "path"
import type { NextConfig } from "next"

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

    // Image optimization
    images: {
        remotePatterns: [
            {
                protocol: "https",
                hostname: "*",
                pathname: "/**"
            },
        ]
        // Vercel handles image optimization automatically
    },

    // Disable scroll restoration
    experimental: {
        scrollRestoration: false
    }
}

export default nextConfig
