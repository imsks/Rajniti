"use client"

import { motion } from "framer-motion"

interface SkeletonProps {
    className?: string
    variant?: "rectangle" | "circle"
    width?: string | number
    height?: string | number
}

export default function Skeleton({
    className = "",
    variant = "rectangle",
    width,
    height,
}: SkeletonProps) {
    return (
        <motion.div
            initial={{ opacity: 0.5 }}
            animate={{ opacity: [0.5, 0.8, 0.5] }}
            transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut",
            }}
            className={`bg-gray-200 ${variant === "circle" ? "rounded-full" : "rounded-lg"} ${className}`}
            style={{ width, height }}
        />
    )
}
