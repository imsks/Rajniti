"use client"

import NextImage, { ImageProps as NextImageProps } from "next/image"
import { useState } from "react"

interface ImageProps extends NextImageProps {
    fallbackSrc?: string
    rounded?: "none" | "sm" | "md" | "lg" | "full"
}

export default function Image({
    src,
    alt,
    className = "",
    fallbackSrc = "/default-avatar.png",
    rounded = "none",
    unoptimized,
    ...props
}: ImageProps) {
    const [error, setError] = useState(false)

    const roundedStyles = {
        none: "",
        sm: "rounded-sm",
        md: "rounded-md",
        lg: "rounded-lg",
        full: "rounded-full"
    }

    const isExternal =
        typeof src === "string" && src.startsWith("http")

    return (
        <NextImage
            src={error ? fallbackSrc : src}
            alt={alt}
            loading='lazy'
            unoptimized={unoptimized ?? isExternal}
            className={`${roundedStyles[rounded]} ${className}`}
            onError={() => setError(true)}
            {...props}
        />
    )
}

