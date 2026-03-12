"use client"

import { Suspense, useEffect } from "react"
import PreambleSection from "@/components/PreambleSection"
import { Navbar, Footer } from "@/components/layout"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import Button from "@/components/ui/Button"
import Image from "next/image"
import { motion } from "framer-motion"
import { useAnalytics } from "@/hooks/useAnalytics"
import contributors from "@/data/contributors.json"

const civicPulse = [
    { label: "Profiles to explore", value: "50K+", tone: "from-orange-500/20 to-orange-100" },
    { label: "States and UTs", value: "36", tone: "from-sky-500/20 to-sky-100" },
    { label: "Community enriched", value: "Open", tone: "from-emerald-500/20 to-emerald-100" },
]

const questionPrompts = [
    "Which MPs have serious criminal cases?",
    "Show MLAs from Maharashtra with legal disclosures.",
    "Which party dominates my state?",
    "Who are the youngest representatives in Parliament?",
]

const discoveryCards = [
    {
        title: "Search with intent",
        eyebrow: "Find patterns",
        description:
            "Move beyond names. Search by constituency, party, state, and public record signals to compare representatives faster.",
        accent: "from-orange-500 to-amber-400",
    },
    {
        title: "Read richer profiles",
        eyebrow: "Understand context",
        description:
            "Every profile is designed to surface biography, election history, education, declared cases, and the details people usually have to dig for.",
        accent: "from-sky-700 to-blue-500",
    },
    {
        title: "Contribute improvements",
        eyebrow: "Help fill gaps",
        description:
            "Rajniti is meant to get sharper over time. Contributors can improve data quality, add missing records, and shape the product experience.",
        accent: "from-emerald-600 to-lime-500",
    },
]

export default function Home() {
    return (
        <Suspense>
            <HomeContent />
        </Suspense>
    )
}

