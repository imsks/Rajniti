import type { Metadata } from "next"
import { SITE_NAME } from "@/lib/seo/site"

export const metadata: Metadata = {
    title: "Edit profile",
    description: `Update your ${SITE_NAME} account details and preferences.`,
    robots: { index: false, follow: false },
}

export default function EditProfileLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return children
}
