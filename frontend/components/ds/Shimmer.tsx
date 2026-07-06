import React from "react";

interface ShimmerProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string;
  height?: string;
}

export function Shimmer({ width = "w-full", height = "h-12", className = "", ...props }: ShimmerProps) {
  return (
    <div
      className={`${width} ${height} bg-gradient-to-r from-gray-200 to-gray-100 dark:from-gray-700 dark:to-gray-600 rounded-lg animate-pulse ${className}`}
      {...props}
    />
  );
}
