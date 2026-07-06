import React from "react";

interface TextProps extends React.HTMLAttributes<HTMLElement> {
  as?: "h1" | "h2" | "h3" | "h4" | "h5" | "h6" | "p" | "span";
}

export function Text({
  as: Component = "p",
  children,
  className = "",
  ...props
}: TextProps) {
  const headingStyles = {
    h1: "text-4xl font-bold leading-tight",
    h2: "text-3xl font-bold leading-tight",
    h3: "text-2xl font-bold leading-tight",
    h4: "text-xl font-bold leading-tight",
    h5: "text-lg font-semibold leading-snug",
    h6: "text-base font-semibold leading-snug",
    p: "text-base leading-relaxed",
    span: "text-base",
  };

  const classes = `${headingStyles[Component]} text-gray-900 dark:text-gray-50 ${className}`;

  return React.createElement(Component, { className: classes, ...props }, children);
}
