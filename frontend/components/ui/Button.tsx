import React from "react"
import Link from "next/link"

interface BaseButtonProps {
    variant?: "primary" | "secondary" | "outline" | "ghost" | "danger"
    size?: "sm" | "md" | "lg"
    isLoading?: boolean
    fullWidth?: boolean
    leftIcon?: React.ReactNode
    rightIcon?: React.ReactNode
    className?: string
}

interface ButtonAsButtonProps
    extends BaseButtonProps,
        React.ButtonHTMLAttributes<HTMLButtonElement> {
    href?: never
}

interface ButtonAsLinkProps
    extends BaseButtonProps,
        React.AnchorHTMLAttributes<HTMLAnchorElement> {
    href: string
    external?: boolean
}

type ButtonProps = ButtonAsButtonProps | ButtonAsLinkProps

export default function Button(props: ButtonProps) {
    const {
        children,
        variant = "primary",
        size = "md",
        isLoading = false,
        fullWidth = false,
        leftIcon,
        rightIcon,
        className = "",
        ...rest
    } = props

    const baseStyles =
        "inline-flex items-center justify-center font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg"

    const variants = {
        primary:
            "bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 shadow-md hover:shadow-lg focus:ring-primary-500",
        secondary:
            "bg-white dark:bg-gray-800 text-secondary-700 dark:text-gray-200 border-2 border-secondary-300 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-400 hover:text-primary-600 dark:hover:text-primary-400 shadow-sm focus:ring-primary-500",
        outline:
            "border-2 border-primary-500 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 focus:ring-primary-500",
        ghost: "text-secondary-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30 focus:ring-primary-500",
        danger: "text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 focus:ring-red-500"
    }

    const sizes = {
        sm: "px-3 py-1.5 text-sm",
        md: "px-6 py-2 text-base",
        lg: "px-8 py-3 text-lg"
    }

    const width = fullWidth ? "w-full" : ""
    const classes = `${baseStyles} ${variants[variant]} ${sizes[size]} ${width} ${className}`

    const content = (
        <>
            {isLoading ? (
                <div className='mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent' />
            ) : leftIcon ? (
                <span className='mr-2 pointer-events-none'>{leftIcon}</span>
            ) : null}
            {children}
            {rightIcon && (<span className='ml-2 pointer-events-none'>{rightIcon}</span>
)}
        </>
    )

    if (props.href) {
        const { href, external, ...linkProps } = rest as ButtonAsLinkProps

        if (external) {
            return (
                <a
                    href={href}
                    className={classes}
                    target='_blank'
                    rel='noopener noreferrer'
                    {...linkProps}>
                    {content}
                </a>
            )
        }

        return (
            <Link href={href} className={classes} {...(linkProps as any)}>
                {content}
            </Link>
        )
    }

    const { disabled, ...buttonProps } = rest as ButtonAsButtonProps

    return (
        <button
            className={classes}
            disabled={disabled || isLoading}
            {...buttonProps}>
            {content}
        </button>
    )
}
