"use client"

import UserButton from "@/components/auth/UserButton"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import ThemeToggle from "@/components/ui/ThemeToggle"
import { useAnalytics } from "@/hooks/useAnalytics"

interface NavbarProps {
    variant?: "default" | "dashboard"
    sticky?: boolean
}

export default function Navbar({
    variant = "default",
    sticky = false
}: NavbarProps) {
    const isDashboard = variant === "dashboard"
    const stickyClasses = sticky ? "sticky top-0 z-10" : ""
    const { trackEvent } = useAnalytics()
    const trackNav = (text: string, url: string) => trackEvent('nav_click', { link_text: text, link_url: url, nav_section: 'navbar' })

    return (
        <header
            className={`border-b border-orange-200 dark:border-gray-700 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm ${stickyClasses}`}>
            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                <div className='flex h-16 items-center justify-between'>
                    <Link href='/' onClick={() => trackNav('Logo', '/')} className='flex items-center gap-2 no-underline'>
                        <div className='w-7 h-7'><img src='/logo/voting-box.png' alt='Rajniti Logo' /></div>
                        <Text variant='h3' className='text-[#0F1F3D] dark:text-white font-bold tracking-tight font-poppins mt-2'>
                            Raj<span><span className='text-orange-600'>niti</span></span>
                        </Text>
                    </Link>

                    <div className='flex items-center gap-4'>
                        {isDashboard ? (
                            <nav className='hidden sm:flex items-center gap-4'>
                                <Link href='/' variant='nav' onClick={() => trackNav('Home', '/')}>
                                    Home
                                </Link>
                                <Link
                                    href='https://github.com/imsks/rajniti/issues/new'
                                    variant='nav'
                                    target='_blank'
                                    onClick={() => {
                                        trackNav('Found a Bug?', 'https://github.com/imsks/rajniti/issues/new')
                                        trackEvent('contribute_click', { contribute_type: 'bug', page_location: 'navbar' })
                                    }}>
                                    Found a Bug?
                                </Link>
                            </nav>
                        ) : (
                            <nav className='hidden md:flex gap-6 items-center'>
                                <Link href='/dashboard' variant='nav' onClick={() => trackNav('Explore Politicians', '/dashboard')}>
                                    Explore Politicians
                                </Link>
                                <Link href='#about' variant='nav' onClick={() => trackNav('About', '#about')}>
                                    About
                                </Link>
                                <Link href='#contribute' variant='nav' onClick={() => trackNav('Contribute', '#contribute')}>
                                    Contribute
                                </Link>
                                <Link
                                    href='https://chat.whatsapp.com/IceA98FSHHuDmXOwv8WH7v'
                                    external
                                    variant='nav'
                                    onClick={() => trackEvent('external_link_click', { link_text: 'Join Community', link_url: 'https://chat.whatsapp.com/IceA98FSHHuDmXOwv8WH7v', page_location: 'navbar' })}>
                                    Join Community
                                </Link>
                            </nav>
                        )}

                        <ThemeToggle />
                        <UserButton />
                    </div>
                </div>
            </div>
        </header>
    )
}
