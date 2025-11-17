import type { NextConfig } from "next"

const nextConfig: NextConfig = {
    // Environment variables
    env: {
        NEXT_PUBLIC_API_URL:
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"
    },

    // Image optimization
    images: {
        remotePatterns: [
            {
                protocol: "https",
                hostname: "results.eci.gov.in",
                pathname: "/**"
            }
        ],
        unoptimized: true // Netlify handles image optimization
    }
}

export default nextConfig
