"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import Text from "@/components/ui/Text"
import Image from "@/components/ui/Image"
import Button from "@/components/ui/Button"
import { getParty, getPartyInitial } from "@/lib/politicianUtils"
import type { Politician } from "@/types/politician"
import type { ElectionType } from "@/types/politician"

interface MyPoliticianCardProps {
    politician: Politician | null
    slotType: ElectionType
    onAddClick?: () => void
}

const SLOT_LABELS: Record<ElectionType, string> = {
    MP: "Your MP",
    MLA: "Your MLA",
}

export default function MyPoliticianCard({
    politician,
    slotType,
    onAddClick,
}: MyPoliticianCardProps) {
    const label = SLOT_LABELS[slotType]
    const isPlaceholder = politician == null

    if (isPlaceholder) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className='bg-white rounded-2xl shadow-sm border-2 border-dashed border-gray-200 p-6 flex flex-col items-center justify-center min-h-[200px]'
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

    const party = getParty(politician)
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
            className='bg-white rounded-2xl shadow-sm border border-gray-200 p-5 hover:border-orange-400 transition-all h-full flex flex-col'
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
            <div className='mt-auto pt-3 border-t border-gray-100'>
                <Button
                    href={`/politician/${encodeURIComponent(politician.id)}`}
                    variant='primary'
                    size='sm'
                    className='w-full sm:w-auto'
                >
                    View more
                </Button>
            </div>
        </motion.div>
    )
}
