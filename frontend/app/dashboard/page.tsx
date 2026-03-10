"use client"

import { Suspense, useState, useMemo, useEffect } from "react"
import { motion } from "framer-motion"
import { Footer, Navbar } from "@/components/layout"
import Button from "@/components/ui/Button"
import Text from "@/components/ui/Text"
import PoliticianCard from "@/components/PoliticianCard"
import PoliticianCardWrapper from "@/components/PoliticianCardWrapper"
import MyPoliticiansSection from "@/components/MyPoliticiansSection"
import { usePoliticians } from "@/hooks/usePoliticians"
import { useAnalytics } from "@/hooks/useAnalytics"
type Tab = "ALL" | "MP" | "MLA"

export default function Dashboard() {
    return (
        <Suspense fallback={
            <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900 flex items-center justify-center'>
                <div className='inline-block animate-spin rounded-full h-12 w-12 border-4 border-orange-500 border-t-transparent'></div>
            </div>
        }>
            <DashboardContent />
        </Suspense>
    )
}

function DashboardContent() {
    const [activeTab, setActiveTab] = useState<Tab>("ALL")
    const [searchQuery, setSearchQuery] = useState("")
    const [stateFilter, setStateFilter] = useState("")
    const [partyFilter, setPartyFilter] = useState("")
    const [currentPage, setCurrentPage] = useState(1)
    const [itemsPerPage, setItemsPerPage] = useState(12)
    const { trackEvent, trackSearch } = useAnalytics()

    // One API call for all politicians; filter client-side by tab + search/filters
const { all, loading, error, states, parties, stats, filter } =
    usePoliticians()


    // Filtered list — pure client-side (type from tab + query, state, party)
    const displayPoliticians = useMemo(() => {
        let list = filter({
            query: searchQuery,
            state: stateFilter,
            party: partyFilter,
        })
        if (activeTab === "MP") list = list.filter((p) => p.type === "MP")
        else if (activeTab === "MLA") list = list.filter((p) => p.type === "MLA")
        return list
    }, [filter, searchQuery, stateFilter, partyFilter, activeTab])

    // Pagination calculations
    const totalPages = Math.ceil(displayPoliticians.length / itemsPerPage)
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    const paginatedPoliticians = displayPoliticians.slice(startIndex, endIndex)

    // Reset to page 1 when filters change
    useMemo(() => {
        setCurrentPage(1)
    }, [searchQuery, stateFilter, partyFilter, activeTab, itemsPerPage])

    // Scroll to top when page changes
    useEffect(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }, [currentPage])

    // Debounced search tracking
    useEffect(() => {
        trackSearch(searchQuery, "dashboard", displayPoliticians.length)
    }, [searchQuery, trackSearch, displayPoliticians.length])

    const hasActiveFilters = !!(searchQuery || stateFilter || partyFilter)

    // ── Render ────────────────────────────────────────────────────────────

    useEffect(() => {
        if (error) trackEvent('error_view', { error_type: 'connection', error_message: error, page_location: 'dashboard' })
    }, [error, trackEvent])

    if (error) {
        return (
            <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900 flex items-center justify-center p-4'>
                <div className='bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-md w-full border-l-4 border-red-500'>
                    <div className='flex items-center gap-3 mb-4'>
                        <div className='text-red-500 text-3xl'>⚠️</div>
                        <Text variant='h4' weight='bold' className='text-gray-900 dark:text-white'>
                            Connection Error
                        </Text>
                    </div>
                    <Text variant='body' className='text-gray-600 dark:text-gray-400 mb-4'>
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
        <div className='min-h-screen bg-gradient-to-b from-orange-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-gray-900'>
            <Navbar variant='dashboard' sticky={true} />

            <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8'>
                {/* Your Politicians (MP + MLA slots) */}
                <MyPoliticiansSection allPoliticians={all} />

                {/* Header + Stats */}
                <motion.div 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className='mb-8'>
                    <Text variant='h2' weight='bold' className='text-gray-900 dark:text-white mb-2'>
                        <span className='text-orange-600'>Indian</span>  Politicians
                    </Text>
                    <Text variant='body' className='text-gray-600 dark:text-gray-400 mb-6'>
                        Browse elected MPs and MLAs. Help us enrich their profiles!
                    </Text>

                    {!loading && (
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                            className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-6'>
                            <StatCard
                                value={stats.total.toLocaleString()}
                                label='Total Politicians'
                                color='text-orange-600'
                            />
                            <StatCard
                                value={stats.totalStates.toString()}
                                label='States / UTs'
                                color='text-[#1E40AF]'
                            />
                            <StatCard
                                value={stats.totalParties.toString()}
                                label='Parties'
                                color='text-green-800'
                            />
                            <StatCard
                                value={stats.topParty}
                                label='Top Party'
                                color='text-[#1E40AF] '
                            />
                        </motion.div>
                    )}
                </motion.div>

                {/* Tabs */}
                <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                    className='flex gap-2 mb-6'>
                    {(["ALL", "MP", "MLA"] as Tab[]).map((tab, i) => (
                        <motion.button
                            key={tab}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.4, delay: 0.4 + i * 0.1 }}
                            onClick={() => {
                                setActiveTab(tab)
                                setSearchQuery("")
                                setStateFilter("")
                                setPartyFilter("")
                                trackEvent('filter_apply', { filter_type: 'tab', filter_value: tab })
                            }}
                            className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all ${
                                activeTab === tab
                                    ? "bg-orange-500 text-white shadow-md"
                                    : "bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:border-orange-400 dark:hover:border-orange-500 hover:text-orange-600 dark:hover:text-orange-400"
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
                <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.6 }}
                    className='bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6'>
                    <div className='flex flex-col md:flex-row gap-3'>
                        {/* Search input */}
                        <div className='flex-1 relative'>
                            <span className='absolute left-3 top-1/2 -translate-y-1/2 text-gray-400'>
                                <img
                                    src='/logo/search.png'
                                    alt='Search'
                                    className='w-5 h-5'
                                />
                            </span>
                            <input
                                type='text'
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder='Search by name, constituency, state or party...'
                                className='w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent'
                            />
                        </div>

                        {/* State filter */}
                        <select
                            value={stateFilter}
                            onChange={(e) => {
                                setStateFilter(e.target.value)
                                if (e.target.value) trackEvent('filter_apply', { filter_type: 'state', filter_value: e.target.value })
                            }}
                            className='px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500 min-w-[180px]'>
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
                            onChange={(e) => {
                                setPartyFilter(e.target.value)
                                if (e.target.value) trackEvent('filter_apply', { filter_type: 'party', filter_value: e.target.value })
                            }}
                            className='px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500 min-w-[180px]'>
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
                        <div className='flex items-center gap-2 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700'>
                            <Text variant='small' className='text-gray-500 dark:text-gray-400'>
                                Showing {displayPoliticians.length.toLocaleString()} result
                                {displayPoliticians.length !== 1 ? "s" : ""}
                            </Text>
                            <button
                                onClick={() => {
                                    setSearchQuery("")
                                    setStateFilter("")
                                    setPartyFilter("")
                                    trackEvent('filter_clear', {})
                                }}
                                className='ml-2 text-xs text-orange-600 hover:underline'>
                                Clear filters
                            </button>
                        </div>
                    )}
                </motion.div>

                {/* Loading state */}
               {loading && (
    <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5'>
        {Array.from({ length: 12 }).map((_, i) => (
            <PoliticianCardWrapper key={i} loading={true} />
        ))}
    </div>
)}

                {/* Empty state */}
                {!loading && displayPoliticians.length === 0 && (
                    <div className='text-center py-20'>
                        <div className='text-6xl mb-4'>🔍</div>
                        <Text variant='h4' weight='bold' className='text-gray-700 dark:text-gray-200 mb-2'>
                            No politicians found
                        </Text>
                        <Text variant='body' className='text-gray-500 dark:text-gray-400'>
                            {hasActiveFilters
                                ? "Try adjusting your search or filters."
                                : "No data available yet."}
                        </Text>
                    </div>
                )}

                {/* Politician grid */}
                {!loading && displayPoliticians.length > 0 && (
                    <>
                        {/* Results info and items per page selector */}
                        <div className='flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6'>
                            <Text variant='body' className='text-gray-600 dark:text-gray-400'>
                                Showing {startIndex + 1}-{Math.min(endIndex, displayPoliticians.length)} of {displayPoliticians.length} politicians
                            </Text>
                            <div className='flex items-center gap-2'>
                                <Text variant='body' className='text-gray-600 dark:text-gray-400 text-sm'>
                                    Show:
                                </Text>
                                <select
                                    value={itemsPerPage}
                                    onChange={(e) => {
                                        const val = Number(e.target.value)
                                        setItemsPerPage(val)
                                        trackEvent('filter_apply', { filter_type: 'items_per_page', filter_value: String(val) })
                                    }}
                                    className='px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200'>
                                    <option value={12}>12</option>
                                    <option value={24}>24</option>
                                    <option value={48}>48</option>
                                    <option value={96}>96</option>
                                </select>
                                <Text variant='body' className='text-gray-600 dark:text-gray-400 text-sm'>
                                    per page
                                </Text>
                            </div>
                        </div>

                        <motion.div 
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ duration: 0.5 }}
                            className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5'>
                            {paginatedPoliticians.map((p, i) => (
                                <motion.div
                                    key={p.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.4, delay: i * 0.05 }}
                                >
                                    <PoliticianCard politician={p} />
                                </motion.div>
                            ))}
                        </motion.div>

                        {/* Pagination controls */}
                        {totalPages > 1 && (
                            <div className='flex justify-center items-center gap-2 mt-8'>
                                <button
                                    onClick={() => {
                                        const newPage = Math.max(1, currentPage - 1)
                                        setCurrentPage(newPage)
                                        trackEvent('pagination', { direction: 'previous', page_number: newPage, total_pages: totalPages })
                                    }}
                                    disabled={currentPage === 1}
                                    className='px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors'>
                                    Previous
                                </button>

                                <button
                                    onClick={() => {
                                        const newPage = Math.min(totalPages, currentPage + 1)
                                        setCurrentPage(newPage)
                                        trackEvent('pagination', { direction: 'next', page_number: newPage, total_pages: totalPages })
                                    }}
                                    disabled={currentPage === totalPages}
                                    className='px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors'>
                                    Next
                                </button>
                            </div>
                        )}
                    </>
                )}

                {/* Contribute CTA */}
                <motion.div 
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className='mt-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-2xl p-8 text-center text-white'>
                    <Text variant='h3' weight='bold' className='text-white mb-2'>
                        Help us build the most comprehensive politician database
                    </Text>
                    <Text variant='body' className='text-orange-100 mb-6 max-w-2xl mx-auto'>
                        Many profiles are missing education, family, and criminal record
                        details. You can contribute by enriching profiles or reporting
                        inaccuracies.
                    </Text>
                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <Button
                            href='https://github.com/imsks/rajniti/issues/new'
                            external
                            onClick={() => trackEvent('contribute_click', { contribute_type: 'data', page_location: 'dashboard_cta' })}
                            className='bg-white text-orange-600 py-2 px-4 rounded-lg font-semibold border-none shadow-lg'
                            size='lg'>
                            Contribute on GitHub →
                        </Button>
                    </motion.div>
                </motion.div>
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
        <motion.div 
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
            className='bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm'>
            <Text variant='h3' weight='bold' className={color}>
                {value}
            </Text>
            <Text variant='small' className='text-gray-500 dark:text-gray-400'>
                {label}
            </Text>
        </motion.div>
    )
}
