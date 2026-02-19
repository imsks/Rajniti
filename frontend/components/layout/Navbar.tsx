"use client"

import UserButton from "@/components/auth/UserButton"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"

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

    return (
        <header
            className={`border-b border-orange-200 bg-white/80 backdrop-blur-sm ${stickyClasses}`}>
            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                <div className='flex h-16 items-center justify-between'>
                    <Link href='/' className='flex items-center gap-2 no-underline'>
                        <div className='w-7 h-7'><img src="./logo/voting-box.png" alt="Rajniti Logo" /></div>
                        <Text variant='h3' className='text-[#0F1F3D]  font-bold tracking-tight font-poppins mt-2'>
                            Raj<span><span className='text-orange-500'>niti</span></span>
                        </Text>
                    </Link>

                    <div className='flex flex-row gap-4'>
                        {isDashboard ? (
                            <>
                                <div className='flex items-center gap-4'>
                                    <Link href='/' variant='nav'>
                                        Home
                                    </Link>
                                </div>
                                <div className='flex items-center gap-4'>
                                    <Link href='/dashboard' variant='nav'>
                                        Politicians
                                    </Link>
                                </div>
                                <div className='flex items-center gap-4'>
                                    <Link
                                        href='https://github.com/imsks/rajniti/issues/new'
                                        variant='nav'
                                        target='_blank'>
                                        Found a Bug?
                                    </Link>
                                </div>
                            </>
                        ) : (
                            <nav className='hidden md:flex gap-6 items-center'>
                                <Link href='/dashboard' variant='nav'>
                                    Explore Politicians
                                </Link>
                                <Link href='#about' variant='nav'>
                                    About
                                </Link>
                                <Link href='#contribute' variant='nav'>
                                    Contribute
                                </Link>
                                <Link
                                    href='https://chat.whatsapp.com/IceA98FSHHuDmXOwv8WH7v'
                                    external
                                    variant='nav'>
                                    Join Community
                                </Link>
                            </nav>
                        )}

                        <UserButton />
                    </div>
                </div>
            </div>
        </header>
    )
}
