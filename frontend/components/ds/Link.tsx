import React from "react";

interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  external?: boolean;
}

export const Link = React.forwardRef<HTMLAnchorElement, LinkProps>(
  ({ external = false, children, ...props }, ref) => (
    <a
      ref={ref}
      {...props}
      {...(external && { target: "_blank", rel: "noopener noreferrer" })}
      className={`text-blue-600 dark:text-blue-400 hover:underline ${props.className || ""}`}
    >
      {children}
    </a>
  )
);

Link.displayName = "Link";
