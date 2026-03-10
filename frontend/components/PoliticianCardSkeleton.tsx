"use client"

import Shimmer from "@/components/ui/Shimmer"

function SkeletonBox({ className }: { className: string }) {
    return (
        <div className={`relative overflow-hidden bg-gray-200 dark:bg-gray-700 rounded ${className}`}>
            <Shimmer />
        </div>
    )
}

export default function PoliticianCardSkeleton() {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 h-full flex flex-col">
            {/* Avatar + Name */}
            <div className="flex items-start gap-4 mb-3">
                <SkeletonBox className="w-14 h-14 rounded-full flex-shrink-0" />
                <div className="flex-1 min-w-0 flex flex-col gap-2 pt-1">
                    <SkeletonBox className="h-4 w-3/4 rounded" />
                    <SkeletonBox className="h-3 w-1/2 rounded" />
                </div>
                <SkeletonBox className="w-10 h-6 rounded-full flex-shrink-0" />
            </div>

            {/* Pills */}
            <div className="flex gap-2 mb-3">
                <SkeletonBox className="h-6 w-24 rounded-lg" />
                <SkeletonBox className="h-6 w-20 rounded-lg" />
            </div>

            {/* Footer */}
            <div className="mt-auto pt-3 border-t border-gray-100 dark:border-gray-700">
                <SkeletonBox className="h-4 w-24 rounded" />
            </div>
        </div>
    )
}