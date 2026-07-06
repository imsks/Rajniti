"use client";
import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useEffect, useState, useCallback, } from "react";
const ThemeContext = createContext(undefined);
export function useTheme() {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error("useTheme must be used within a ThemeProvider");
    }
    return context;
}
function getInitialTheme() {
    if (typeof window === "undefined") {
        return "light";
    }
    const stored = localStorage.getItem("theme");
    if (stored === "dark" || stored === "light") {
        return stored;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
}
export default function ThemeProvider({ children, }) {
    const [theme, setThemeState] = useState(getInitialTheme);
    useEffect(() => {
        const root = document.documentElement;
        root.classList.toggle("dark", theme === "dark");
        localStorage.setItem("theme", theme);
    }, [theme]);
    // Listen for system theme changes only when
    // user has not manually selected a theme
    useEffect(() => {
        const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
        const handler = (e) => {
            const stored = localStorage.getItem("theme");
            if (!stored) {
                setThemeState(e.matches ? "dark" : "light");
            }
        };
        mediaQuery.addEventListener("change", handler);
        return () => {
            mediaQuery.removeEventListener("change", handler);
        };
    }, []);
    const setTheme = useCallback((t) => {
        setThemeState(t);
    }, []);
    const toggleTheme = useCallback(() => {
        setThemeState((prev) => (prev === "dark" ? "light" : "dark"));
    }, []);
    return (_jsx(ThemeContext.Provider, { value: {
            theme,
            setTheme,
            toggleTheme,
        }, children: children }));
}
//# sourceMappingURL=ThemeProvider.js.map