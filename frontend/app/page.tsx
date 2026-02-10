import PreambleSection from "@/components/PreambleSection"
import { Navbar, Footer } from "@/components/layout"
import Text from "@/components/ui/Text"
import Link from "@/components/ui/Link"
import Button from "@/components/ui/Button"

export default function Home() {
    return (
        <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50'>
            <Navbar variant='default' />

            {/* Hero Section */}
            <section className='py-20 sm:py-32 relative z-[2]'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <div className='text-center'>
                        <div className='mb-8 flex justify-center'>
                            <div className='rounded-full bg-gradient-to-r from-orange-500 via-white to-green-500 p-1'>
                                <div className='rounded-full bg-white px-6 py-2'>
                                    <span className='text-sm font-semibold text-gray-700'>
                                        Built for 🇮🇳 Democracy
                                    </span>
                                </div>
                            </div>
                        </div>

                        <Text variant='h1' className='text-gray-900 mb-6'>
                            Know Your{" "}
                            <span className='block bg-gradient-to-r from-orange-600 via-orange-500 to-green-600 bg-clip-text text-transparent'>
                                Elected Representatives
                            </span>
                        </Text>

                        <Text
                            variant='body'
                            className='mx-auto max-w-2xl text-gray-600 mb-10'>
                            Rajniti is an open-source platform to explore Indian
                            MPs and MLAs — their political history, education,
                            family background, criminal records, and more. All free
                            and community-driven.
                        </Text>

                        <div className='flex flex-col sm:flex-row gap-4 justify-center items-center'>
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
                        </div>
                    </div>
                </div>

                {/* Decorative Elements */}
                <div className='absolute top-0 left-0 w-72 h-72 bg-orange-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse z-[1] pointer-events-none'></div>
                <div className='absolute bottom-0 right-0 w-72 h-72 bg-green-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse delay-1000 z-[1] pointer-events-none'></div>
            </section>

            {/* What You Can Find */}
            <section id='about' className='py-20 bg-white'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <div className='text-center mb-16'>
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
                    </div>

                    <div className='grid md:grid-cols-3 gap-8'>
                        <div className='bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 border border-blue-200'>
                            <div className='text-4xl mb-4'>🏛️</div>
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
                        </div>

                        <div className='bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-8 border border-purple-200'>
                            <div className='text-4xl mb-4'>🏢</div>
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
                        </div>

                        <div className='bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-8 border border-orange-200'>
                            <div className='text-4xl mb-4'>📊</div>
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
                        </div>
                    </div>
                </div>
            </section>

            {/* We The People of India - Preamble Section */}
            <PreambleSection />

            {/* Contribute Section */}
            <section
                id='contribute'
                className='py-20 bg-gradient-to-r from-orange-600 to-orange-500 text-white'>
                <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
                    <div className='text-center mb-12'>
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
                    </div>

                    <div className='grid md:grid-cols-2 gap-8 max-w-4xl mx-auto'>
                        <div className='bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20'>
                            <div className='text-3xl mb-3'>💻</div>
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
                        </div>

                        <div className='bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20'>
                            <div className='text-3xl mb-3'>🔧</div>
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
                        </div>
                    </div>

                    <div className='text-center mt-12'>
                        <Button
                            href='/dashboard'
                            className='bg-white text-orange-600 hover:bg-gray-50 border-none shadow-lg hover:shadow-xl hover:scale-105'
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
                            Start Exploring
                        </Button>
                    </div>
                </div>
            </section>

            <Footer />
        </div>
    )
}
