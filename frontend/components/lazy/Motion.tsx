"use client"

import dynamic from "next/dynamic"
import type { ComponentProps } from "react"
import type { motion } from "framer-motion"

/**
 * Lazy-loaded framer-motion components.
 * These wrappers defer the ~150 KiB framer-motion bundle until the component
 * actually renders, improving FCP and reducing initial JS payload.
 */

export const MotionDiv = dynamic(
    () => import("framer-motion").then((mod) => mod.motion.div),
    { ssr: false }
) as unknown as typeof motion.div

export const MotionSection = dynamic(
    () => import("framer-motion").then((mod) => mod.motion.section),
    { ssr: false }
) as unknown as typeof motion.section

export const MotionSvg = dynamic(
    () => import("framer-motion").then((mod) => mod.motion.svg),
    { ssr: false }
) as unknown as typeof motion.svg

export type MotionDivProps = ComponentProps<typeof MotionDiv>
