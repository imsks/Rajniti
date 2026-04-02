import type { Metadata } from "next"
import { SITE_NAME } from "@/lib/seo/site"

export const metadata: Metadata = {
    title: "Onboarding",
    description: `Complete your ${SITE_NAME} profile — preferences and discovery settings.`,
    robots: { index: false, follow: false },
}

export default function OnboardingLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return children
}
