"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import Text from "@/components/ui/Text"
import Image from "@/components/ui/Image"
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
    console.log(politician)

    return (
        <Link
            href={`/politician/${encodeURIComponent(politician.id)}`}
            className='block group'>
            <motion.div 
                whileHover={{ y: -4, scale: 1.02 }}
                transition={{ duration: 0.2 }}
                className='bg-white rounded-2xl shadow-sm border border-gray-200 p-5 hover:border-orange-400 hover:shadow-lg transition-all h-full flex flex-col'>
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
                        <div className='w-14 h-14 rounded-full bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center flex-shrink-0 border-2 border-orange-200'>
                            <span className='text-orange-700 font-bold text-xs'>
                                {initial}
                            </span>
                        </div>
                    )}

                    <div className='flex-1 min-w-0'>
                        <Text
                            variant='body'
                            weight='bold'
                            className='text-gray-900 truncate'>
                            {politician.name}
                        </Text>
                        <Text variant='small' className='text-gray-500 truncate'>
                            {party}
                        </Text>
                    </div>

                    {/* Type badge */}
                    <span
                        className={`px-2.5 py-1 rounded-full text-xs font-bold flex-shrink-0 ${
                            isMp
                                ? "bg-blue-100 text-blue-700"
                                : "bg-purple-100 text-purple-700"
                        }`}>
                        {politician.type}
                    </span>
                </div>

                {/* Info pills */}
                <div className='flex flex-wrap gap-2 mt-auto'>
                    <span className='inline-flex items-center gap-1 px-2.5 py-1 bg-gray-50 rounded-lg text-xs text-gray-600'>
                        📍 {politician.constituency}
                    </span>
                    <span className='inline-flex items-center gap-1 px-2.5 py-1 bg-gray-50 rounded-lg text-xs text-gray-600'>
                        🏛️ {politician.state}
                    </span>
                </div>

                {/* Subtle CTA */}
                <div className='mt-3 pt-3 border-t border-gray-100 flex items-center text-orange-600 opacity-0 group-hover:opacity-100 transition-opacity'>
                    <Text variant='small' weight='semibold'>
                        View Details
                    </Text>
                    <span className='ml-1'>→</span>
                </div>
            </motion.div>
        </Link>
    )
}
