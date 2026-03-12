"use client"

import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"
import Text from "@/components/ui/Text"
import Button from "@/components/ui/Button"
import MyPoliticianCard from "@/components/MyPoliticianCard"
import { useMyPoliticians } from "@/hooks/useMyPoliticians"
import { usePoliticianSearch } from "@/hooks/usePoliticianSearch"
import { useAnalytics } from "@/hooks/useAnalytics"
import {
    getCurrentPosition,
    getPincodeFromCoords,
    buildGoogleSearchUrlForMlaMp,
} from "@/lib/locationPincode"
import { getPartyInitial } from "@/lib/politicianUtils"
import type { Politician } from "@/types/politician"

const GITHUB_ISSUE_URL =
    "https://github.com/imsks/rajniti/issues/new?title=Add+MLA+MP+for+my+area&body=Request+to+add+MLA+%2F+MP+for+my+constituency.%0A%0APlease+share+constituency+name+or+pincode+if+known%3A+"

interface MyPoliticiansSectionProps {
    allPoliticians: Politician[]
}

export default function MyPoliticiansSection({
    allPoliticians,
}: MyPoliticiansSectionProps) {
    const { myMP, myMLA, setMyMP, setMyMLA } =
        useMyPoliticians(allPoliticians)
    const { trackEvent, trackSearch } = useAnalytics()
    const [searchQuery, setSearchQuery] = useState("")
    const [dropdownOpen, setDropdownOpen] = useState(false)
    const [locationLoading, setLocationLoading] = useState(false)
    const [pincodeInput, setPincodeInput] = useState("")
    const [showPincodeFallback, setShowPincodeFallback] = useState(false)
    const searchContainerRef = useRef<HTMLDivElement>(null)

    const { results, loading } = usePoliticianSearch(searchQuery)
    const showDropdown = dropdownOpen && searchQuery.trim().length >= 2

    useEffect(() => {
        trackSearch(searchQuery, "my_politicians", results.length)
    }, [searchQuery, results.length, trackSearch])
    const isEmpty = !myMP && !myMLA
    const hasAny = !!myMP || !!myMLA

    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (
                searchContainerRef.current &&
                !searchContainerRef.current.contains(e.target as Node)
            ) {
                setDropdownOpen(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])

    const handleSelectResult = (p: Politician) => {
        if (p.type === "MP") setMyMP(p)
        else setMyMLA(p)
        trackEvent('my_politician_set', { politician_id: p.id, politician_name: p.name, slot_type: p.type as "MP" | "MLA" })
        setSearchQuery("")
        setDropdownOpen(false)
    }

    const handleLocationClick = async () => {
        setLocationLoading(true)
        setShowPincodeFallback(false)
        const pos = await getCurrentPosition()
        if (pos) {
            const pincode = await getPincodeFromCoords(pos.lat, pos.lon)
            if (pincode) {
                trackEvent('location_lookup', { method: 'gps', success: true })
                window.open(buildGoogleSearchUrlForMlaMp(pincode), "_blank")
            } else {
                trackEvent('location_lookup', { method: 'gps', success: false })
                setPincodeInput("")
                setShowPincodeFallback(true)
            }
        } else {
            trackEvent('location_lookup', { method: 'gps', success: false })
            setPincodeInput("")
            setShowPincodeFallback(true)
        }
        setLocationLoading(false)
    }

    const handlePincodeSubmit = () => {
        const value = pincodeInput.trim()
        if (value) {
            trackEvent('location_lookup', { method: 'pincode', success: true })
            window.open(buildGoogleSearchUrlForMlaMp(value), "_blank")
            setPincodeInput("")
            setShowPincodeFallback(false)
        }
    }

    const focusSearch = () => {
        const el = document.getElementById("my-politicians-search")
        if (el) {
            el.focus()
            setDropdownOpen(true)
        }
    }

    return (
        <motion.section
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className='mb-10 rounded-2xl bg-gradient-to-br from-amber-50/80 via-orange-50/40 to-amber-50/60 dark:from-gray-800/80 dark:via-gray-800/40 dark:to-gray-800/60 border border-amber-200/60 dark:border-gray-700 shadow-sm overflow-hidden'
        >
            <div className='p-6 sm:p-8'>
                <div className='mb-4'>
                    <div className='inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100/80 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 text-xs font-semibold uppercase tracking-wide mb-3'>
                        Your dashboard
                    </div>
                    <Text
                        variant='h2'
                        weight='bold'
                        className='text-gray-900 dark:text-white mb-1'
                    >
                        {isEmpty
                            ? "Add Your Local Politicians"
                            : "Your Politicians"}
                    </Text>
                    <Text variant='body' className='text-gray-600 dark:text-gray-400'>
                        {isEmpty
                            ? "Track their performance and know their progress"
                            : "Analyse their performance"}
                    </Text>
                </div>

            <div ref={searchContainerRef} className='relative mb-6'>
                <div className='relative'>
                    <span className='absolute left-3 top-1/2 -translate-y-1/2 text-gray-400'>
                        <img
                            src='/logo/search.png'
                            alt='Search'
                            className='w-5 h-5'
                        />
                    </span>
                    <input
                        id='my-politicians-search'
                        type='text'
                        value={searchQuery}
                        onChange={(e) => {
                            setSearchQuery(e.target.value)
                            setDropdownOpen(true)
                        }}
                        onFocus={() =>
                            searchQuery.trim().length >= 2 && setDropdownOpen(true)
                        }
                        placeholder='Find your MP or MLA, e.g. Modi'
                        className='w-full pl-10 pr-4 py-3 border border-amber-200 dark:border-gray-600 rounded-lg bg-white/80 dark:bg-gray-700/80 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-amber-400 dark:focus:ring-orange-500 focus:border-amber-300 dark:focus:border-orange-500'
                    />
                </div>
                {showDropdown && (
                    <div className='absolute z-20 left-0 right-0 top-full mt-1 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 max-h-80 overflow-auto'>
                        {loading ? (
                            <div className='px-4 py-6 text-center text-gray-500 dark:text-gray-400 text-sm'>
                                Searching...
                            </div>
                        ) : results.length === 0 ? (
                            <div className='px-4 py-3'>
                                <p className='text-gray-500 dark:text-gray-400 text-sm mb-1'>
                                    Not found? Some MLAs may not be in our dataset yet.
                                </p>
                                <div className='flex flex-wrap items-center gap-x-3 gap-y-1'>
                                    <a
                                        href={GITHUB_ISSUE_URL}
                                        target='_blank'
                                        rel='noopener noreferrer'
                                        className='text-orange-600 hover:underline text-sm font-medium'
                                    >
                                        Request addition →
                                    </a>
                                    <span className='text-gray-300 text-sm'>|</span>
                                    <a
                                        href='https://github.com/imsks/rajniti#-contributing-with-ai'
                                        target='_blank'
                                        rel='noopener noreferrer'
                                        className='text-gray-500 hover:text-orange-600 hover:underline text-xs'
                                    >
                                        Dev? Run the state agent & open a PR
                                    </a>
                                </div>
                            </div>
                        ) : (
                            <ul className='divide-y divide-gray-100 dark:divide-gray-700'>
                                {results.map((p) => (
                                    <li key={p.id}>
                                        <button
                                            type='button'
                                            onClick={() => handleSelectResult(p)}
                                            className='w-full px-4 py-3 flex items-center gap-3 hover:bg-orange-50 dark:hover:bg-gray-700 text-left transition-colors'
                                        >
                                            {p.photo ? (
                                                <img
                                                    src={p.photo}
                                                    alt=''
                                                    className='w-10 h-10 rounded-full object-cover border border-gray-200 dark:border-gray-600'
                                                />
                                            ) : (
                                                <div className='w-10 h-10 rounded-full bg-gradient-to-br from-orange-100 to-orange-200 dark:from-orange-900/40 dark:to-orange-800/40 flex items-center justify-center border border-orange-200 dark:border-orange-700'>
                                                    <span className='text-orange-700 font-bold text-xs'>
                                                        {getPartyInitial(p)}
                                                    </span>
                                                </div>
                                            )}
                                            <div className='flex-1 min-w-0'>
                                                <p className='font-medium text-gray-900 dark:text-gray-100 truncate'>
                                                    {p.name}
                                                </p>
                                                <p className='text-xs text-gray-500 dark:text-gray-400 truncate'>
                                                    {p.type} · {p.constituency}
                                                </p>
                                            </div>
                                            <span
                                                className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                                                    p.type === "MP"
                                                        ? "bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                                                        : "bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300"
                                                }`}
                                            >
                                                {p.type}
                                            </span>
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                )}
            </div>

            <div className='grid grid-cols-1 md:grid-cols-2 gap-5 mb-6'>
                <MyPoliticianCard
                    politician={myMP}
                    slotType='MP'
                    onAddClick={focusSearch}
                    onRemove={myMP ? () => { setMyMP(null); trackEvent('my_politician_remove', { slot_type: 'MP' }) } : undefined}
                />
                <MyPoliticianCard
                    politician={myMLA}
                    slotType='MLA'
                    onAddClick={focusSearch}
                    onRemove={myMLA ? () => { setMyMLA(null); trackEvent('my_politician_remove', { slot_type: 'MLA' }) } : undefined}
                />
            </div>

            <div className='border-t border-amber-200/60 dark:border-gray-700 pt-4'>
                <Text variant='small' className='text-gray-600 dark:text-gray-400 mb-2'>
                    Don&apos;t know your MLA or MP?
                </Text>
                {!showPincodeFallback ? (
                    <Button
                        variant='outline'
                        size='sm'
                        onClick={handleLocationClick}
                        isLoading={locationLoading}
                    >
                        Use location to find by pincode
                    </Button>
                ) : (
                    <div className='flex flex-wrap items-center gap-2'>
                        <input
                            type='text'
                            value={pincodeInput}
                            onChange={(e) => setPincodeInput(e.target.value)}
                            placeholder='Enter pincode'
                            className='px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-orange-500 max-w-[140px]'
                        />
                        <Button
                            variant='primary'
                            size='sm'
                            onClick={handlePincodeSubmit}
                        >
                            Search on Google
                        </Button>
                        <button
                            type='button'
                            onClick={() => setShowPincodeFallback(false)}
                            className='text-sm text-gray-500 hover:underline'
                        >
                            Cancel
                        </button>
                    </div>
                )}
                <p className='text-xs text-gray-500 dark:text-gray-400 mt-3'>
                    Can&apos;t find your MLA? Data for some states is still being added.{" "}
                    <a
                        href='https://github.com/imsks/rajniti#-contributing-with-ai'
                        target='_blank'
                        rel='noopener noreferrer'
                        className='text-orange-600 hover:underline'
                    >
                        Developers can help&nbsp;&rarr;
                    </a>
                </p>
            </div>
            </div>
        </motion.section>
    )
}
