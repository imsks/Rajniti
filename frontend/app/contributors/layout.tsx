import type { Metadata } from "next"
import { buildDefaultOg, buildDefaultTwitter, getSiteUrl, SITE_NAME } from "@/lib/seo/site"

const title = "Contributors"
const description = `Open-source contributors building ${SITE_NAME} — transparent profiles for Indian MPs and MLAs.`

export const metadata: Metadata = {
    title,
    description,
    alternates: { canonical: `${getSiteUrl()}/contributors` },
    openGraph: {
        ...buildDefaultOg(),
        title: `${title} | ${SITE_NAME}`,
        description,
        url: `${getSiteUrl()}/contributors`,
    },
    twitter: {
        ...buildDefaultTwitter(),
        title: `${title} | ${SITE_NAME}`,
        description,
    },
}

export default function ContributorsLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return children
}
