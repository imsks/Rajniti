import React from "react";

interface ImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  alt: string;
}

export const Image = React.forwardRef<HTMLImageElement, ImageProps>(
  ({ alt, className = "", ...props }, ref) => (
    <img
      ref={ref}
      alt={alt}
      {...props}
      className={`max-w-full h-auto ${className}`}
    />
  )
);

Image.displayName = "Image";
