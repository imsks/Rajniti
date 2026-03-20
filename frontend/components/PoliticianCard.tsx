"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import Text from "@/components/ui/Text"
import Image from "@/components/ui/Image"
import { useAnalytics } from "@/hooks/useAnalytics"
import type { Politician } from "@/types/politician"

interface PoliticianCardProps {
    politician: Politician
}

/** Get the latest (first) party name from political background */
function getParty(p: Politician): string {
    const elections = p.political_background?.elections ?? []
    return elections.length > 0 ? elections[0].party : "—"
}

/** A short party abbreviation for the avatar */
function getPartyInitial(p: Politician): string {
    const party = getParty(p)
    if (party === "—") return "?"
    // Use first letters of major words
    const words = party.split(" ").filter((w) => w.length > 2)
    return words
        .slice(0, 3)
        .map((w) => w[0])
        .join("")
        .toUpperCase()
}

export default function PoliticianCard({ politician }: PoliticianCardProps) {
    const party = getParty(politician)
    const initial = getPartyInitial(politician)
    const isMp = politician.type === "MP"
    const hasPhoto = !!politician.photo
    const { trackEvent } = useAnalytics()
    const politicianUrlSlugOrId = politician.slug ?? politician.id

    return (
        <Link
            href={`/politician/${encodeURIComponent(politicianUrlSlugOrId)}`}
            className='block group'
            onClick={() => trackEvent('politician_card_click', {
                politician_id: politician.id,
                politician_name: politician.name,
                politician_type: politician.type as "MP" | "MLA",
                party,
                state: politician.state,
            })}>
            <motion.div 
                whileHover={{ y: -4, scale: 1.02 }}
                transition={{ duration: 0.2 }}
                className='bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 hover:border-orange-400 dark:hover:border-orange-500 hover:shadow-lg transition-all h-full flex flex-col'>
                {/* Top: Photo / Avatar + Name */}
                <div className='flex items-start gap-4 mb-3'>
                    {hasPhoto ? (
                        <Image
                            src={politician.photo!}
                            alt={politician.name}
                            width={56}
                            height={56}
                            rounded='full'
                            className='w-14 h-14 object-cover border-2 border-orange-200 flex-shrink-0'
                        />
                    ) : (
                        <div className='w-14 h-14 rounded-full bg-gradient-to-br from-orange-100 to-orange-200 dark:from-orange-900/40 dark:to-orange-800/40 flex items-center justify-center flex-shrink-0 border-2 border-orange-200 dark:border-orange-700'>
                            <span className='text-orange-700 font-bold text-xs'>
                                {initial}
                            </span>
                        </div>
                    )}

                    <div className='flex-1 min-w-0'>
                        <Text
                            variant='body'
                            weight='bold'
                            className='text-gray-900 dark:text-gray-100 truncate'>
                            {politician.name}
                        </Text>
                        <Text variant='small' className='text-gray-500 dark:text-gray-400 truncate'>
                            {party}
                        </Text>
                    </div>

                    {/* Type badge */}
                    <span
                        className={`px-2.5 py-1 rounded-full text-xs font-bold flex-shrink-0 ${
                            isMp
                                ? "bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                                : "bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300"
                        }`}>
                        {politician.type}
                    </span>
                </div>

                {/* Info pills */}
                <div className='flex flex-wrap gap-2 mb-3'>
                    <span className='inline-flex items-center gap-1 px-2.5 py-1 bg-gray-50 dark:bg-gray-700 rounded-lg text-xs text-gray-600 dark:text-gray-300'>
                        <img src='/logo/location.png' alt='Constituency' className='w-4 h-4' /> {politician.constituency}
                    </span>
                    <span className='inline-flex items-center gap-1 px-2.5 py-1 bg-gray-50 dark:bg-gray-700 rounded-lg text-xs text-gray-600 dark:text-gray-300'>
                        <img src='/logo/skyline.png' alt='State' className='w-4 h-4' /> {politician.state}
                    </span>
                </div>

                {/* CTA Button - Always visible */}
                <div className='mt-auto pt-3 border-t border-gray-100 dark:border-gray-700'>
                    <div className='flex items-center justify-between text-orange-600 group-hover:text-orange-700 transition-colors'>
                        <Text variant='small' weight='semibold'>
                            View Details
                        </Text>
                        <span className='transform group-hover:translate-x-1 transition-transform'>→</span>
                    </div>
                </div>
            </motion.div>
        </Link>
    )
}
