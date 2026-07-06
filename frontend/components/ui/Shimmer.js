"use client";
import { jsx as _jsx } from "react/jsx-runtime";
import { m } from "framer-motion";
export default function Shimmer() {
    return (_jsx(m.div, { className: "absolute inset-0 -translate-x-full", animate: { translateX: "100%" }, transition: { duration: 1.2, repeat: Infinity, ease: "linear" }, style: {
            background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)"
        } }));
}
//# sourceMappingURL=Shimmer.js.map