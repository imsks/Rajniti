"use client"

import { useState } from "react"
import Image from "next/image"
import { getPartyColor } from "@/lib/constants/partyColors"

interface PoliticianAvatarProps {
    /** Photo URL (null/undefined falls back to initials). */
    photo?: string | null
    /** Full name used to derive initials. */
    name: string
    /** Optional party name to color the fallback avatar. */
    party?: string | null
    /** Avatar size in pixels (default: 40). */
    size?: number
    /** Additional CSS classes. */
    className?: string
}

/**
 * Extracts up to 2 initials from a name.
 * Handles space-separated words and abbreviated prefixes (e.g., "C.M.RAMESH").
 */
function getInitials(name: string): string {
    if (!name) return ""
    return name
        .trim()
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((w) => w[0]?.toUpperCase() ?? "")
        .join("")
}

/**
 * Reusable avatar component for politicians.
 * Shows photo when available, falls back to coloured initial circle.
 */
export default function PoliticianAvatar({
    photo,
    name,
    party,
    size = 40,
    className = "",
}: PoliticianAvatarProps) {
    const [imgError, setImgError] = useState(false)
    const initials = getInitials(name)
    const partyColor = getPartyColor(party)

    const showFallback = !photo || imgError

    // Scale font based on avatar size
    const fontSize = Math.max(10, Math.floor(size / 3))

    return (
        <div
            className={`relative shrink-0 rounded-full overflow-hidden flex items-center justify-center ${className}`}
            style={{
                width: size,
                height: size,
                backgroundColor: showFallback ? partyColor.bg : undefined,
                color: showFallback ? partyColor.darkText : undefined,
                fontSize: showFallback ? fontSize : undefined,
                fontWeight: showFallback ? 600 : undefined,
            }}
        >
            {!showFallback ? (
                <Image
                    src={photo!}
                    alt={name}
                    fill
                    className="object-cover"
                    sizes={`${size}px`}
                    onError={() => setImgError(true)}
                />
            ) : (
                <span aria-hidden="true">{initials || "?"}</span>
            )}
        </div>
    )
}
