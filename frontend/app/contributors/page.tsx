"use client"

import { Suspense } from "react"
import Image from "next/image"
import { motion } from "framer-motion"
import { Navbar, Footer } from "@/components/layout"
import Text from "@/components/ui/Text"
import Button from "@/components/ui/Button"
import contributors from "@/data/contributors.json"

export default function ContributorsPage() {
    return (
        <Suspense>
            <ContributorsContent />
        </Suspense>
    )
}

function ContributorsContent() {
    return (
        <div className="min-h-screen bg-linear-to-b from-orange-50 via-white to-green-70  dark:from-[#070b16] dark:via-[#0b1324] dark:to-[#101a32]">
            <Navbar />

            <section className="py-20 sm:py-28">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <div className="flex items-center justify-center gap-3 text-md font-semibold text-orange-600 mb-4 uppercase tracking-wider">
                            <div className="w-8 h-0.5 border-t-2 border-orange-600" />
                            Open Source
                        </div>
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold text-[#0F1F3D] mb-6 dark:text-slate-100">
                            Our <span className="text-orange-600 italic">Contributors</span>
                        </h1>
                        <Text variant="body" className="text-gray-600 dark:text-slate-300 max-w-3xl mx-auto">
                            Rajniti is built by a passionate community. Every contribution
                            — code, data, or ideas — makes Indian democracy more transparent.
                        </Text>
                    </motion.div>

                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 ">
                        {contributors.map((c, i) => (
                            <motion.a
                                key={c.login}
                                href={c.html_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: i * 0.05 }}
                                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                                className="flex flex-col items-center gap-3 rounded-2xl border border-black/10 bg-white dark:border-gray-700 dark:bg-gray-800 p-6 text-center hover:shadow-lg transition-shadow"
                            >
                                <Image
                                    src={c.avatar_url}
                                    alt={c.login}
                                    width={80}
                                    height={80}
                                    className="rounded-full"
                                />
                                <div>
                                    <Text variant="small" weight="semibold" className="text-[#0F1F3D] truncate max-w-full">
                                        {c.login}
                                    </Text>
                                    <Text variant="caption" color="muted">
                                        {c.contributions} contribution{c.contributions !== 1 ? "s" : ""}
                                    </Text>
                                </div>
                            </motion.a>
                        ))}
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                        className="text-center mt-16 space-y-4"
                    >
                        <Text variant="h4" className="text-[#0F1F3D]">
                            Want to see your name here?
                        </Text>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <Button
                                href="https://github.com/imsks/rajniti/fork"
                                external
                                size="lg"
                                rightIcon={
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                    </svg>
                                }
                            >
                                Fork &amp; Contribute
                            </Button>
                            <Button
                                href="https://github.com/imsks/rajniti"
                                external
                                variant="secondary"
                                size="lg"
                                leftIcon={
                                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                        <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                                    </svg>
                                }
                            >
                                View on GitHub
                            </Button>
                        </div>
                    </motion.div>
                </div>
            </section>

            <Footer />
        </div>
    )
}
