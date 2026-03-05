"use client"

import { motion } from "framer-motion"

function shimmer() {
    return (
        <motion.div
            className="absolute inset-0 -translate-x-full"
            animate={{ translateX: "100%" }}
            transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }}
            style={{
                background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)"
            }}
        />
    )
}

function SkeletonBox({ className }: { className: string }) {
    return (
        <div className={`relative overflow-hidden bg-gray-200 rounded ${className}`}>
            {shimmer()}
        </div>
    )
}

export default function PoliticianCardSkeleton() {
    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 h-full flex flex-col">
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
            <div className="mt-auto pt-3 border-t border-gray-100">
                <SkeletonBox className="h-4 w-24 rounded" />
            </div>
        </div>
    )
}