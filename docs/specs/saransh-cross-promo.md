# Saransh cross-promo section

**Issue**: [imsks/Rajniti#261](https://github.com/imsks/Rajniti/issues/261) · **Type**: AFK · **Blocked by**: none

Part of the Saransh launch-readiness epic ([imsks/Saransh#41](https://github.com/imsks/Saransh/issues/41)).
The other ten slices live in the Saransh repo under `docs/specs/launch-readiness/`. This is the
only slice that touches Rajniti.

## Why

Saransh already links to Rajniti — `RajnitiSection.tsx` on the Saransh marketing page explains that
when a Story mentions a representative's promise, it cross-links to their record. Rajniti says
nothing about Saransh. The loop is open in one direction.

The two products share an audience. Someone reading a politician's tracked promises on Rajniti is
exactly the person who wants attributed news summaries about what actually happened.

## Decision

A **link-out section only**. No waitlist form embedded in Rajniti, and no new API surface here —
the Waitlist write path stays in Saransh, in one place. (Grilling decision D11.)

## Current state

- `frontend/app/(marketing)/page.tsx` — Navbar → Hero → Features → Preamble → Contribute →
  Contributors → Footer. Below-fold sections are loaded with `dynamic()` to keep the initial bundle
  down; the file's comment records roughly 150 KiB saved.
- `frontend/components/marketing/` — `HeroSection`, `FeaturesSection`, `ContributeSection`,
  `ContributorsSection`, `ScrollReset`, and an `index.ts` barrel export
- `frontend/components/PreambleSection.tsx` — imported directly, not from the marketing barrel
- Design system: `@/components/ui` (`Text`, `Link`, `Button`), framer-motion via `m` with
  `initial` / `whileInView` / `viewport={{ once: true }}`, `useAnalytics()` for tracked events
- `ContributeSection.tsx` is the closest model to copy — a `"use client"` section with an analytics
  hook, motion reveals, and a two-card grid

## Placement

Between `PreambleSection` and `ContributeSection`.

The reasoning is sequencing, not aesthetics: the Preamble establishes what Rajniti stands for, and
the Contribute section is the ask. The cross-promo belongs after the reader is bought in and before
they are asked for something. Putting it after Contributors buries it below the fold's fold.

## Content

Rajniti's voice, not Saransh's marketing copy. The relationship is the message: Rajniti tracks what
representatives promised; Saransh reports the news those promises turn up in, summarised from
verified sources with attribution. Same civic-accountability project, two halves.

One clear outbound call to action. Do not restate Saransh's feature list — the reader can get that
from the site.

## Action plan

1. Create `components/marketing/SaranshSection.tsx` and export it from
   `components/marketing/index.ts`.
2. Build it with the existing design system — `Text`, `Link`, `Button`, `m` from framer-motion —
   matching the visual weight of its neighbours in light and dark mode.
3. Render it in `app/(marketing)/page.tsx` between `PreambleSection` and `ContributeSection`, loaded
   via `dynamic()` like the other below-fold sections. Do not import it eagerly; it would undo the
   bundle-size work the file's comment describes.
4. Read the destination from `NEXT_PUBLIC_SARANSH_URL`, defaulting to
   `https://saransh-app.vercel.app`. **The env var is the point** — the Saransh frontend is not
   deployed yet, and the final URL is decided in Saransh slice 10. A hardcoded link would need a
   code change and a redeploy to fix.
5. External link: `target="_blank"` and `rel="noopener noreferrer"`.
6. Track the click with `useAnalytics()`, adding the event to the typed `AnalyticsEventMap` in
   `lib/analytics` — the map is typed, so an untyped event name will not compile.
7. Document `NEXT_PUBLIC_SARANSH_URL` in the frontend env example.
8. Component test: renders, resolves the href from the env var, and fires the analytics event on
   click.

## Acceptance criteria

- [ ] `components/marketing/SaranshSection.tsx` created and exported from the barrel
- [ ] Rendered between `PreambleSection` and `ContributeSection`, code-split via `dynamic()`
- [ ] Visual language matches the surrounding sections in light and dark mode; responsive on mobile
- [ ] Destination from `NEXT_PUBLIC_SARANSH_URL` with the documented default
- [ ] External link carries `target="_blank"` and `rel="noopener noreferrer"`
- [ ] Click fires a tracked analytics event, added to the typed `AnalyticsEventMap`
- [ ] `NEXT_PUBLIC_SARANSH_URL` documented in the frontend env example
- [ ] Test covers render, resolved href, and the analytics event
- [ ] Lint, typecheck and the frontend suite pass

## How to verify

```bash
cd frontend
npm run dev            # section appears between Preamble and Contribute, both themes
npm test
npm run lint
```

## A note on the link

Until Saransh slice 10 deploys the frontend, the default URL does not resolve. That is expected and
is why the URL is env-driven. If Saransh lands on a different domain, `NEXT_PUBLIC_SARANSH_URL` gets
set in the Rajniti deployment — no code change.

## Out of scope

An embedded waitlist form, any Rajniti API surface, and the Story↔representative data cross-link
(that is a Saransh-side HTTP call, unimplemented, and not part of this epic).
