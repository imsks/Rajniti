import Text from "@/components/ui/Text"

export default function PreambleSection() {
    return (
        <section className='py-24 bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900 relative overflow-hidden'>
            {/* Decorative Background Elements */}
            <div className='absolute -top-24 -left-24 w-80 h-80 bg-orange-200/20 dark:bg-orange-900/10 rounded-full blur-3xl'></div>
            <div className='absolute -bottom-24 -right-24 w-80 h-80 bg-green-200/20 dark:bg-green-900/10 rounded-full blur-3xl'></div>

            <div className='mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 relative z-10'>
                {/* Header */}
                <div className='text-center mb-14'>
                    <div className='inline-flex items-center gap-3 text-lg uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400 mb-4'>
                        <span className='h-px w-10 bg-orange-400'></span>
                        Preamble
                        <span className='h-px w-10 bg-green-500'></span>
                    </div>
                    <Text variant='h1' weight='bold' className='text-[#0F1F3D] dark:text-white mb-2 text-3xl sm:text-4xl'>
                        The <span className='text-orange-600 italic'>Constitution</span> of India
                    </Text>
                    <Text variant='body' className='text-gray-600 dark:text-gray-400'>
                        A statement of ideals that guides the Republic
                    </Text>
                </div>

                {/* Main Preamble Card */}
                <div className='bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden'>
                    <div className='h-1.5 bg-gradient-to-r from-orange-500 via-white to-green-600'></div>

                    <div className='p-10 sm:p-14'>
                        <div className='grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-start'>
                            <div>
                                <div className='mb-6'>
                                    <Text
                                        variant='h2'
                                        className='text-3xl sm:text-4xl md:text-5xl font-bold text-[#0F1F3D] dark:text-white leading-tight'>
                                        WE, THE PEOPLE OF INDIA
                                    </Text>
                                    <Text variant='body' className='text-gray-600 dark:text-gray-400 italic mt-3'>
                                        having solemnly resolved to constitute India into a
                                    </Text>
                                </div>

                                <div className='rounded-xl border border-gray-100 dark:border-gray-600 bg-gray-50/70 dark:bg-gray-700/50 p-6'>
                                    <Text
                                        variant='h3'
                                        weight='semibold'
                                        className='text-xl sm:text-2xl text-gray-900 dark:text-gray-100 leading-snug'>
                                        SOVEREIGN SOCIALIST SECULAR
                                        <br />
                                        DEMOCRATIC REPUBLIC
                                    </Text>
                                    <Text variant='body' className='text-gray-700 dark:text-gray-300 mt-4'>
                                        and to secure to all its citizens:
                                    </Text>
                                </div>

                                <div className='text-sm text-gray-600 dark:text-gray-400 italic mt-6'>
                                    In our Constituent Assembly this twenty-sixth day of
                                    November, 1949, we do hereby adopt, enact and give to
                                    ourselves this Constitution.
                                </div>
                            </div>

                            <div>
                                <div className='grid gap-4'>
                                    <div className='rounded-xl border border-orange-100 dark:border-orange-800/40 bg-orange-50/70 dark:bg-orange-900/20 p-5'>
                                        <Text variant='h4' weight='bold' className='text-orange-900 dark:text-orange-300 mb-1 text-lg'>
                                            JUSTICE
                                        </Text>
                                        <Text variant='small' className='text-orange-800 dark:text-orange-400'>
                                            social, economic and political
                                        </Text>
                                    </div>

                                    <div className='rounded-xl border border-blue-100 dark:border-blue-800/40 bg-blue-50/70 dark:bg-blue-900/20 p-5'>
                                        <Text variant='h4' weight='bold' className='text-blue-900 dark:text-blue-300 mb-1 text-lg'>
                                            LIBERTY
                                        </Text>
                                        <Text variant='small' className='text-blue-800 dark:text-blue-400'>
                                            of thought, expression, belief, faith and worship
                                        </Text>
                                    </div>

                                    <div className='rounded-xl border border-purple-100 dark:border-purple-800/40 bg-purple-50/70 dark:bg-purple-900/20 p-5'>
                                        <Text variant='h4' weight='bold' className='text-purple-900 dark:text-purple-300 mb-1 text-lg'>
                                            EQUALITY
                                        </Text>
                                        <Text variant='small' className='text-purple-800 dark:text-purple-400'>
                                            of status and of opportunity
                                        </Text>
                                    </div>

                                    <div className='rounded-xl border border-green-100 dark:border-green-800/40 bg-green-50/70 dark:bg-green-900/20 p-5'>
                                        <Text variant='h4' weight='bold' className='text-green-900 dark:text-green-300 mb-1 text-lg'>
                                            FRATERNITY
                                        </Text>
                                        <Text variant='small' className='text-green-800 dark:text-green-400'>
                                            assuring the dignity of the individual and the
                                            unity and integrity of the Nation
                                        </Text>
                                    </div>
                                </div>

                                <div className='flex items-center gap-3 mt-6 text-gray-500 dark:text-gray-400'>
                                    <span className='h-px flex-1 bg-gray-200 dark:bg-gray-600'></span>
                                    <Text variant='caption' className='uppercase tracking-[0.2em]'>Satyameva Jayate</Text>
                                    <span className='h-px flex-1 bg-gray-200 dark:bg-gray-600'></span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className='h-1.5 bg-gradient-to-r from-orange-500 via-white to-green-600'></div>
                </div>
            </div>
        </section>
    )
}
