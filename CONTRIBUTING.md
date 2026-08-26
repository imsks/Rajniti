# Contributing to Rajniti

Thanks for helping make Indian democracy more transparent. Rajniti is community-driven, and every contribution — a single corrected record, a bug fix, or a new feature — matters.

This guide covers **how to contribute**. For **how to run the project** (setup, Makefile, env vars, API endpoints, structure), see the [README](./readme.md) and [`frontend/README.md`](./frontend/README.md). We won't repeat that here.

---

## The one rule that matters most

**Never publish unsourced or fabricated data.** Rajniti's entire value is trust. A single made-up criminal record, fake election result, or guessed education detail permanently breaks the "verified" positioning for every user.

- Every data point must trace to a real, citable source.
- If you're unsure about a value, leave it blank and flag it — don't guess.
- Enrichment agents auto-verify against sources; low-confidence output is for human review, not auto-publish.

Everything else in this guide is negotiable style. This rule is not.

---

## Ways to contribute

- **Code — frontend or backend:** pick an issue from the backlog and ship it.
- **Data enrichment:** add or correct MP/MLA records (`app/data/mp.json`, `app/data/mla.json`), manually or via the AI agents.
- **Bug reports & feature ideas:** open an issue.
- **Docs:** improve the README, this guide, or inline docs.

New here? Look for issues labelled **`good first issue`**.

---

## Before you start: claim an issue