function HomeContent() {
    const { trackEvent } = useAnalytics()

    useEffect(() => {
        // Ensure page starts at top
        window.scrollTo(0, 0)
        document.documentElement.scrollTop = 0
        document.body.scrollTop = 0
        
        // Disable scroll restoration
        if ('scrollRestoration' in history) {
            history.scrollRestoration = 'manual'
        }
    }, [])

    return (
        <div className='min-h-screen bg-linear-to-b from-orange-50 via-white to-green-70'>
            <Navbar variant='default' />

            {/* Hero Section */}
            <section className='relative overflow-hidden py-20 sm:py-28 lg:py-32 z-2'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <div className='relative z-10 grid items-center gap-14 lg:grid-cols-[minmax(0,1.05fr)_minmax(380px,0.95fr)]'>
                        <div>
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
                                <h1 className="font-serif text-[44px] sm:text-[56px] lg:text-[80px] font-semibold leading-[1.02] tracking-[-0.03em] text-[#0F1F3D] text-left mb-6">
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
                                    className='max-w-2xl text-lg leading-8 text-slate-600 mb-10'>
                                    Rajniti turns scattered public information into a
                                    clean civic product. Explore Indian MPs and MLAs,
                                    compare parties and states, and surface the context
                                    behind every profile with a community-built data layer.
                                </Text>
                            </motion.div>

                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: 0.3 }}
                                className='mb-8 flex flex-col sm:flex-row gap-4 justify-start items-start'>
                                <div className='shadow-[0_10px_40px_rgba(249,115,22,0.25)]'>
                                    <Button
                                        href='/dashboard'
                                        size='lg'
                                        onClick={() => trackEvent('cta_click', { cta_name: 'explore_politicians', cta_url: '/dashboard', page_location: 'home_hero' })}
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
                                    onClick={() => trackEvent('external_link_click', { link_text: 'View on GitHub', link_url: 'https://github.com/imsks/rajniti', page_location: 'home_hero' })}
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

                            <motion.div
                                initial={{ opacity: 0, y: 24 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.6, delay: 0.4 }}
                                className='flex flex-wrap gap-3'>
                                {questionPrompts.map((prompt) => (
                                    <div
                                        key={prompt}
                                        className='rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm font-medium text-slate-600 shadow-sm backdrop-blur'>
                                        {prompt}
                                    </div>
                                ))}
                            </motion.div>
                        </div>

                        <motion.div
                            initial={{ opacity: 0, x: 24 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.7, delay: 0.2 }}
                            className='relative z-20'>
                            <div className='absolute -right-12 top-10 hidden h-28 w-28 rounded-full bg-orange-300/40 blur-3xl lg:block' />
                            <div className='absolute -left-8 bottom-10 hidden h-28 w-28 rounded-full bg-emerald-300/40 blur-3xl lg:block' />
                            <div className='relative overflow-hidden rounded-[32px] border border-slate-200/70 bg-white/85 p-6 shadow-[0_30px_80px_rgba(15,31,61,0.16)] backdrop-blur'>
                                <div className='mb-6 flex items-center justify-between'>
                                    <div>
                                        <p className='text-sm font-semibold uppercase tracking-[0.24em] text-orange-600'>
                                            Civic Pulse
                                        </p>
                                        <h3 className='mt-2 font-serif text-3xl text-[#0F1F3D]'>
                                            A cleaner way to inspect political data
                                        </h3>
                                    </div>
                                    <div className='rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-500'>
                                        Live community dataset
                                    </div>
                                </div>

                                <div className='grid gap-4 sm:grid-cols-3'>
                                    {civicPulse.map((item) => (
                                        <div
                                            key={item.label}
                                            className={`rounded-2xl bg-gradient-to-br ${item.tone} p-4`}> 
                                            <div className='text-3xl font-semibold text-[#0F1F3D]'>
                                                {item.value}
                                            </div>
                                            <div className='mt-2 text-sm font-medium text-slate-600'>
                                                {item.label}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className='mt-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]'>
                                    <div className='rounded-3xl bg-[#0F1F3D] p-5 text-white'>
                                        <div className='mb-4 flex items-center justify-between'>
                                            <span className='text-sm font-semibold uppercase tracking-[0.2em] text-orange-300'>
                                                Explore flow
                                            </span>
                                            <span className='rounded-full bg-white/10 px-3 py-1 text-xs text-orange-100'>
                                                Dashboard ready
                                            </span>
                                        </div>
                                        <div className='space-y-4'>
                                            <div className='flex items-start gap-3'>
                                                <div className='mt-1 h-2.5 w-2.5 rounded-full bg-orange-400' />
                                                <div>
                                                    <p className='font-semibold'>Browse representatives</p>
                                                    <p className='text-sm text-slate-300'>Filter by type, state, party, and search intent.</p>
                                                </div>
                                            </div>
                                            <div className='flex items-start gap-3'>
                                                <div className='mt-1 h-2.5 w-2.5 rounded-full bg-sky-400' />
                                                <div>
                                                    <p className='font-semibold'>Read profile detail</p>
                                                    <p className='text-sm text-slate-300'>Surface election context, education, and public declarations.</p>
                                                </div>
                                            </div>
                                            <div className='flex items-start gap-3'>
                                                <div className='mt-1 h-2.5 w-2.5 rounded-full bg-emerald-400' />
                                                <div>
                                                    <p className='font-semibold'>Contribute missing data</p>
                                                    <p className='text-sm text-slate-300'>Improve quality and make the dataset more useful for everyone.</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className='rounded-3xl border border-slate-200 bg-slate-50 p-5'>
                                        <p className='text-sm font-semibold uppercase tracking-[0.2em] text-slate-500'>
                                            Popular prompts
                                        </p>
                                        <div className='mt-4 space-y-3'>
                                            {questionPrompts.slice(0, 3).map((prompt, index) => (
                                                <div key={prompt} className='rounded-2xl bg-white px-4 py-3 shadow-sm'>
                                                    <div className='text-xs font-semibold text-orange-500'>0{index + 1}</div>
                                                    <div className='mt-1 text-sm font-medium text-slate-700'>{prompt}</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </div>

                    {/* Ashoka Chakra - Below content on mobile, right side on desktop */}
                    <motion.svg
                        className="pointer-events-none mx-auto mt-12 opacity-35 lg:absolute lg:right-[-220px] lg:top-[50%] lg:z-0 lg:-translate-y-1/2 lg:mt-0 xl:right-[-260px] w-[300px] h-[300px] sm:w-[400px] sm:h-[400px] lg:w-[520px] lg:h-[520px] xl:w-[640px] xl:h-[640px] text-blue-800"
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

            <section className='bg-[#F7F2EA] py-20'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <div className='grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-end'>
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5 }}>
                            <div className='text-sm font-semibold uppercase tracking-[0.26em] text-orange-600'>
                                Discover faster
                            </div>
                            <h2 className='mt-4 font-serif text-4xl leading-tight text-[#0F1F3D] md:text-5xl'>
                                Built for citizens, journalists, researchers, and contributors
                            </h2>
                            <Text variant='body' className='mt-5 max-w-xl text-slate-600'>
                                The experience should feel useful before it feels technical. Rajniti is strongest when it helps people spot patterns, compare representatives, and verify public claims quickly.
                            </Text>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                            className='grid gap-4 sm:grid-cols-3'>
                            {discoveryCards.map((card, index) => (
                                <div key={card.title} className='rounded-[28px] border border-black/8 bg-white p-6 shadow-[0_12px_40px_rgba(15,31,61,0.08)]'>
                                    <div className={`mb-5 inline-flex rounded-full bg-gradient-to-r ${card.accent} px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white`}>
                                        {card.eyebrow}
                                    </div>
                                    <h3 className='text-2xl font-semibold text-[#0F1F3D]'>{card.title}</h3>
                                    <Text variant='body' className='mt-3 text-slate-600'>
                                        {card.description}
                                    </Text>
                                    <div className='mt-6 text-sm font-semibold text-slate-400'>0{index + 1}</div>
                                </div>
                            ))}
                        </motion.div>
                    </div>
                </div>
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
                            <div className='text-4xl mb-4'><Image src="/logo/parliament.png" alt="Parliament Logo" width={40} height={40} className="w-10 h-10" /></div>
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
                            <div className='text-4xl mb-4'><Image src="/logo/Assembly.png" alt="State Assembly Logo" width={40} height={40} className="w-10 h-10" /></div>
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
                            <div className='text-4xl mb-4'><Image src="/logo/Profile.png" alt="Rich Profile Logo" width={36} height={36} className="w-9 h-9" /></div>
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
                            <div className='text-3xl mb-3'><Image src="/logo/ContributeData.png" alt="Contribute Data Logo" width={40} height={40} className="w-10 h-10" /></div>
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
                                onClick={() => trackEvent('contribute_click', { contribute_type: 'data', page_location: 'home_contribute' })}
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
                            <div className='text-3xl mb-3'><Image src="/logo/Contribute.png" alt="Contribute Code Logo" width={40} height={40} className="w-10 h-10" /></div>
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
                                onClick={() => trackEvent('contribute_click', { contribute_type: 'code', page_location: 'home_contribute' })}
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
                        <Button
                            href='/dashboard'
                            size='lg'
                            onClick={() => trackEvent('cta_click', { cta_name: 'explore_politicians', cta_url: '/dashboard', page_location: 'home_contribute' })}
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

            {/* Top Contributors Preview */}
            <section id="contributors" className="py-20 bg-white">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-12"
                    >
                        <div className="flex items-center justify-center gap-3 text-md font-semibold text-orange-600 mb-4 uppercase tracking-wider">
                            <div className="w-8 h-0.5 border-t-2 border-orange-600" />
                            Community
                        </div>
                        <h2 className="text-xl md:text-4xl lg:text-5xl font-serif font-bold text-[#0F1F3D] mb-6">
                            Built by <span className="text-orange-600 italic">Contributors</span>
                        </h2>
                        <Text variant="body" className="text-gray-600 max-w-3xl mx-auto">
                            Rajniti is open source and community-driven. Meet the people
                            making Indian democracy more transparent.
                        </Text>
                    </motion.div>

                    <div className="flex flex-wrap justify-center gap-6">
                        {contributors.slice(0, 6).map((c, i) => (
                            <motion.a
                                key={c.login}
                                href={c.html_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.4, delay: i * 0.08 }}
                                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                                className="flex flex-col items-center gap-3 rounded-2xl border border-black/10 bg-white p-6 w-36 text-center hover:shadow-lg transition-shadow"
                            >
                                <Image
                                    src={c.avatar_url}
                                    alt={c.login}
                                    width={64}
                                    height={64}
                                    className="rounded-full"
                                />
                                <Text variant="small" weight="semibold" className="text-[#0F1F3D] truncate max-w-full">
                                    {c.login}
                                </Text>
                                <Text variant="caption" color="muted">
                                    {c.contributions} commit{c.contributions !== 1 ? "s" : ""}
                                </Text>
                            </motion.a>
                        ))}
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="text-center mt-10"
                    >
                        <Button
                            href="/contributors"
                            variant="secondary"
                            size="lg"
                            onClick={() => trackEvent('cta_click', { cta_name: 'view_all_contributors', cta_url: '/contributors', page_location: 'home_contributors' })}
                            rightIcon={
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                </svg>
                            }
                        >
                            View All Contributors
                        </Button>
                    </motion.div>
                </div>
            </section>

            <Footer />
        </div>
    )
}
