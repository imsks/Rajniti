"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import Text from "@/components/ui/Text"
import Image from "@/components/ui/Image"
import Button from "@/components/ui/Button"
import { getPartyInitial } from "@/lib/politicianUtils"
import type { Politician } from "@/types/politician"
import type { ElectionType } from "@/types/politician"

interface MyPoliticianCardProps {
    politician: Politician | null
    slotType: ElectionType
    onAddClick?: () => void
    onRemove?: () => void
}

const SLOT_LABELS: Record<ElectionType, string> = {
    MP: "Your MP",
    MLA: "Your MLA",
}

export default function MyPoliticianCard({
    politician,
    slotType,
    onAddClick,
    onRemove,
}: MyPoliticianCardProps) {
    const label = SLOT_LABELS[slotType]
    const isPlaceholder = politician == null

    if (isPlaceholder) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className='bg-white/70 dark:bg-gray-800/70 rounded-2xl shadow-sm border-2 border-dashed border-amber-300/60 dark:border-gray-600 p-6 flex flex-col items-center justify-center min-h-[200px]'
            >
                <Text variant='body' className='text-gray-500 dark:text-gray-400 mb-2'>
                    {label}
                </Text>
                <Text variant='small' className='text-gray-400 dark:text-gray-500 mb-4 text-center'>
                    Search above to add
                </Text>
                {onAddClick && (
                    <Button
                        variant='outline'
                        size='sm'
                        onClick={onAddClick}
                        leftIcon={<span className='text-lg'>+</span>}
                    >
                        Add
                    </Button>
                )}
            </motion.div>
        )
    }

    const initial = getPartyInitial(politician)
    const hasPhoto = !!politician.photo
    const isMp = politician.type === "MP"
    const politicianUrlSlugOrId = politician.slug ?? politician.id
    const designation =
        politician.type === "MP"
            ? `MP of ${politician.constituency}`
            : `MLA of ${politician.constituency}`

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className='bg-white dark:bg-gray-800 rounded-xl shadow-md border border-amber-200/70 dark:border-gray-700 p-5 hover:border-amber-400/80 dark:hover:border-orange-500 hover:shadow-lg transition-all h-full flex flex-col'
        >
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
                        className='text-gray-900 dark:text-gray-100 truncate'
                    >
                        {politician.name}
                    </Text>
                    <Text variant='small' className='text-gray-500 dark:text-gray-400 truncate'>
                        {designation}
                    </Text>
                </div>
                <span
                    className={`px-2.5 py-1 rounded-full text-xs font-bold flex-shrink-0 ${
                        isMp
                            ? "bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300"
                            : "bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300"
                    }`}
                >
                    {politician.type}
                </span>
            </div>
            <div className='flex flex-wrap gap-2 mb-4'>
                <span className='px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300'>
                    {politician.type}
                </span>
                <span className='px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300'>
                    {politician.constituency}
                </span>
            </div>
            <div className='mt-auto pt-3 border-t border-amber-100 dark:border-gray-700 flex flex-wrap items-center justify-between gap-2'>
                <Button
                    href={`/politician/${encodeURIComponent(politicianUrlSlugOrId)}`}
                    variant='primary'
                    size='sm'
                    className='w-full sm:w-auto'
                >
                    View more
                </Button>
                {onRemove && (
                    <Button
                        type='button'
                        variant='ghost'
                        size='sm'
                        onClick={(e) => {
                            e.preventDefault()
                            onRemove()
                        }}
                        className='text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 p-2 min-w-0'
                        aria-label='Remove from your politicians'
                    >
                        <svg className='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24' aria-hidden>
                            <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16' />
                        </svg>
                    </Button>
                )}
            </div>
        </motion.div>
    )
}