1. Browse the [Issues](https://github.com/imsks/Rajniti/issues) and the project backlog.
2. Read the issue fully — the description, **current behaviour**, **expected behaviour**, and **acceptance criteria** define "done."
3. Check nobody else is already on it (open PRs / recent comments).
4. **Comment to get assigned** before writing code, so effort isn't duplicated.
5. If anything is unclear, ask in the issue or in [Discussions](https://github.com/imsks/Rajniti/discussions) first. A two-line question saves a rejected PR.

Please don't open large unsolicited PRs that aren't tied to an issue — start a discussion so we can align on approach.

---

## Setup (quick pointer)

Full instructions are in the [README](./readme.md). The short version:

```bash
git clone https://github.com/imsks/Rajniti.git && cd Rajniti
make setup            # copies .env templates
make up               # full stack (API :8000 + Next.js :3000 + Postgres)
```

---

## Branching

The default branch is **`development`** — branch off it and target it in your PR (not `main`/`production`).

```bash
git checkout development && git pull
git checkout -b <type>/<short-scope>
```

Branch prefixes:

| Prefix | Use for |
| --- | --- |
| `feat/` | New feature or enhancement |
| `fix/` | Bug fix |
| `data/` or `enrich/` | Politician data additions/corrections |
| `refactor/` | Code cleanup, no behaviour change |
| `docs/` | Documentation only |
| `chore/` | Tooling, CI, deps |

Example: `feat/numbered-pagination`, `fix/search-dropdown-stale-results`.

---

## Project house rules (read before touching the UI)

These are settled architectural decisions. Work within them — a PR that violates one will be sent back.

- **Dark mode:** use real `dark:bg-* / text-* / border-*` classes only. **No `filter: invert()` hacks** — they produce patchy, unreliable dark mode. Every UI change must look right in **both** light and dark.
- **Preserve path-based URLs.** Listing/pagination routes are path-based (`/politicians/page/N`, `/politicians/mp/page/N`, `/politicians/state/<slug>/page/N`) so they stay shareable and crawlable. Don't quietly switch to query params.
- **Filters match cardinality.** Toggle for a few options, dropdown for ~36 states, searchable multi-select for ~93 parties. Don't force one generic pattern.
- **Names render in title case** everywhere (list, profile, OG tags), preserving initials and honorifics.
- **Public data needs no login.** Basic "tell me about this politician" must never sit behind auth. Accounts are only for personalisation (tracking your reps).
- **Accessibility baseline:** keyboard-navigable, correct ARIA roles, visible focus, contrast that passes AA, tap targets ≥ 44px, and no horizontal overflow at 360px.
- **Reuse existing components** (avatar, `RoleBadge`, the party → logo/colour map) instead of re-implementing.

---

## Code style & linting

- **Python:** `black` + `isort` formatting, `flake8` linting. Run `black app tests scripts && isort app tests scripts`, then `flake8` / `mypy`.
- **Frontend:** ESLint + TypeScript typecheck (`cd frontend && npm run lint && npx tsc --noEmit`).
- **Pre-commit hook:** copy `scripts/pre_commit_hook.py` into `.git/hooks/pre-commit` once — this auto-stamps `lastUpdated` on data-file commits.
- Keep changes focused; don't reformat unrelated files in the same PR.

---

## Testing

Your PR must keep the suite green.

```bash
pip install -r requirements-test.txt   # first time
pytest tests/unit tests/integration tests/e2e -v
pytest tests/unit -v
cd frontend && npm test
```

- Add or update tests for new behaviour and bug fixes.
- Paste the command(s) you ran into the PR's "How was this tested?" section.

**Required CI checks (all must pass):** `Backend — tests`, `Frontend — tests`, `Backend — lint`, `Frontend — lint & typecheck`, `Frontend — production build`.

---

## Commit messages

- Imperative mood, present tense: "Add numbered pagination", not "Added" / "Adds".
- One logical change per commit where practical; a scope helps: `feat(explore): add numbered pagination`.
- Reference the issue in the body when useful.

---

## Opening a pull request

1. Push your branch and open a PR **into `development`**.
2. **Fill in the PR template** — it's pre-loaded. In particular:
   - Tick the correct **Type of change**.
   - Add **exactly one version-bump label** — `patch` (fixes/tweaks), `minor` (features/enhancements), or `major` (breaking). No label defaults to `patch`.
   - Describe **how you tested** (paste the command).
3. **Link the issue:** put `Closes #<issue-number>` in the description so it auto-closes on merge.
4. **UI changes:** attach before/after screenshots in **both light and dark mode**, and a mobile (360px) shot.
5. **Never commit** `.env`, API keys, secrets, or `app/database/cache.db`.
6. **Data PRs** should change **only** `app/data/mp.json` and/or `app/data/mla.json` — nothing else.
7. Keep the diff to intended changes only; review it yourself first.

Map your work back to the issue's **acceptance criteria** — a reviewer will check each box against your PR.

---

## Review & merge

- A maintainer reviews for correctness, the house rules above, tests, and green CI.
- Respond to feedback with follow-up commits (don't force-push over the review history unless asked).
- Once approved and CI is green, a maintainer merges. The version-bump label drives the automatic release bump on merge to production.
- Be patient and kind — reviewers are volunteers too.

---

## Data & AI-agent contributions

To enrich records with the agents (needs at least one LLM key — Gemini's free tier works), see **Running agents** and **Contributing with AI agents** in the [README](./readme.md). Rules: data PRs touch JSON only, no secrets in commits, run the test suite before pushing, and every enriched field must be source-backed.

---

## Reporting bugs & requesting features

- **Bug:** open an issue via **Found a Bug?** ([new issue](https://github.com/imsks/Rajniti/issues/new)). Include steps to reproduce, expected vs actual, environment, and a screenshot/log.
- **Missing politician data:** open a data issue with the details and sources — we'll enrich the profile.
- **Feature idea:** start a [Discussion](https://github.com/imsks/Rajniti/discussions) or open a feature issue so we can align before code.

---

## Code of Conduct

Be respectful, assume good intent, and keep discussion focused on the work. Harassment or discrimination isn't tolerated. Rajniti is a civic project — treat data about real people with accuracy and care.

## License

By contributing, you agree that your contributions are licensed under the project's [MIT License](https://opensource.org/licenses/MIT).

---

**Built with ❤️ in 🇮🇳 — thank you for contributing.**