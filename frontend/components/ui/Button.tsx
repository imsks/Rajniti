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
        "inline-flex items-center justify-center font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg"

    const variants = {
        primary:
            "bg-gradient-to-r from-orange-500 to-orange-600 text-white hover:from-orange-600 hover:to-orange-700 shadow-md hover:shadow-lg focus:ring-orange-500",
        secondary:
            "bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-200 border-2 border-slate-300 dark:border-slate-600 hover:border-orange-500 hover:text-orange-600 dark:hover:text-orange-400 shadow-sm focus:ring-orange-500",
        outline:
            "border-2 border-primary-500 text-primary-600 hover:bg-primary-50 focus:ring-primary-500",
        ghost: "text-gray-600 dark:text-gray-400 hover:text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 focus:ring-orange-500",
        danger: "text-red-600 hover:bg-red-50 focus:ring-red-500"
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
        const { 
            href, 
            external, 
            variant: _v,
            size: _s,
            isLoading: _il,
            fullWidth: _fw,
            leftIcon: _li,
            rightIcon: _ri,
            className: _cn,
            ...linkProps 
        } = props as ButtonAsLinkProps

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
            <Link 
                href={href} 
                className={classes}
                {...linkProps}
            >
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
