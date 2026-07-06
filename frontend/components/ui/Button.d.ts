import React from "react";
interface BaseButtonProps {
    variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
    size?: "sm" | "md" | "lg";
    isLoading?: boolean;
    fullWidth?: boolean;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
    className?: string;
}
interface ButtonAsButtonProps extends BaseButtonProps, React.ButtonHTMLAttributes<HTMLButtonElement> {
    href?: never;
}
interface ButtonAsLinkProps extends BaseButtonProps, React.AnchorHTMLAttributes<HTMLAnchorElement> {
    href: string;
    external?: boolean;
}
type ButtonProps = ButtonAsButtonProps | ButtonAsLinkProps;
export default function Button(props: ButtonProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=Button.d.ts.map