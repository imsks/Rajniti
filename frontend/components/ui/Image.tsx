"use client"

import NextImage, { ImageProps as NextImageProps } from "next/image"
import { useState } from "react"
import { shouldUseUnoptimizedImage } from "@/lib/images/optimize-external"

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
    loading,
    priority,
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

    const resolvedSrc = error ? fallbackSrc : src
    const resolvedUnoptimized =
        typeof resolvedSrc === "string"
            ? shouldUseUnoptimizedImage(resolvedSrc, unoptimized)
            : (unoptimized ?? false)

    return (
    <NextImage
        src={resolvedSrc}
        alt={alt}
        priority={priority}
        loading={priority ? undefined : (loading ?? "lazy")}
        unoptimized={resolvedUnoptimized}
        className={`${roundedStyles[rounded]} ${className}`}
        onError={() => setError(true)}
        width={props.fill ? undefined : (props.width ?? 200)}
        height={props.fill ? undefined : (props.height ?? 200)}
        {...props}
    />
    )
}
