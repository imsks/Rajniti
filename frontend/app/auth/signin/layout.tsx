import type { Metadata } from "next"
import { SITE_NAME } from "@/lib/seo/site"

const title = "Sign in"

export const metadata: Metadata = {
    title,
    description: `Sign in to ${SITE_NAME} with Google to save preferences and track politicians you follow.`,
    robots: { index: false, follow: true },
}

export default function SignInLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return children
}
