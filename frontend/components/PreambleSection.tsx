"use client"

import { motion } from "framer-motion"
import Text from "@/components/ui/Text"
import { scrollReveal, staggerContainer, fadeInUp, scaleIn, quickTransition } from "@/utils/motion"

export default function PreambleSection() {
    return (
        <section className='py-20 bg-gradient-to-br from-orange-50 via-white to-green-50 relative overflow-hidden'>
            {/* Decorative Background Elements */}
            <div className='absolute top-0 left-0 w-96 h-96 bg-orange-200/30 rounded-full blur-3xl'></div>
            <div className='absolute bottom-0 right-0 w-96 h-96 bg-green-200/30 rounded-full blur-3xl'></div>

            <div className='mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 relative z-10'>
                {/* Header with Indian Flag Colors Accent */}
                <motion.div 
                    className='text-center mb-12'
                    {...scrollReveal}
                >
                    <div className='inline-block'>
                        <div className='h-1 w-32 bg-gradient-to-r from-orange-500 via-white to-green-600 rounded-full mb-6'></div>
                    </div>
                    <Text variant="h2" weight="bold" className='text-gray-900 mb-2'>
                        The Constitution of India
                    </Text>
                    <Text variant="body" className='text-gray-600'>
                        The Preamble to our Constitution
                    </Text>
                </motion.div>

                {/* Main Preamble Card */}
                <motion.div 
                    className='bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden'
                    {...scrollReveal}
                    transition={{ delay: 0.2, duration: 0.6 }}
                >
                    {/* Tricolor Top Border */}
                    <div className='h-2 bg-gradient-to-r from-orange-500 via-white to-green-600'></div>

                    {/* Content */}
                    <div className='p-8 sm:p-12'>
                        {/* Opening Line - Emphasized */}
                        <motion.div 
                            className='mb-8 text-center'
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true, amount: 0.5 }}
                            transition={{ delay: 0.3, duration: 0.5 }}
                        >
                            <Text variant="h2" className='text-3xl sm:text-4xl md:text-5xl font-bold bg-gradient-to-r from-orange-600 via-gray-800 to-green-600 bg-clip-text text-transparent leading-tight'>
                                WE, THE PEOPLE OF INDIA
                            </Text>
                        </motion.div>

                        {/* Preamble Text */}
                        <motion.div 
                            className='space-y-6 text-gray-700 text-base sm:text-lg leading-relaxed'
                            initial="initial"
                            whileInView="animate"
                            viewport={{ once: true, amount: 0.3 }}
                            variants={staggerContainer}
                        >
                            <motion.div variants={fadeInUp}>
                            <Text variant="body" className='text-center italic block'>
                                having solemnly resolved to constitute India into a
                            </Text>
                            </motion.div>

                            <motion.div variants={fadeInUp}>
                            <Text variant="h3" weight="semibold" className='text-center text-xl sm:text-2xl text-gray-900'>
                                SOVEREIGN SOCIALIST SECULAR
                                <br />
                                DEMOCRATIC REPUBLIC
                            </Text>
                            </motion.div>

                            <motion.div variants={fadeInUp}>
                            <Text variant="body" className='text-center block'>and to secure to all its citizens:</Text>
                            </motion.div>

                            {/* Key Principles */}
                            <motion.div 
                                className='grid sm:grid-cols-2 gap-6 my-8'
                                variants={staggerContainer}
                            >
                                <motion.div 
                                    className='bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200'
                                    variants={scaleIn}
                                    whileHover={{ scale: 1.05, y: -5 }}
                                    transition={quickTransition}
                                >
                                    <Text variant="h4" weight="bold" className='text-orange-900 mb-2 text-lg'>
                                        JUSTICE
                                    </Text>
                                    <Text variant="small" className='text-orange-800'>
                                        social, economic and political
                                    </Text>
                                </motion.div>

                                <motion.div 
                                    className='bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200'
                                    variants={scaleIn}
                                    whileHover={{ scale: 1.05, y: -5 }}
                                    transition={quickTransition}
                                >
                                    <Text variant="h4" weight="bold" className='text-blue-900 mb-2 text-lg'>
                                        LIBERTY
                                    </Text>
                                    <Text variant="small" className='text-blue-800'>
                                        of thought, expression, belief, faith and worship
                                    </Text>
                                </motion.div>

                                <motion.div 
                                    className='bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200'
                                    variants={scaleIn}
                                    whileHover={{ scale: 1.05, y: -5 }}
                                    transition={quickTransition}
                                >
                                    <Text variant="h4" weight="bold" className='text-purple-900 mb-2 text-lg'>
                                        EQUALITY
                                    </Text>
                                    <Text variant="small" className='text-purple-800'>
                                        of status and of opportunity
                                    </Text>
                                </motion.div>

                                <motion.div 
                                    className='bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200'
                                    variants={scaleIn}
                                    whileHover={{ scale: 1.05, y: -5 }}
                                    transition={quickTransition}
                                >
                                    <Text variant="h4" weight="bold" className='text-green-900 mb-2 text-lg'>
                                        FRATERNITY
                                    </Text>
                                    <Text variant="small" className='text-green-800'>
                                        assuring the dignity of the individual and the
                                        unity and integrity of the Nation
                                    </Text>
                                </motion.div>
                            </motion.div>

                            {/* Closing Statement */}
                            <motion.div 
                                className='text-center pt-6 border-t border-gray-200'
                                variants={fadeInUp}
                            >
                                <Text variant="small" className='text-gray-600 italic'>
                                    In our Constituent Assembly this twenty-sixth day of
                                    November, 1949,
                                    <br />
                                    do{' '}
                                    <span className='font-semibold text-gray-900'>
                                        HEREBY ADOPT, ENACT AND GIVE TO OURSELVES THIS
                                        CONSTITUTION
                                    </span>
                                </Text>
                            </motion.div>
                        </motion.div>
                    </div>

                    {/* Tricolor Bottom Border */}
                    <div className='h-2 bg-gradient-to-r from-orange-500 via-white to-green-600'></div>
                </motion.div>

                {/* Ashoka Chakra Symbol */}
                <motion.div 
                    className='text-center mt-8'
                    {...scrollReveal}
                    transition={{ delay: 0.4, duration: 0.5 }}
                >
                    <div className='inline-flex items-center justify-center w-16 h-16 rounded-full bg-white shadow-lg border-4 border-blue-800'>
                        <svg
                            className='w-12 h-12 text-blue-800'
                            viewBox='0 0 24 24'
                            fill='currentColor'>
                            <circle cx='12' cy='12' r='1.5' />
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
                                        stroke='currentColor'
                                        strokeWidth='0.5'
                                    />
                                )
                            })}
                            <circle
                                cx='12'
                                cy='12'
                                r='10'
                                fill='none'
                                stroke='currentColor'
                                strokeWidth='1'
                            />
                        </svg>
                    </div>
                    <Text variant="caption" className='text-gray-500 mt-2'>Satyameva Jayate</Text>
                </motion.div>
            </div>
        </section>
    )
}
