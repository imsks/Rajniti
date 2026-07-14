import React from "react";
import Link from "next/link";
import {
  Button as SutraButton,
  button as buttonVariants,
  Spinner,
  cn,
  type ButtonProps as SutraButtonProps,
} from "@sutra/ui";

type RajnitiVariant = "primary" | "secondary" | "outline" | "ghost" | "danger";

interface BaseButtonProps {
  variant?: RajnitiVariant;
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  className?: string;
}

interface ButtonAsButtonProps
  extends BaseButtonProps,
    React.ButtonHTMLAttributes<HTMLButtonElement> {
  href?: never;
}

interface ButtonAsLinkProps
  extends BaseButtonProps,
    React.AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  external?: boolean;
}

type ButtonProps = ButtonAsButtonProps | ButtonAsLinkProps;

// Sutra ships four variants; Rajniti's "outline" maps onto the nearest.
const VARIANT_MAP: Record<RajnitiVariant, SutraButtonProps["variant"]> = {
  primary: "primary",
  secondary: "secondary",
  outline: "secondary",
  ghost: "ghost",
  danger: "danger",
};

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
  } = props;

  const sutraVariant: SutraButtonProps["variant"] = VARIANT_MAP[variant];

  // Link mode: reuse Sutra's button styling on an anchor / Next link.
  if (props.href) {
    const { href, external, ...linkProps } = rest as ButtonAsLinkProps;
    const classes = cn(
      buttonVariants({ variant: sutraVariant, size, fullWidth }),
      className,
    );

    const content = (
      <>
        {isLoading ? (
          <Spinner size="sm" />
        ) : leftIcon ? (
          <span className="inline-flex shrink-0" aria-hidden="true">
            {leftIcon}
          </span>
        ) : null}
        {children}
        {!isLoading && rightIcon ? (
          <span className="inline-flex shrink-0" aria-hidden="true">
            {rightIcon}
          </span>
        ) : null}
      </>
    );

    if (external) {
      return (
        <a
          href={href}
          className={classes}
          target="_blank"
          rel="noopener noreferrer"
          {...linkProps}
        >
          {content}
        </a>
      );
    }

    return (
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      <Link href={href} className={classes} {...(linkProps as any)}>
        {content}
      </Link>
    );
  }

  const { disabled, ...buttonProps } =
    rest as React.ButtonHTMLAttributes<HTMLButtonElement>;

  return (
    <SutraButton
      variant={sutraVariant}
      size={size}
      fullWidth={fullWidth}
      isLoading={isLoading}
      leftIcon={leftIcon}
      rightIcon={rightIcon}
      className={className}
      disabled={disabled}
      {...buttonProps}
    >
      {children}
    </SutraButton>
  );
}
