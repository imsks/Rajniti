"use client"

import { useSession, signIn, signOut } from "next-auth/react"
import { useState, useRef, useEffect } from "react"
import Image from "@/components/ui/Image"
import Button from "@/components/ui/Button"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import { useAnalytics } from "@/hooks/useAnalytics"

export default function UserButton() {
    const { data: session } = useSession()
    const [showMenu, setShowMenu] = useState(false)
    const menuRef = useRef<HTMLDivElement>(null)
    const { trackEvent } = useAnalytics()

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (
                menuRef.current &&
                !menuRef.current.contains(event.target as Node)
            ) {
                setShowMenu(false)
            }
        }

        document.addEventListener("mousedown", handleClickOutside)
        return () => {
            document.removeEventListener("mousedown", handleClickOutside)
        }
    }, [])

    if (!session) {
        return <Button onClick={() => {
            trackEvent('login_start', { method: 'google', trigger_location: 'navbar_button' })
            signIn()
        }}>Sign In</Button>
    }

    return (
        <div className='relative z-50'>
            <button
                onClick={() => setShowMenu(!showMenu)}
                className='flex items-center gap-2 p-1 pr-3 border-2 border-orange-200 dark:border-gray-600 rounded-full hover:border-orange-300 dark:hover:border-gray-500 transition-all cursor-pointer'>
                <Image
                    src={session.user?.image || "/default-avatar.png"}
                    alt={session.user?.name || "User"}
                    width={32}
                    height={32}
                    rounded='full'
                    className='w-8 h-8'
                />
                <Text variant='small' weight='medium' className='text-gray-700 dark:text-gray-300'>
                    {session.user?.name?.split(" ")[0]}
                </Text>
            </button>

            {showMenu && (
                <div className='absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-[100]'>
                    <div className='px-4 py-3 border-b border-gray-100 dark:border-gray-700'>
                        <Text variant='small' weight='semibold' color='default'>
                            {session.user?.name}
                        </Text>
                    </div>

                    <Link
                        href='/dashboard'
                        variant='secondary'
                        onClick={() => trackEvent('nav_click', { link_text: 'Dashboard', link_url: '/dashboard', nav_section: 'user_menu' })}
                        className='block px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer'>
                        Dashboard
                    </Link>

                    {/* <Link
                        href='/profile/edit'
                        variant='secondary'
                        className='block px-4 py-2 text-sm hover:bg-gray-50 transition-colors cursor-pointer'>
                        Edit Profile
                    </Link> */}

                    <button
                        onClick={() => {
                            trackEvent('logout', {})
                            signOut({ callbackUrl: "/" })
                        }}
                        className='w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors cursor-pointer'>
                        Sign Out
                    </button>
                </div>
            )}
        </div>
    )
}
