import React from "react";
type TextVariant = "h1" | "h2" | "h3" | "h4" | "body" | "small" | "caption";
type TextColor = "default" | "muted" | "primary" | "white" | "danger" | "success";
type TextWeight = "normal" | "medium" | "semibold" | "bold";
interface TextProps extends React.HTMLAttributes<HTMLElement> {
    variant?: TextVariant;
    color?: TextColor;
    weight?: TextWeight;
    as?: React.ElementType;
}
export default function Text({ children, variant, color, weight, as, className, ...props }: TextProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=Text.d.ts.map