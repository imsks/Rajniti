"use client"

import type { CSSProperties, MouseEvent, ReactNode } from "react"
import { motion, useReducedMotion } from "framer-motion"

interface SpotlightCardProps {
    children: ReactNode
    className?: string
    glowColor?: string
}

type SpotlightStyle = CSSProperties & {
    "--spotlight-x": string
    "--spotlight-y": string
    "--spotlight-color": string
}

export default function SpotlightCard({
    children,
    className = "",
    glowColor = "rgba(249, 115, 22, 0.30)",
}: SpotlightCardProps) {
    const reduceMotion = useReducedMotion()

    const handleMouseMove = (event: MouseEvent<HTMLDivElement>) => {
        if (reduceMotion) return
        const rect = event.currentTarget.getBoundingClientRect()
        if (!rect.width || !rect.height) return

        const x = ((event.clientX - rect.left) / rect.width) * 100
        const y = ((event.clientY - rect.top) / rect.height) * 100

        event.currentTarget.style.setProperty("--spotlight-x", `${x}%`)
        event.currentTarget.style.setProperty("--spotlight-y", `${y}%`)
    }

    return (
        <motion.div
            onMouseMove={handleMouseMove}
            whileHover={reduceMotion ? undefined : { y: -6, scale: 1.01 }}
            transition={{ duration: 0.2 }}
            className={`group relative overflow-hidden rounded-2xl ${className}`}
            style={
                {
                    "--spotlight-x": "50%",
                    "--spotlight-y": "50%",
                    "--spotlight-color": glowColor,
                } as SpotlightStyle
            }>
            <div className='pointer-events-none absolute inset-0 rounded-2xl border border-white/20'></div>
            <div
                aria-hidden='true'
                className='pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100'
                style={{
                    background:
                        "radial-gradient(260px circle at var(--spotlight-x) var(--spotlight-y), var(--spotlight-color), transparent 60%)",
                }}></div>
            <div className='relative z-10'>{children}</div>
        </motion.div>
    )
}
