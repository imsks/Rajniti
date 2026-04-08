import type { Metadata } from "next"
import { buildDefaultOg, buildDefaultTwitter, getSiteUrl, SITE_NAME } from "@/lib/seo/site"

const title = "Browse MPs & MLAs"
const description = `Search and filter Lok Sabha MPs and state MLAs on ${SITE_NAME} — by state, party, and name.`

export const metadata: Metadata = {
    title,
    description,
    alternates: { canonical: `${getSiteUrl()}/dashboard` },
    openGraph: {
        ...buildDefaultOg(),
        title: `${title} | ${SITE_NAME}`,
        description,
        url: `${getSiteUrl()}/dashboard`,
    },
    twitter: {
        ...buildDefaultTwitter(),
        title: `${title} | ${SITE_NAME}`,
        description,
    },
}

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return children
}
