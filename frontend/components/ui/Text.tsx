import React from "react"

type TextVariant = "h1" | "h2" | "h3" | "h4" | "body" | "small" | "caption"
type TextColor = "default" | "muted" | "primary" | "white" | "danger" | "success"
type TextWeight = "normal" | "medium" | "semibold" | "bold"

interface TextProps extends React.HTMLAttributes<HTMLElement> {
    variant?: TextVariant
    color?: TextColor
    weight?: TextWeight
    as?: React.ElementType
}

export default function Text({
    children,
    variant = "body",
    color = "default",
    weight,
    as,
    className = "",
    ...props
}: TextProps) {
    const Component = as || (
        variant === "h1" ? "h1" :
        variant === "h2" ? "h2" :
        variant === "h3" ? "h3" :
        variant === "h4" ? "h4" :
        "p"
    )

    const baseStyles = "transition-colors"

    const variants = {
        h1: "text-4xl sm:text-6xl font-serif tracking-[-0.025em] leading-[1.06]",
        h2: "text-3xl sm:text-4xl font-serif tracking-[-0.015em] leading-[1.1]",
        h3: "text-2xl sm:text-3xl font-serif tracking-[-0.01em] leading-[1.2]",
        h4: "text-xl font-serif tracking-[-0.01em] leading-[1.3]",
        body: "text-base sm:text-lg font-sans leading-[1.8]",
        small: "text-sm font-sans leading-[1.75]",
        caption: "text-xs font-sans leading-normal"
    }

    const colors = {
        default: "text-[#0F1F3D] dark:text-gray-100",
        muted: "text-gray-500 dark:text-gray-400",
        primary: "text-orange-600 dark:text-orange-400",
        white: "text-white",
        danger: "text-red-600 dark:text-red-400",
        success: "text-green-600 dark:text-green-400"
    }

    const weights = {
        normal: "font-normal",
        medium: "font-medium",
        semibold: "font-semibold",
        bold: "font-bold"
    }

    const defaultWeights: Record<TextVariant, TextWeight> = {
        h1: "bold",
        h2: "bold",
        h3: "bold",
        h4: "bold",
        body: "normal",
        small: "normal",
        caption: "normal"
    }

    const selectedWeight = weight || defaultWeights[variant]

    return (
        <Component
            className={`${baseStyles} ${variants[variant]} ${colors[color]} ${weights[selectedWeight]} ${className}`}
            {...props}
        >
            {children}
        </Component>
    )
}

