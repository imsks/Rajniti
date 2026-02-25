import type { NextConfig } from "next"

const nextConfig: NextConfig = {
    // Environment variables
    env: {
        NEXT_PUBLIC_API_URL:
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
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
    }
}

export default nextConfig
