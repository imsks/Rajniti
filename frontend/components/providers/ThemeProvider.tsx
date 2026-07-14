"use client";

import {
  ThemeProvider as SutraThemeProvider,
  useTheme as useSutraTheme,
} from "@sutra/ui";

type Theme = "light" | "dark";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

/**
 * Rajniti's theme hook, now backed by Sutra's theme engine. `theme` reports the
 * concrete applied theme (Sutra's resolvedTheme) to preserve the previous API.
 */
export function useTheme(): ThemeContextType {
  const { resolvedTheme, setTheme, toggleTheme } = useSutraTheme();
  return { theme: resolvedTheme, setTheme, toggleTheme };
}

/**
 * Wraps Sutra's ThemeProvider, keeping the existing `"theme"` localStorage key
 * so the anti-flash script in the root layout stays compatible.
 */
export default function ThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SutraThemeProvider defaultTheme="system" storageKey="theme">
      {children}
    </SutraThemeProvider>
  );
}
