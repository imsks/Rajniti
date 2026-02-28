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
                className='bg-white/70 rounded-2xl shadow-sm border-2 border-dashed border-amber-300/60 p-6 flex flex-col items-center justify-center min-h-[200px]'
            >
                <Text variant='body' className='text-gray-500 mb-2'>
                    {label}
                </Text>
                <Text variant='small' className='text-gray-400 mb-4 text-center'>
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
    const designation =
        politician.type === "MP"
            ? `MP of ${politician.constituency}`
            : `MLA of ${politician.constituency}`

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className='bg-white rounded-xl shadow-md border border-amber-200/70 p-5 hover:border-amber-400/80 hover:shadow-lg transition-all h-full flex flex-col relative'
        >
            {onRemove && (
                <button
                    type='button'
                    onClick={(e) => {
                        e.preventDefault()
                        onRemove?.()
                    }}
                    className='absolute top-3 right-3 p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors'
                    title='Remove from your politicians'
                    aria-label='Remove from your politicians'
                >
                    <svg className='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                        <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16' />
                    </svg>
                </button>
            )}
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
                        className='text-gray-900 truncate'
                    >
                        {politician.name}
                    </Text>
                    <Text variant='small' className='text-gray-500 truncate'>
                        {designation}
                    </Text>
                </div>
                <span
                    className={`px-2.5 py-1 rounded-full text-xs font-bold flex-shrink-0 ${
                        isMp
                            ? "bg-blue-100 text-blue-700"
                            : "bg-purple-100 text-purple-700"
                    }`}
                >
                    {politician.type}
                </span>
            </div>
            <div className='flex flex-wrap gap-2 mb-4'>
                <span className='px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-50 text-gray-600'>
                    {politician.type}
                </span>
                <span className='px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-50 text-gray-600'>
                    {politician.constituency}
                </span>
            </div>
            <div className='mt-auto pt-3 border-t border-amber-100 flex flex-wrap items-center justify-between gap-2'>
                <Button
                    href={`/politician/${encodeURIComponent(politician.id)}`}
                    variant='primary'
                    size='sm'
                    className='w-full sm:w-auto'
                >
                    View more
                </Button>
                {onRemove && (
                    <button
                        type='button'
                        onClick={(e) => {
                            e.preventDefault()
                            onRemove()
                        }}
                        className='text-xs text-gray-500 hover:text-red-600 transition-colors'
                    >
                        Remove
                    </button>
                )}
            </div>
        </motion.div>
    )
}
