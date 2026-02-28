"use client"

import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"
import Text from "@/components/ui/Text"
import Button from "@/components/ui/Button"
import MyPoliticianCard from "@/components/MyPoliticianCard"
import { useMyPoliticians } from "@/hooks/useMyPoliticians"
import { usePoliticianSearch } from "@/hooks/usePoliticianSearch"
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
    const [searchQuery, setSearchQuery] = useState("")
    const [dropdownOpen, setDropdownOpen] = useState(false)
    const [locationLoading, setLocationLoading] = useState(false)
    const [pincodeInput, setPincodeInput] = useState("")
    const [showPincodeFallback, setShowPincodeFallback] = useState(false)
    const searchContainerRef = useRef<HTMLDivElement>(null)

    const { results, loading } = usePoliticianSearch(searchQuery)
    const showDropdown = dropdownOpen && searchQuery.trim().length >= 2
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
                window.open(buildGoogleSearchUrlForMlaMp(pincode), "_blank")
            } else {
                setPincodeInput("")
                setShowPincodeFallback(true)
            }
        } else {
            setPincodeInput("")
            setShowPincodeFallback(true)
        }
        setLocationLoading(false)
    }

    const handlePincodeSubmit = () => {
        const value = pincodeInput.trim()
        if (value) {
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
            className='mb-10 rounded-2xl bg-gradient-to-br from-amber-50/80 via-orange-50/40 to-amber-50/60 border border-amber-200/60 shadow-sm overflow-hidden'
        >
            <div className='p-6 sm:p-8'>
                <div className='mb-4'>
                    <div className='inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-100/80 text-amber-800 text-xs font-semibold uppercase tracking-wide mb-3'>
                        Your dashboard
                    </div>
                    <Text
                        variant='h2'
                        weight='bold'
                        className='text-gray-900 mb-1'
                    >
                        {isEmpty
                            ? "Add Your Local Politicians"
                            : "Your Politicians"}
                    </Text>
                    <Text variant='body' className='text-gray-600'>
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
                        className='w-full pl-10 pr-4 py-3 border border-amber-200 rounded-lg bg-white/80 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-300'
                    />
                </div>
                {showDropdown && (
                    <div className='absolute z-20 left-0 right-0 top-full mt-1 bg-white rounded-lg shadow-lg border border-gray-200 py-2 max-h-80 overflow-auto'>
                        {loading ? (
                            <div className='px-4 py-6 text-center text-gray-500 text-sm'>
                                Searching...
                            </div>
                        ) : results.length === 0 ? (
                            <div className='px-4 py-3'>
                                <p className='text-gray-500 text-sm mb-2'>
                                    Not found? Help us add them
                                </p>
                                <a
                                    href={GITHUB_ISSUE_URL}
                                    target='_blank'
                                    rel='noopener noreferrer'
                                    className='text-orange-600 hover:underline text-sm font-medium'
                                >
                                    Contribute →
                                </a>
                            </div>
                        ) : (
                            <ul className='divide-y divide-gray-100'>
                                {results.map((p) => (
                                    <li key={p.id}>
                                        <button
                                            type='button'
                                            onClick={() => handleSelectResult(p)}
                                            className='w-full px-4 py-3 flex items-center gap-3 hover:bg-orange-50 text-left transition-colors'
                                        >
                                            {p.photo ? (
                                                <img
                                                    src={p.photo}
                                                    alt=''
                                                    className='w-10 h-10 rounded-full object-cover border border-gray-200'
                                                />
                                            ) : (
                                                <div className='w-10 h-10 rounded-full bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center border border-orange-200'>
                                                    <span className='text-orange-700 font-bold text-xs'>
                                                        {getPartyInitial(p)}
                                                    </span>
                                                </div>
                                            )}
                                            <div className='flex-1 min-w-0'>
                                                <p className='font-medium text-gray-900 truncate'>
                                                    {p.name}
                                                </p>
                                                <p className='text-xs text-gray-500 truncate'>
                                                    {p.type} · {p.constituency}
                                                </p>
                                            </div>
                                            <span
                                                className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                                                    p.type === "MP"
                                                        ? "bg-blue-100 text-blue-700"
                                                        : "bg-purple-100 text-purple-700"
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
                    onRemove={myMP ? () => setMyMP(null) : undefined}
                />
                <MyPoliticianCard
                    politician={myMLA}
                    slotType='MLA'
                    onAddClick={focusSearch}
                    onRemove={myMLA ? () => setMyMLA(null) : undefined}
                />
            </div>

            <div className='border-t border-amber-200/60 pt-4'>
                <Text variant='small' className='text-gray-600 mb-2'>
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
                            className='px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 max-w-[140px]'
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
            </div>
            </div>
        </motion.section>
    )
}
