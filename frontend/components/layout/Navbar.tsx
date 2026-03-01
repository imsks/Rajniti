"use client"

import UserButton from "@/components/auth/UserButton"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import {
    Bug,
    Compass,
    HandHeart,
    Home,
    Info,
    Menu,
    MessageCircle,
    Users,
    X
} from "lucide-react"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"

interface NavbarProps {
    variant?: "default" | "dashboard"
    sticky?: boolean
}

export default function Navbar({
    variant = "default",
    sticky = false
}: NavbarProps) {
    const isDashboard = variant === "dashboard"
    const pathname = usePathname()
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
    const stickyClasses = sticky ? "sticky top-0 z-10" : ""
    const homeNavItems = [
        { href: "/dashboard", label: "Explore Politicians", icon: Compass },
        { href: "#about", label: "About", icon: Info },
        { href: "#contribute", label: "Contribute", icon: HandHeart },
        {
            href: "https://chat.whatsapp.com/IceA98FSHHuDmXOwv8WH7v",
            label: "Join Community",
            icon: MessageCircle,
            external: true
        }
    ]
    const dashboardNavItems = [
        { href: "/", label: "Home", icon: Home },
        { href: "/dashboard", label: "Politicians", icon: Users },
        {
            href: "https://github.com/imsks/rajniti/issues/new",
            label: "Found a Bug?",
            icon: Bug,
            external: true
        }
    ]
    const navItems = isDashboard ? dashboardNavItems : homeNavItems

    useEffect(() => {
        setIsMobileMenuOpen(false)
    }, [pathname])

    return (
        <header
            className={`border-b border-orange-200/80 bg-white/80 backdrop-blur-md supports-[backdrop-filter]:bg-white/70 ${stickyClasses}`}>
            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                <div className='flex h-16 items-center gap-3'>
                    <Link href='/' className='flex items-center gap-2 no-underline shrink-0'>
                        <div className='text-2xl font-bold'>🗳️</div>
                        <Text variant='h4' className='text-gray-900'>
                            Rajniti
                        </Text>
                    </Link>

                    <nav className='hidden sm:block min-w-0 flex-1' aria-label='Primary navigation'>
                        <div className='flex items-center gap-1 overflow-x-auto whitespace-nowrap rounded-full border border-orange-100 bg-orange-50/60 p-1'>
                            {navItems.map(item => {
                                const Icon = item.icon
                                const isHashLink = item.href.startsWith("#")
                                const isActive =
                                    !item.external &&
                                    !isHashLink &&
                                    (pathname === item.href ||
                                        (item.href !== "/" && pathname.startsWith(`${item.href}/`)))

                                return (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        variant='nav'
                                        external={item.external}
                                        className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm ${
                                            isActive
                                                ? "bg-white text-orange-600 shadow-sm"
                                                : "text-gray-700 hover:bg-white/80 focus-visible:bg-white/80 focus-visible:outline-none"
                                        }`}>
                                        {Icon && <Icon aria-hidden='true' className='h-4 w-4' />}
                                        {item.label}
                                    </Link>
                                )
                            })}
                        </div>
                    </nav>

                    <div className='hidden sm:block shrink-0'>
                        <UserButton />
                    </div>

                    <button
                        type='button'
                        aria-expanded={isMobileMenuOpen}
                        aria-controls='mobile-nav-panel'
                        aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
                        onClick={() => setIsMobileMenuOpen(open => !open)}
                        className='sm:hidden ml-auto inline-flex items-center justify-center rounded-md border border-orange-200 bg-white p-2 text-gray-700 hover:bg-orange-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-orange-500 focus-visible:ring-offset-2'>
                        {isMobileMenuOpen ? (
                            <X aria-hidden='true' className='h-5 w-5' />
                        ) : (
                            <Menu aria-hidden='true' className='h-5 w-5' />
                        )}
                    </button>
                </div>

                {isMobileMenuOpen && (
                    <div id='mobile-nav-panel' className='sm:hidden border-t border-orange-100 py-3'>
                        <nav aria-label='Mobile navigation' className='grid gap-1'>
                            {navItems.map(item => {
                                const Icon = item.icon
                                return (
                                    <Link
                                        key={`mobile-${item.href}`}
                                        href={item.href}
                                        variant='nav'
                                        external={item.external}
                                        className='inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-orange-50'>
                                        {Icon && <Icon aria-hidden='true' className='h-4 w-4' />}
                                        {item.label}
                                    </Link>
                                )
                            })}
                            {isDashboard && (
                                <div className='pt-1'>
                                    <UserButton />
                                </div>
                            )}
                        </nav>
                    </div>
                )}
            </div>
        </header>
    )
}
