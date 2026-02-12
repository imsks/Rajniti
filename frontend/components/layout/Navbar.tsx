"use client"

import { motion } from "framer-motion"
import UserButton from "@/components/auth/UserButton"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import { fadeIn } from "@/utils/motion"

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
        <motion.header
            className={`border-b border-gray-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md shadow-sm ${stickyClasses}`}
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
        >
            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                <div className='flex h-16 items-center justify-between'>
                    <Link href='/' className='flex items-center gap-2 no-underline'>
                        <motion.div 
                            className='text-2xl font-bold'
                            whileHover={{ rotate: [0, -10, 10, -10, 0], scale: 1.1 }}
                            transition={{ duration: 0.5 }}
                        >
                            🗳️
                        </motion.div>
                        <Text variant='h4' className='text-foreground dark:text-foreground'>
                            Rajniti
                        </Text>
                    </Link>

                    <div className='flex flex-row gap-6 items-center'>
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
        </motion.header>
    )
}
