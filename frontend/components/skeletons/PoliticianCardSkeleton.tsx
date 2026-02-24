"use client"

import Skeleton from "@/components/ui/Skeleton"

export default function PoliticianCardSkeleton() {
    return (
        <div className='bg-white rounded-2xl shadow-sm border border-gray-200 p-5 h-full flex flex-col'>
            {/* Top: Photo / Avatar + Name */}
            <div className='flex items-start gap-4 mb-3'>
                {/* Avatar Skeleton */}
                <Skeleton variant='circle' width={56} height={56} className='flex-shrink-0' />

                <div className='flex-1 min-w-0 flex flex-col gap-2'>
                    {/* Name Skeleton */}
                    <Skeleton width='70%' height={20} />
                    {/* Party Skeleton */}
                    <Skeleton width='40%' height={14} />
                </div>

                {/* Type badge Skeleton */}
                <Skeleton width={40} height={20} className='rounded-full' />
            </div>

            {/* Info pills Skeleton */}
            <div className='flex flex-wrap gap-2 mt-auto'>
                <Skeleton width={100} height={24} className='rounded-lg' />
                <Skeleton width={120} height={24} className='rounded-lg' />
            </div>

            {/* Subtle CTA Skeleton */}
            <div className='mt-3 pt-3 border-t border-gray-100 flex items-center'>
                <Skeleton width={80} height={16} />
            </div>
        </div>
    )
}
