# Rajniti Design System Conventions

## Setup & Wrapping

Components require three providers to render correctly:

```jsx
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { MotionProvider } from '@/components/providers/MotionProvider';
import { AuthProvider } from '@/components/auth/AuthProvider';

export default function App({ children }) {
  return (
    <html className="dark">
      <body>
        <AuthProvider>
          <ThemeProvider>
            <MotionProvider>
              {children}
            </MotionProvider>
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
```

Without these providers, components won't have access to theme context (colors, dark mode) or animation capabilities. The `dark` class on the root element enables dark mode.

## Font System

CSS custom properties define the font family:

- `--font-serif`: Serif font (Lora, defaults to Georgia)
- `--font-sans`: Sans-serif font (Plus Jakarta Sans, defaults to system)

Set these on the root `<html>` element. Components use `font-serif` and `font-sans` Tailwind classes that reference these variables.

## Styling Idiom

All components use **Tailwind CSS utility classes** via prop-based variants. There are no exported class names — style via component props only:

```jsx
<Button variant="primary" size="lg" fullWidth>
  Click me
</Button>
```

Color system uses semantic tokens in Tailwind:
- `primary-*` (primary action colors, 50-900)
- `secondary-*` (secondary/neutral colors)
- `red-*` (destructive actions)
- Standard grays (`gray-*`) and semantic colors

Dark mode is automatic via the `dark:` prefix; components detect it from the `dark` class on the root element.

## Component Variants

**Button**: `variant` (primary | secondary | outline | ghost | danger), `size` (sm | md | lg)

**Text**: semantic heading/paragraph sizing via standard HTML tags (`<h1>`, `<p>`, etc.)

**Image/Link**: standard HTML attributes, no custom props

**ThemeToggle**: toggles dark mode theme in localStorage

**Shimmer**: loading skeleton using gradient animation

## Where to Read

Real component props and usage: `components/ui/*.tsx` files  
Tailwind tokens: `tailwind.config.ts`  
Built stylesheet: `_ds_bundle.css` (imported via `styles.css`)

# Frontend (rajniti-frontend@0.1.0)

This design system is the published rajniti-frontend React library, bundled as a single
browser global. All 6 components are the real upstream code.

## Where things are

- `_ds_bundle.js` — the whole-DS bundle at the project root; loads every component to `window.Frontend`. First line is a `/* @ds-bundle: … */` metadata header.
- `styles.css` — the single stylesheet entry (tokens and fonts; this DS injects component styles at runtime). Link this one file.
- `components/<group>/<Name>/<Name>.prompt.md` (example JSX + variants), `<Name>.d.ts` (types), `<Name>.html` (variant grid).
- `tokens/*.css` — CSS custom properties, names verbatim from upstream.
- `fonts/` — `@font-face` files + `fonts.css` (when the package ships fonts).

For a specific component, `read_file("components/<group>/<Name>/<Name>.prompt.md")`.

## Loading

Add these two lines to your page once (React must be on the page first):

```html
<link rel="stylesheet" href="styles.css">
<script src="_ds_bundle.js"></script>
```

Components are then available at `window.Frontend.*`. Mount into a dedicated child node (e.g. `<div id="ds-root">`), not the host page's own React root, so the two trees don't collide:

```jsx
const { Button } = window.Frontend;
ReactDOM.createRoot(document.getElementById('ds-root')).render(<Button />);
```

## Tokens

0 CSS custom properties from rajniti-frontend. Names are
preserved verbatim from upstream. None detected — this DS may compute styles at runtime (CSS-in-JS).



## Components

### general
- `Button`
- `Image`
- `Link`
- `Shimmer`
- `Text`
- `ThemeToggle`
