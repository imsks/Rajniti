/** Hostnames whose politician photos may be resized via Next.js image optimization. */
export const OPTIMIZABLE_IMAGE_HOSTS = new Set([
    "results.eci.gov.in",
    "eci.gov.in",
]);
export function isExternalImageUrl(url) {
    return url.startsWith("http://") || url.startsWith("https://");
}
/** True when Next.js should proxy/resize this remote URL (known ECI photo hosts). */
export function isOptimizableExternalUrl(url) {
    if (!isExternalImageUrl(url))
        return false;
    try {
        const hostname = new URL(url).hostname.toLowerCase();
        return OPTIMIZABLE_IMAGE_HOSTS.has(hostname);
    }
    catch {
        return false;
    }
}
/** Whether the Image component should skip Next.js optimization for this src. */
export function shouldUseUnoptimizedImage(src, explicitUnoptimized) {
    if (explicitUnoptimized !== undefined)
        return explicitUnoptimized;
    if (typeof src !== "string")
        return false;
    if (!isExternalImageUrl(src))
        return false;
    return !isOptimizableExternalUrl(src);
}
//# sourceMappingURL=optimize-external.js.map