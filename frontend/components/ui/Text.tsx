import React from "react"
import { Text as SutraText, type TextProps as SutraTextProps } from "@sutra/ui"

type TextVariant = "h1" | "h2" | "h3" | "h4" | "body" | "small" | "caption"
type TextColor = "default" | "muted" | "primary" | "white" | "danger" | "success"
type TextWeight = "normal" | "medium" | "semibold" | "bold"

interface TextProps extends React.HTMLAttributes<HTMLElement> {
    variant?: TextVariant
    color?: TextColor
    weight?: TextWeight
    as?: React.ElementType
}

// Map Rajniti's public API onto Sutra's Text primitive so typography is unified
// on the design system while every existing call site keeps working.
const COLOR_MAP: Record<TextColor, SutraTextProps["color"]> = {
    default: "default",
    muted: "muted",
    primary: "accent",
    white: "inverse",
    danger: "danger",
    success: "success",
}

const WEIGHT_MAP: Record<TextWeight, SutraTextProps["weight"]> = {
    normal: "regular",
    medium: "medium",
    semibold: "semibold",
    bold: "bold",
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
    return (
        <SutraText
            as={as}
            variant={variant}
            color={COLOR_MAP[color]}
            weight={weight ? WEIGHT_MAP[weight] : undefined}
            className={className}
            {...props}
        >
            {children}
        </SutraText>
    )
}
