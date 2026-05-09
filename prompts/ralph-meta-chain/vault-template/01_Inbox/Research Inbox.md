---
ralph_type: memory
memory_layer: raw
memory_temperature: hot
created: 2026-05-09
status: active
summary: "FutureTools weekly + GitHub trending + creator RSS landings."
---

# Research Inbox

Auto-populated weekly by `04-research-ingest.md` and `08-autoupdate.md`.

| File pattern                            | Source                                         | Cadence  |
| --------------------------------------- | ---------------------------------------------- | -------- |
| `00-Inbox/trending-YYYY-MM-DD.md`       | GitHub trending (research axis)                | daily 01:00 UTC |
| `00-Inbox/futuretools-YYYY-Www.md`      | FutureTools + release feeds (update axis)      | weekly Mon 06:00 UTC |
| `00-Inbox/creators-YYYY-MM-DD.md`       | Alex Finn / Matt Wolfe / Nate Herk RSS         | with research/update axes |

## What's in here right now

Browse `00-Inbox/` directly in Obsidian; entries land here on schedule.

## Promotion rules

The memory pass (#1) promotes anything tagged `#trending` to
`30-Notes/<id>-trending-<slug>.md`. The autoupdate pass also opens
bump-proposals at `30-Notes/<id>-bump-<package>-<version>.md` for any
significantly-stale dependency.

## Cross-references

- `research/github-watchlist.md` — the repo list.
- `research/trend-scout.md` — creator + paper streams.
- `04-research-ingest.md` — daily 01:00 cron.
- `08-autoupdate.md` — weekly Monday cron.
