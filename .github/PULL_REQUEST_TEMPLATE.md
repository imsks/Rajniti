## What does this PR do?

<!-- A brief description of the change. -->

## Type of change

- [ ] Data contribution (added/updated MP or MLA records)
- [ ] New enrichment process (new agent process class)
- [ ] Bug fix
- [ ] Feature / enhancement
- [ ] Refactor / code cleanup
- [ ] Documentation update
- [ ] Other (describe below)

## Scope

<!-- For data PRs: which state/segment? How many records added/updated? -->
<!-- For code PRs: which modules are affected? -->

## How was this tested?

<!-- Paste the command you ran and a short summary of the result. -->

```bash
# e.g.
# python3 scripts/run_politician_agent.py --type MP --limit 3 --log-level INFO
# python3 scripts/fetch_mlas.py --state "Andhra Pradesh" --log-level INFO
# make test
```

## Version bump

<!-- Add ONE label to this PR to control the automatic version bump when merged to production. -->
<!-- If no label is added, defaults to `patch`. -->

- [ ] `patch` — Bug fixes, small tweaks (0.3.5 → 0.3.6)
- [ ] `minor` — New features, enhancements (0.3.5 → 0.4.0)
- [ ] `major` — Breaking changes (0.3.5 → 1.0.0)

## Checklist

- [ ] I have **not** committed `.env`, API keys, or any secrets
- [ ] I have **not** committed `app/database/cache.db`
- [ ] I have reviewed the diff and it only contains intended changes
- [ ] Data changes are limited to `app/data/mp.json` and/or `app/data/mla.json`
- [ ] Tests pass locally (`make test`)

## Screenshots / logs (optional)

<!-- Attach relevant logs, screenshots, or snippets if helpful. -->

## Additional notes

<!-- Anything reviewers should know — uncertain records, manual fixes, edge cases, etc. -->
