"use client"

import PreambleSection from "@/components/PreambleSection"
import { Navbar, Footer } from "@/components/layout"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import Button from "@/components/ui/Button"
import SpotlightCard from "@/components/ui/SpotlightCard"
import { motion } from "framer-motion"
import {
    ArrowRight,
    BarChart3,
    Building2,
    Code2,
    Database,
    Github,
    Landmark,
} from "lucide-react"

export default function Home() {
    return (
        <div className='min-h-screen bg-linear-to-b from-orange-50 via-white to-green-50'>
            <Navbar variant='default' />

            {/* Hero Section */}
            <section className='py-20 sm:py-32 relative z-2'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <div className='text-center'>
                        <motion.div
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6 }}
                            className='mb-8 flex justify-center'>
                            <div className='rounded-full bg-linear-to-r from-orange-500 via-white to-green-500 p-1'>
                                <div className='rounded-full bg-white px-6 py-2'>
                                    <span className='text-sm font-semibold text-gray-700'>
                                        Built for 🇮🇳 Democracy
                                    </span>
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.1 }}>
                            <Text variant='h1' className='text-gray-900 mb-6'>
                                Know Your{" "}
                                <span className='block bg-linear-to-r from-orange-600 via-orange-500 to-green-600 bg-clip-text text-transparent'>
                                    Elected Representatives
                                </span>
                            </Text>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.2 }}>
                            <Text
                                variant='body'
                                className='mx-auto max-w-2xl text-gray-600 mb-10'>
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
                            className='flex flex-col sm:flex-row gap-4 justify-center items-center'>
                            <Button
                                href='/dashboard'
                                size='lg'
                                rightIcon={<ArrowRight className='w-5 h-5' />}>
                                Explore Politicians
                            </Button>

                            <Button
                                href='https://github.com/imsks/rajniti'
                                external
                                variant='secondary'
                                size='lg'
                                leftIcon={<Github className='w-5 h-5' />}>
                                View on GitHub
                            </Button>
                        </motion.div>
                    </div>
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
                        initial={false}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className='text-center mb-16'>
                        <Text variant='h2' className='text-gray-900 mb-4'>
                            What You&apos;ll Find
                        </Text>
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
                            initial={false}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                            className='h-full'>
                            <SpotlightCard
                                className='h-full bg-gradient-to-br from-blue-50 to-blue-100 p-8 border border-blue-200'
                                glowColor='rgba(59, 130, 246, 0.24)'>
                                <div className='mb-4 inline-flex rounded-xl bg-blue-500/10 p-3 text-blue-700'>
                                    <Landmark className='w-7 h-7' />
                                </div>
                                <Text
                                    variant='h4'
                                    weight='bold'
                                    className='text-gray-900 mb-3'>
                                    Members of Parliament
                                </Text>
                                <Text variant='body' color='muted'>
                                    Browse all winning Lok Sabha MPs — their party,
                                    constituency, state, and election history.
                                </Text>
                            </SpotlightCard>
                        </motion.div>

                        <motion.div
                            initial={false}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                            className='h-full'>
                            <SpotlightCard
                                className='h-full bg-gradient-to-br from-purple-50 to-purple-100 p-8 border border-purple-200'
                                glowColor='rgba(168, 85, 247, 0.24)'>
                                <div className='mb-4 inline-flex rounded-xl bg-purple-500/10 p-3 text-purple-700'>
                                    <Building2 className='w-7 h-7' />
                                </div>
                                <Text
                                    variant='h4'
                                    weight='bold'
                                    className='text-gray-900 mb-3'>
                                    State Assembly MLAs
                                </Text>
                                <Text variant='body' color='muted'>
                                    Explore elected MLAs from state assemblies across
                                    India with detailed political backgrounds.
                                </Text>
                            </SpotlightCard>
                        </motion.div>

                        <motion.div
                            initial={false}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.5, delay: 0.3 }}
                            className='h-full'>
                            <SpotlightCard
                                className='h-full bg-gradient-to-br from-orange-50 to-orange-100 p-8 border border-orange-200'
                                glowColor='rgba(249, 115, 22, 0.24)'>
                                <div className='mb-4 inline-flex rounded-xl bg-orange-500/10 p-3 text-orange-700'>
                                    <BarChart3 className='w-7 h-7' />
                                </div>
                                <Text
                                    variant='h4'
                                    weight='bold'
                                    className='text-gray-900 mb-3'>
                                    Rich Profiles
                                </Text>
                                <Text variant='body' color='muted'>
                                    Education, family, criminal records, social media,
                                    and more — enriched with community contributions.
                                </Text>
                            </SpotlightCard>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* We The People of India - Preamble Section */}
            <PreambleSection />

            {/* Contribute Section */}
            <section
                id='contribute'
                className='py-20 bg-linear-to-r from-orange-600 to-orange-500 text-white'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <motion.div
                        initial={false}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className='text-center mb-12'>
                        <Text variant='h2' className='text-white mb-4'>
                            Help Us Enrich Profiles
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
                            initial={false}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
                            className='bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20'>
                            <div className='mb-3 inline-flex rounded-xl bg-white/10 p-2 text-white'>
                                <Database className='w-6 h-6' />
                            </div>
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
                            <Link
                                href='https://github.com/imsks/rajniti/issues'
                                external
                                className='inline-flex items-center gap-2 text-white font-semibold hover:underline'>
                                Open an Issue
                                <ArrowRight className='w-4 h-4' />
                            </Link>
                        </motion.div>

                        <motion.div
                            initial={false}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: 0.3 }}
                            whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
                            className='bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20'>
                            <div className='mb-3 inline-flex rounded-xl bg-white/10 p-2 text-white'>
                                <Code2 className='w-6 h-6' />
                            </div>
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
                                enhance the UI. PRs welcome!
                            </Text>
                            <Link
                                href='https://github.com/imsks/rajniti/fork'
                                external
                                className='inline-flex items-center gap-2 text-white font-semibold hover:underline'>
                                Fork &amp; Contribute
                                <ArrowRight className='w-4 h-4' />
                            </Link>
                        </motion.div>
                    </div>

                    <motion.div
                        initial={false}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                        className='text-center mt-12'>
                        <Button
                            href='/dashboard'
                            className='bg-white text-orange-600 hover:bg-gray-50 border-none shadow-lg hover:shadow-xl hover:scale-105'
                            size='lg'
                            rightIcon={<ArrowRight className='w-5 h-5' />}>
                            Start Exploring
                        </Button>
                    </motion.div>
                </div>
            </section>

            <Footer />
        </div>
    )
}
