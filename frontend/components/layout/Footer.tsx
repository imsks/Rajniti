"use client"

import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import { useAnalytics } from "@/hooks/useAnalytics"

export default function Footer() {
    const { trackEvent } = useAnalytics()
    return (
        <footer className='bg-[#0F1F3D] text-white'>
            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12'>
                <div className='flex flex-col items-center text-center gap-6'>
                    {/* Logo + tagline */}
                    <div className='flex flex-col gap-2'>
                        <span className='font-serif text-2xl font-semibold'>
                            Raj<span className='text-orange-500'>niti</span>
                        </span>
                        <Text variant='small' className='text-gray-400'>
                            Open source · Built for India · Community driven
                        </Text>
                        <p className='text-gray-500 text-sm mt-1'>
                            Built with love ❤️ in India 🇮🇳
                        </p>
                    </div>

                    {/* Links */}
                    <nav
                        className='flex flex-wrap justify-center gap-6 pt-2 border-t border-white/10 w-full max-w-xs'
                        aria-label='Footer links'
                    >
                        <Link
                            href='https://github.com/imsks/rajniti'
                            external
                            onClick={() => trackEvent('nav_click', { link_text: 'GitHub', link_url: 'https://github.com/imsks/rajniti', nav_section: 'footer' })}
                            className='text-gray-400 hover:text-white transition-colors text-sm'
                        >
                            GitHub
                        </Link>
                        <Link
                            href='/#about'
                            onClick={() => trackEvent('nav_click', { link_text: 'About', link_url: '/#about', nav_section: 'footer' })}
                            className='text-gray-400 hover:text-white transition-colors text-sm'
                        >
                            About
                        </Link>
                    </nav>
                </div>
            </div>
        </footer>
    )
}
