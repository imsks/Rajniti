"use client"

import NextImage from "next/image"
import UserButton from "@/components/auth/UserButton"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import ThemeToggle from "@/components/ui/ThemeToggle"
import { useAnalytics } from "@/hooks/useAnalytics"

interface NavbarProps {
    /** @deprecated Use sticky only; nav links are identical on every page. */
    variant?: "default" | "dashboard"
    sticky?: boolean
}

/** Public links always visible in the navbar. App links live in the profile menu. */
const NAV_LINKS: ReadonlyArray<{
    label: string
    href: string
    external?: boolean
}> = [
    { label: "About", href: "/#about" },
    { label: "Contribute", href: "/#contribute" },
    {
        label: "Found a Bug?",
        href: "https://github.com/imsks/rajniti/issues/new",
        external: true,
    },
]

export default function Navbar({ sticky = false }: NavbarProps) {
    const stickyClasses = sticky ? "sticky top-0" : ""
    const { trackEvent } = useAnalytics()
    const trackNav = (text: string, url: string) =>
        trackEvent("nav_click", { link_text: text, link_url: url, nav_section: "navbar" })

    return (
        <header
            className={`relative z-50 border-b border-orange-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm ${stickyClasses}`}
        >
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <div className="flex h-16 items-center justify-between">
                    <Link
                        href="/"
                        onClick={() => trackNav("Logo", "/")}
                        className="flex items-center gap-2 no-underline"
                    >
                        <div className="w-7 h-7">
                            <NextImage src="/logo/voting-box.png" alt="Rajniti Logo" width={28} height={28} />
                        </div>
                        <Text
                            variant="h3"
                            className="text-[#0F1F3D] dark:text-white font-bold tracking-tight font-poppins mt-2"
                        >
                            Raj<span><span className="text-orange-600">niti</span></span>
                        </Text>
                    </Link>

                    <div className="flex items-center gap-4">
                        <nav className="hidden md:flex gap-6 items-center">
                            {NAV_LINKS.map(({ label, href, external }) => (
                                <Link
                                    key={label}
                                    href={href}
                                    variant="nav"
                                    {...(external ? { external: true, target: "_blank" } : {})}
                                    onClick={() => {
                                        trackNav(label, href)
                                        if (label === "Found a Bug?") {
                                            trackEvent("contribute_click", {
                                                contribute_type: "bug",
                                                page_location: "navbar",
                                            })
                                        }
                                    }}
                                >
                                    {label}
                                </Link>
                            ))}
                        </nav>

                        <ThemeToggle />
                        <UserButton />
                    </div>
                </div>
            </div>
        </header>
    )
}
