import type { MetadataRoute } from "next"
import { getSiteUrl } from "@/lib/seo/site"

export default function robots(): MetadataRoute.Robots {
    const base = getSiteUrl()
    return {
        rules: {
            userAgent: "*",
            allow: "/",
            disallow: ["/api/", "/auth/", "/onboarding", "/profile/"],
        },
        sitemap: `${base}/sitemap.xml`,
    }
}
