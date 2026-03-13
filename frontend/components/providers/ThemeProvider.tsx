"use client"

import { createContext, useContext, useEffect, useState, useCallback } from "react"

type Theme = "light" | "dark"

interface ThemeContextType {
    theme: Theme
    setTheme: (theme: Theme) => void
    toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
    const context = useContext(ThemeContext)
    if (!context) throw new Error("useTheme must be used within a ThemeProvider")
    return context
}

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>("light")
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        const stored = localStorage.getItem("theme") as Theme | null
        if (stored === "dark" || stored === "light") {
            setThemeState(stored)
        } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
            setThemeState("dark")
        }
        setMounted(true)
    }, [])

    useEffect(() => {
        if (!mounted) return
        const root = document.documentElement
        if (theme === "dark") {
            root.classList.add("dark")
        } else {
            root.classList.remove("dark")
        }
        localStorage.setItem("theme", theme)
    }, [theme, mounted])

    // Listen for system preference changes
    useEffect(() => {
        const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
        const handler = (e: MediaQueryListEvent) => {
            const stored = localStorage.getItem("theme")
            if (!stored) {
                setThemeState(e.matches ? "dark" : "light")
            }
        }
        mediaQuery.addEventListener("change", handler)
        return () => mediaQuery.removeEventListener("change", handler)
    }, [])

    const setTheme = useCallback((t: Theme) => setThemeState(t), [])
    const toggleTheme = useCallback(
        () => setThemeState((prev) => (prev === "dark" ? "light" : "dark")),
        []
    )

    return (
        <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    )
}
