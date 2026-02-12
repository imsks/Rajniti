"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import Text from "@/components/ui/Text"
import type { Politician } from "@/types/politician"
import { cardHover, fadeIn, quickTransition } from "@/utils/motion"

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

    return (
        <Link
            href={`/politician/${encodeURIComponent(politician.id)}`}
            className='block group'>
            <motion.div 
                className='bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-gray-200 dark:border-slate-700 p-5 hover:border-orange-400 dark:hover:border-orange-500 hover:shadow-lg dark:hover:shadow-xl transition-all h-full flex flex-col'
                initial="rest"
                whileHover="hover"
                variants={cardHover}
                transition={quickTransition}
            >
                {/* Top: Photo / Avatar + Name */}
                <div className='flex items-start gap-4 mb-3'>
                    {hasPhoto ? (
                        <motion.img
                            src={politician.photo!}
                            alt={politician.name}
                            className='w-14 h-14 rounded-full object-cover border-2 border-primary-200 dark:border-primary-700 flex-shrink-0'
                            whileHover={{ scale: 1.1 }}
                            transition={quickTransition}
                            onError={(e) => {
                                (e.target as HTMLImageElement).style.display = "none"
                            }}
                        />
                    ) : (
                        <motion.div 
                            className='w-14 h-14 rounded-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900 dark:to-primary-800 flex items-center justify-center flex-shrink-0 border-2 border-primary-200 dark:border-primary-700'
                            whileHover={{ scale: 1.1, rotate: 5 }}
                            transition={quickTransition}
                        >
                            <span className='text-primary-700 dark:text-primary-300 font-bold text-xs'>
                                {initial}
                            </span>
                        </motion.div>
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
                    <motion.span
                        className={`px-2.5 py-1 rounded-full text-xs font-bold flex-shrink-0 ${
                            isMp
                                ? "bg-blue-100 text-blue-700"
                                : "bg-purple-100 text-purple-700"
                        }`}
                        whileHover={{ scale: 1.1 }}
                        transition={quickTransition}
                    >
                        {politician.type}
                    </motion.span>
                </div>

                {/* Info pills */}
                <div className='flex flex-wrap gap-2 mt-auto'>
                    <motion.span 
                        className='inline-flex items-center gap-1 px-2.5 py-1 bg-gray-50 dark:bg-slate-700 rounded-lg text-xs text-gray-600 dark:text-gray-300'
                        whileHover={{ scale: 1.05 }}
                        transition={quickTransition}
                    >
                        📍 {politician.constituency}
                    </motion.span>
                    <motion.span 
                        className='inline-flex items-center gap-1 px-2.5 py-1 bg-gray-50 dark:bg-slate-700 rounded-lg text-xs text-gray-600 dark:text-gray-300'
                        whileHover={{ scale: 1.05 }}
                        transition={quickTransition}
                    >
                        🏛️ {politician.state}
                    </motion.span>
                </div>

                {/* Subtle CTA */}
                <motion.div 
                    className='mt-3 pt-3 border-t border-gray-100 dark:border-slate-700 flex items-center text-orange-600 dark:text-orange-400 opacity-0 group-hover:opacity-100 transition-opacity'
                    initial={{ x: -10 }}
                    whileHover={{ x: 5 }}
                    transition={quickTransition}
                >
                    <Text variant='small' weight='semibold'>
                        View Details
                    </Text>
                    <span className='ml-1'>→</span>
                </motion.div>
            </motion.div>
        </Link>
    )
}
