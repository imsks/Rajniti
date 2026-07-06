import { LinkProps } from "next/link";
import React from "react";
interface CustomLinkProps extends Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, "href">, LinkProps {
    children: React.ReactNode;
    className?: string;
    external?: boolean;
    variant?: "default" | "nav" | "button" | "underline" | "primary" | "secondary";
}
export default function CustomLink({ children, className, external, variant, ...props }: CustomLinkProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=Link.d.ts.map