"use client"

import Skeleton from "@/components/ui/Skeleton"

export default function StatCardSkeleton() {
    return (
        <div className='bg-white rounded-xl p-4 border border-gray-200 shadow-sm flex flex-col gap-2'>
            <Skeleton width='60%' height={32} />
            <Skeleton width='40%' height={14} />
        </div>
    )
}
