import { ImageProps as NextImageProps } from "next/image";
interface ImageProps extends NextImageProps {
    fallbackSrc?: string;
    rounded?: "none" | "sm" | "md" | "lg" | "full";
}
export default function Image({ src, alt, className, fallbackSrc, rounded, unoptimized, loading, priority, ...props }: ImageProps): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=Image.d.ts.map