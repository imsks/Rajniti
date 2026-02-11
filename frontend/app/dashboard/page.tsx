"use client"

import { useState, useMemo } from "react"
import { motion } from "framer-motion"
import { Footer, Navbar } from "@/components/layout"
import Button from "@/components/ui/Button"
import Text from "@/components/ui/Text"
import PoliticianCard from "@/components/PoliticianCard"
import { usePoliticians } from "@/hooks/usePoliticians"
import type { ElectionType } from "@/types/politician"
import { fadeInUp, staggerContainer, staggerFastContainer, buttonTap, scaleIn, quickTransition } from "@/utils/motion"

type Tab = "ALL" | "MP" | "MLA"

export default function Dashboard() {
    const [activeTab, setActiveTab] = useState<Tab>("ALL")
    const [searchQuery, setSearchQuery] = useState("")
    const [stateFilter, setStateFilter] = useState("")
    const [partyFilter, setPartyFilter] = useState("")

    // One API call — everything else derived client-side
    const typeParam: ElectionType | undefined =
        activeTab === "ALL" ? undefined : activeTab

    const { all, loading, error, states, parties, stats, filter } =
        usePoliticians(typeParam)

    // Filtered list — pure client-side
    const displayPoliticians = useMemo(
        () => filter({ query: searchQuery, state: stateFilter, party: partyFilter }),
        [filter, searchQuery, stateFilter, partyFilter]
    )

    const hasActiveFilters = !!(searchQuery || stateFilter || partyFilter)

    // ── Render ────────────────────────────────────────────────────────────

    if (error) {
        return (
            <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 flex items-center justify-center p-4'>
                <div className='bg-white rounded-lg shadow-lg p-8 max-w-md w-full border-l-4 border-red-500'>
                    <div className='flex items-center gap-3 mb-4'>
                        <div className='text-red-500 text-3xl'>⚠️</div>
                        <Text variant='h4' weight='bold' className='text-gray-900'>
                            Connection Error
                        </Text>
                    </div>
                    <Text variant='body' className='text-gray-600 mb-4'>
                        {error}
                    </Text>
                    <Button onClick={() => window.location.reload()} fullWidth>
                        Try Again
                    </Button>
                </div>
            </div>
        )
    }

    return (
        <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50'>
            <Navbar variant='dashboard' sticky={true} />

            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8'>
                {/* Header + Stats */}
                <motion.div 
                    className='mb-8'
                    initial="initial"
                    animate="animate"
                    variants={staggerContainer}
                >
                    <motion.div variants={fadeInUp}>
                    <Text variant='h2' weight='bold' className='text-gray-900 mb-2'>
                        Indian Politicians
                    </Text>
                    <Text variant='body' className='text-gray-600 mb-6'>
                        Browse elected MPs and MLAs. Help us enrich their profiles!
                    </Text>
                    </motion.div>

                    {!loading && (
                        <motion.div 
                            className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-6'
                            variants={staggerContainer}
                        >
                            <StatCard
                                value={stats.total.toLocaleString()}
                                label='Total Politicians'
                                color='text-orange-600'
                            />
                            </motion.div>
                            <motion.div variants={fadeInUp}>
                            <StatCard
                                value={stats.totalStates.toString()}
                                label='States / UTs'
                                color='text-blue-600'
                            />
                            </motion.div>
                            <motion.div variants={fadeInUp}>
                            <StatCard
                                value={stats.totalParties.toString()}
                                label='Parties'
                                color='text-green-600'
                            />
                            </motion.div>
                            <motion.div variants={fadeInUp}>
                            <StatCard
                                value={stats.topParty}
                                label='Top Party'
                                color='text-purple-600'
                            />
                            </motion.div>
                        </motion.div>
                    )}
                </motion.div>

                {/* Tabs */}
                <motion.div 
                    className='flex gap-2 mb-6'
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    {(["ALL", "MP", "MLA"] as Tab[]).map((tab) => (
                        <motion.button
                            key={tab}
                            whileTap={buttonTap}
                            whileHover={{ scale: 1.05 }}
                            transition={quickTransition}
                            onClick={() => {
                                setActiveTab(tab)
                                setSearchQuery("")
                                setStateFilter("")
                                setPartyFilter("")
                            }}
                            className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all ${
                                activeTab === tab
                                    ? "bg-orange-500 text-white shadow-md"
                                    : "bg-white text-gray-600 border border-gray-300 hover:border-orange-400 hover:text-orange-600"
                            }`}>
                            {tab === "ALL"
                                ? "All"
                                : tab === "MP"
                                  ? "MPs"
                                  : "MLAs"}
                        </motion.button>
                    ))}
                </motion.div>

                {/* Search + Filters */}
                <div className='bg-white rounded-2xl shadow-sm border border-gray-200 p-4 mb-6'>
                    <div className='flex flex-col md:flex-row gap-3'>
                        {/* Search input */}
                        <div className='flex-1 relative'>
                            <span className='absolute left-3 top-1/2 -translate-y-1/2 text-gray-400'>
                                🔍
                            </span>
                            <input
                                type='text'
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder='Search by name, constituency, state or party...'
                                className='w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent'
                            />
                        </div>

                        {/* State filter */}
                        <select
                            value={stateFilter}
                            onChange={(e) => setStateFilter(e.target.value)}
                            className='px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-orange-500 min-w-[180px]'>
                            <option value=''>All States</option>
                            {states.map((s) => (
                                <option key={s} value={s}>
                                    {s}
                                </option>
                            ))}
                        </select>

                        {/* Party filter */}
                        <select
                            value={partyFilter}
                            onChange={(e) => setPartyFilter(e.target.value)}
                            className='px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-orange-500 min-w-[180px]'>
                            <option value=''>All Parties</option>
                            {parties.map((p) => (
                                <option key={p} value={p}>
                                    {p}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Active filters summary */}
                    {hasActiveFilters && (
                        <div className='flex items-center gap-2 mt-3 pt-3 border-t border-gray-100'>
                            <Text variant='small' className='text-gray-500'>
                                Showing {displayPoliticians.length.toLocaleString()} result
                                {displayPoliticians.length !== 1 ? "s" : ""}
                            </Text>
                            <button
                                onClick={() => {
                                    setSearchQuery("")
                                    setStateFilter("")
                                    setPartyFilter("")
                                }}
                                className='ml-2 text-xs text-orange-600 hover:underline'>
                                Clear filters
                            </button>
                        </div>
                    )}
                </div>

                {/* Loading state */}
                {loading && (
                    <div className='flex items-center justify-center py-20'>
                        <div className='text-center'>
                            <div className='inline-block animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent'></div>
                            <p className='mt-4 text-gray-600 font-semibold'>
                                Loading politicians...
                            </p>
                        </div>
                    </div>
                )}

                {/* Empty state */}
                {!loading && displayPoliticians.length === 0 && (
                    <div className='text-center py-20'>
                        <div className='text-6xl mb-4'>🔍</div>
                        <Text variant='h4' weight='bold' className='text-gray-700 mb-2'>
                            No politicians found
                        </Text>
                        <Text variant='body' className='text-gray-500'>
                            {hasActiveFilters
                                ? "Try adjusting your search or filters."
                                : "No data available yet."}
                        </Text>
                    </div>
                )}

                {/* Politician grid */}
                {!loading && displayPoliticians.length > 0 && (
                    <motion.div 
                        className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5'
                        initial="initial"
                        animate="animate"
                        variants={staggerFastContainer}
                    >
                        {displayPoliticians.map((p, index) => (
                            <motion.div key={p.id} variants={scaleIn}>
                                <PoliticianCard politician={p} />
                            </motion.div>
                        ))}
                    </motion.div>
                )}

                {/* Contribute CTA */}
                <div className='mt-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl p-8 text-center text-white'>
                    <Text variant='h3' weight='bold' className='text-white mb-2'>
                        Help us build the most comprehensive politician database
                    </Text>
                    <Text variant='body' className='text-orange-100 mb-6 max-w-2xl mx-auto'>
                        Many profiles are missing education, family, and criminal record
                        details. You can contribute by enriching profiles or reporting
                        inaccuracies.
                    </Text>
                    <Button
                        href='https://github.com/imsks/rajniti/issues/new'
                        external
                        className='bg-white text-orange-600 hover:bg-gray-50 border-none shadow-lg'
                        size='lg'>
                        Contribute on GitHub →
                    </Button>
                </div>
            </div>

            <Footer />
        </div>
    )
}

// ── Tiny helper component ─────────────────────────────────────────────────

function StatCard({
    value,
    label,
    color,
}: {
    value: string
    label: string
    color: string
}) {
    return (
        <div className='bg-white rounded-xl p-4 border border-gray-200 shadow-sm'>
            <Text variant='h3' weight='bold' className={color}>
                {value}
            </Text>
            <Text variant='small' className='text-gray-500'>
                {label}
            </Text>
        </div>
    )
}
