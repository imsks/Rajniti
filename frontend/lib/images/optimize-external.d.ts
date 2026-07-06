/** Hostnames whose politician photos may be resized via Next.js image optimization. */
export declare const OPTIMIZABLE_IMAGE_HOSTS: Set<string>;
export declare function isExternalImageUrl(url: string): boolean;
/** True when Next.js should proxy/resize this remote URL (known ECI photo hosts). */
export declare function isOptimizableExternalUrl(url: string): boolean;
/** Whether the Image component should skip Next.js optimization for this src. */
export declare function shouldUseUnoptimizedImage(src: string, explicitUnoptimized?: boolean): boolean;
//# sourceMappingURL=optimize-external.d.ts.map