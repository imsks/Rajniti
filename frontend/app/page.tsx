"use client"

import PreambleSection from "@/components/PreambleSection"
import { Navbar, Footer } from "@/components/layout"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import Button from "@/components/ui/Button"
import { motion } from "framer-motion"
import { useEffect, useState } from "react"

export default function Home() {
    const [isReady, setIsReady] = useState(false)

    useEffect(() => {
        // Ensure page starts at top
        window.scrollTo(0, 0)
        document.documentElement.scrollTop = 0
        document.body.scrollTop = 0
        
        // Disable scroll restoration
        if ('scrollRestoration' in history) {
            history.scrollRestoration = 'manual'
        }
        
        setIsReady(true)
    }, [])

    if (!isReady) {
        return null
    }

    return (
        <div className='min-h-screen bg-linear-to-b from-orange-50 via-white to-green-70'>
            <Navbar variant='default' />

            {/* Hero Section */}
            <section className='py-20 sm:py-32 relative z-2'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <div className='text-center'>
                        <motion.div
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6 }}
                            className='mb-8 flex justify-start'>
                            <div className='rounded-full bg-gradient-to-r from-orange-500 via-white to-green-500 p-[2px] shadow-lg'>
                                <div className='rounded-full bg-white px-6 py-2.5 flex items-center gap-2'>
                                    <svg className='w-5 h-5' viewBox='0 0 24 24' fill='none'>
                                        <circle cx='12' cy='12' r='10' fill='#FF9933'/>
                                        <circle cx='12' cy='12' r='6.5' fill='#F5F5F5'/>
                                        <circle cx='12' cy='12' r='3' fill='#138808'/>
                                        <circle cx='12' cy='12' r='1.5' fill='#000080'/>
                                    </svg>
                                    <span className='text-sm font-semibold bg-gradient-to-r from-orange-600 via-gray-700 to-green-600 bg-clip-text text-transparent'>
                                        Built for the Indian Democracy
                                    </span>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.1 }}>
                            <h1 className="font-serif text-[44px] sm:text-[56px] lg:text-[80px] font-semibold leading-[1.08] tracking-[-0.02em] text-[#0F1F3D] text-left mb-4">
                                Know Your
                                <br />
                                <span className="text-orange-600 italic">Elected</span> Representatives
                            </h1>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.2 }}>
                            <Text
                                variant='body'
                                className='max-w-2xl text-gray-600 mb-10'>
                                Rajniti is an open-source platform to explore Indian
                                MPs and MLAs — their political history, education,
                                family background, criminal records, and more. All free
                                and community-driven.
                            </Text>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.3 }}
                            className='flex flex-col sm:flex-row gap-4 justify-start items-start'>
                            <div className='shadow-[0_8px_30px_rgba(249,115,22,0.25)]'>
                                <Button
                                    href='/dashboard'
                                    size='lg'
                                    rightIcon={
                                        <svg
                                            className='w-5 h-5'
                                            fill='none'
                                            stroke='currentColor'
                                            viewBox='0 0 24 24'>
                                            <path
                                                strokeLinecap='round'
                                                strokeLinejoin='round'
                                                strokeWidth={2}
                                                d='M13 7l5 5m0 0l-5 5m5-5H6'
                                            />
                                        </svg>
                                    }>
                                    Explore Politicians
                                </Button>
                            </div>

                            <Button
                                href='https://github.com/imsks/rajniti'
                                external
                                variant='secondary'
                                size='lg'
                                leftIcon={
                                    <svg
                                        className='w-5 h-5'
                                        fill='currentColor'
                                        viewBox='0 0 24 24'>
                                        <path
                                            fillRule='evenodd'
                                            d='M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z'
                                            clipRule='evenodd'
                                        />
                                    </svg>
                                }>
                                View on GitHub
                            </Button>
                        </motion.div>
                    </div>

                    {/* Ashoka Chakra - Below content on mobile, right side on desktop */}
                    <motion.svg
                        className="pointer-events-none mx-auto mt-12 lg:absolute lg:right-[-80px] lg:top-[50%] lg:-translate-y-1/2 lg:mt-0 w-[300px] h-[300px] sm:w-[400px] sm:h-[400px] lg:w-[520px] lg:h-[520px] xl:w-[640px] xl:h-[640px] text-blue-800"
                        viewBox="0 0 24 24"
                        fill="none"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 18, repeat: Infinity, ease: "linear" }}>
                        <circle cx="12" cy="12" r="1.5" fill="currentColor" />
                        {Array.from({ length: 24 }).map((_, i) => {
                            const angle = (i * 360) / 24
                            const rad = (angle * Math.PI) / 180
                            const x1 = 12 + Math.cos(rad) * 3
                            const y1 = 12 + Math.sin(rad) * 3
                            const x2 = 12 + Math.cos(rad) * 10
                            const y2 = 12 + Math.sin(rad) * 10
                            return (
                                <line
                                    key={i}
                                    x1={x1}
                                    y1={y1}
                                    x2={x2}
                                    y2={y2}
                                    stroke="currentColor"
                                    strokeWidth="0.5"
                                />
                            )
                        })}
                        <circle
                            cx="12"
                            cy="12"
                            r="10"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1"
                        />
                    </motion.svg>
                </div>

                {/* Decorative Elements */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 0.2, scale: 1 }}
                    transition={{ duration: 1.5, repeat: Infinity, repeatType: "reverse" }}
                    className='absolute top-0 left-0 w-72 h-72 bg-orange-200 rounded-full mix-blend-multiply filter blur-3xl z-1 pointer-events-none'></motion.div>
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 0.2, scale: 1 }}
                    transition={{ duration: 1.5, delay: 0.5, repeat: Infinity, repeatType: "reverse" }}
                    className='absolute bottom-0 right-0 w-72 h-72 bg-green-200 rounded-full mix-blend-multiply filter blur-3xl z-1 pointer-events-none'></motion.div>
            </section>

            {/* What You Can Find */}
            <section id='about' className='py-20 bg-white'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className='text-center mb-16'>
                        <div className='flex items-center justify-center gap-3 text-md font-semibold text-orange-600 mb-4 uppercase tracking-wider'>
                            <div className='w-8 h-0.5 border-t-2  border-orange-600'></div>
                            What You&apos;ll Find
                        </div>
                        <h2 className='text-xl md:text-4xl lg:text-5xl font-serif font-bold text-[#0F1F3D] mb-6'>
                            Transparency for Every <span className='text-orange-600 italic'>Citizen</span>
                        </h2>
                        <Text
                            variant='body'
                            className='text-gray-600 max-w-3xl mx-auto'>
                            We&apos;re building the most transparent and
                            comprehensive database of Indian elected
                            representatives.
                        </Text>
                    </motion.div>

                    <div className='grid md:grid-cols-3 gap-8'>
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                            whileHover={{ y: -8, transition: { duration: 0.2 } }}
                            className=' rounded-2xl p-8 border border-black/10'>
                            <div className='text-4xl mb-4'><img src="./logo/parliament.png" alt="Parliament Logo" className="w-10 h-10" />  </div>
                            <Text
                                variant='h4'
                                weight='bold'
                                className='text-[#0F1F3D] mb-3'>
                                Members of Parliament
                            </Text>
                            <Text variant='body' color='muted'>
                                Browse all winning Lok Sabha MPs — their party,
                                constituency, state, and election history.
                            </Text>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                            whileHover={{ y: -8, transition: { duration: 0.2 } }}
                            className=' rounded-2xl p-8 border border-black/10'>
                            <div className='text-4xl mb-4'><img src="./logo/Assembly.png" alt="State Assembly Logo" className="w-10 h-10" />  </div>
                            <Text
                                variant='h4'
                                weight='bold'
                                className='text-[#0F1F3D] mb-3'>
                                State Assembly MLAs
                            </Text>
                            <Text variant='body' color='muted'>
                                Explore elected MLAs from state assemblies across
                                India with detailed political backgrounds.
                            </Text>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.5, delay: 0.3 }}
                            whileHover={{ y: -8, transition: { duration: 0.2 } }}
                            className=' rounded-2xl p-8 border border-black/10'>
                            <div className='text-4xl mb-4'><img src="./logo/Profile.png" alt="Rich Profile Logo" className="w-9 h-9" />  </div>
                            <Text
                                variant='h4'
                                weight='bold'
                                className='text-[#0F1F3D] mb-3'>
                                Rich Profiles
                            </Text>
                            <Text variant='body' color='muted'>
                                Education, family, criminal records, social media,
                                and more — enriched with community contributions.
                            </Text>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* We The People of India - Preamble Section */}
            <PreambleSection />

            {/* Contribute Section */}
            <section
                id='contribute'
                className='py-20 bg-[#162844] text-white'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className='text-center mb-12'>
                        <Text variant='h1' className='text-white mb-4'>
                            Help Us Enrich <span className='text-orange-400 italic'>Profiles</span> 
                        </Text>
                        <Text
                            variant='body'
                            className='text-orange-100 max-w-3xl mx-auto'>
                            Many politician profiles are missing education, family,
                            and criminal record details. Your contributions make
                            democracy more transparent!
                        </Text>
                    </motion.div>

                    <div className='grid md:grid-cols-2 gap-8 max-w-4xl mx-auto'>
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
                            className='bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20'>
                            <div className='text-3xl mb-3'><img src="./logo/ContributeData.png" alt="Contribute Logo" className="w-10 h-10" />  </div>
                            <Text
                                variant='h4'
                                weight='bold'
                                className='text-white mb-2'>
                                Contribute Data
                            </Text>
                            <Text
                                variant='body'
                                className='text-orange-100 mb-4'>
                                Found a politician with missing info? Open an issue
                                with the details and we&apos;ll update the profile.
                            </Text>
                            <div className='border-t border-white/20 my-4'></div>
                            <Link
                                href='https://github.com/imsks/rajniti/issues'
                                external
                                className='inline-flex items-center gap-2 text-[#0F1F3D] font-bold hover:underline'>
                                Open an Issue
                                <svg
                                    className='w-4 h-4'
                                    fill='none'
                                    stroke='currentColor'
                                    viewBox='0 0 24 24'>
                                    <path
                                        strokeLinecap='round'
                                        strokeLinejoin='round'
                                        strokeWidth={2}
                                        d='M9 5l7 7-7 7'
                                    />
                                </svg>
                            </Link>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: 0.3 }}
                            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
                            className='bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20'>
                            <div className='text-3xl mb-3'><img src="./logo/Contribute.png" alt="Contribute Logo" className="w-10 h-10" />  </div>
                            <Text
                                variant='h4'
                                weight='bold'
                                className='text-white mb-2'>
                                Contribute Code
                            </Text>
                            <Text
                                variant='body'
                                className='text-orange-100 mb-4'>
                                Help improve the scraper, add new state MLAs, or
                                enhance the UI. All contributions are welcome, big or small!
                            </Text>
                            <div className='border-t border-white/20 '></div>
                            <Link
                                href='https://github.com/imsks/rajniti/fork'
                                external
                                className='inline-flex items-center gap-2 text-[#FFD700] font-bold hover:underline mt-4 '>
                                Fork &amp; Contribute
                                <svg
                                    className='w-4 h-4'
                                    fill='none'
                                    stroke='currentColor'
                                    viewBox='0 0 24 24'>
                                    <path
                                        strokeLinecap='round'
                                        strokeLinejoin='round'
                                        strokeWidth={2}
                                        d='M9 5l7 7-7 7'
                                    />
                                </svg>
                            </Link>
                        </motion.div>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                        className='text-center mt-12'>
                        <Link
                            href='/dashboard'
                            size='lg'
                            className='inline-flex items-center gap-3 bg-orange-600 text-white font-semibold px-6 py-3 rounded-lg border-2 border-orange-600  hover:text-white shadow-[0_8px_30px_rgba(249,115,22,0.2)]  hover:-translate-y-0.5 transition-all duration-300'
                            rightIcon={
                                <svg
                                    className='w-5 h-5'
                                    fill='none'
                                    stroke='currentColor'
                                    viewBox='0 0 24 24'>
                                    <path
                                        strokeLinecap='round'
                                        strokeLinejoin='round'
                                        strokeWidth={2}
                                        d='M13 7l5 5m0 0l-5 5m5-5H6'
                                    />
                                </svg>
                            }>
                            Explore Politicians
                        </Button>
                    </motion.div>
                </div>
            </section>

            <Footer />
        </div>
    )
}
