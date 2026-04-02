import type { Metadata } from "next"
import {
    buildDefaultOg,
    buildDefaultTwitter,
    defaultDescription,
    getSiteUrl,
    SITE_NAME,
} from "@/lib/seo/site"

export const metadata: Metadata = {
    title: {
        absolute: `${SITE_NAME} — Know Your Elected Representatives`,
    },
    description: defaultDescription,
    keywords: [
        "Indian MPs",
        "Indian MLAs",
        "Lok Sabha",
        "Vidhan Sabha",
        "election data India",
        "politician profiles",
        "open data",
        "Rajniti",
    ],
    openGraph: {
        ...buildDefaultOg(),
        title: `${SITE_NAME} — Know Your Elected Representatives`,
        description: defaultDescription,
        url: getSiteUrl(),
    },
    twitter: {
        ...buildDefaultTwitter(),
        title: `${SITE_NAME} — Know Your Elected Representatives`,
        description: defaultDescription,
    },
    alternates: {
        canonical: getSiteUrl(),
    },
}

export default function MarketingLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return children
}
