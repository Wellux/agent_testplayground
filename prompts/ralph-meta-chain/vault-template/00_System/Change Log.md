---
ralph_type: system
memory_layer: system
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Append-only audit trail of every Ralph action (mirrors 90-Meta/log.md)."
---

# Change Log

> Append-only. Karpathy LLM-Wiki format: `## [YYYY-MM-DD] axis | k=v ...`.
> Mirrors `90-Meta/log.md`; this is the human-readable surface.

## How to use

- Open this file when you want a fast summary of what Ralph did this week.
- The `harness traces --tail N` CLI gives the same data plus per-axis filters.
- `90-Meta/log.md` is the raw source; this file is curated highlights
  (the autoheal pass updates this every 6h).

## Recent entries

(populated by `06-autoheal.md` + `07-autoevolve.md` + `08-autoupdate.md`)

## Entry format

```
## [<YYYY-MM-DD>] research | repos=N deduped=D new=K
## [<YYYY-MM-DD>] memory | promotions=N mocs=M orphans=O hypotheses=H validated=V
## [<YYYY-MM-DD>] skills | new=N amended=M validated=V refuted=R hypotheses=H
## [<YYYY-MM-DD>] interaction | profile_updates=P rewrites=R ab=A wins=W losses=L
## [<YYYY-MM-DD HH>] compress | atomic=N weekly=W tokens_saved=T
## [<YYYY-MM-DD HH>] heal | fixed=F escalated=E
## [<YYYY-MM-DD>] evolve | proposals=P deprecations=D rewrites=R coverage_gaps=G
## [<YYYY-MM-DD>] update | releases=R news=N bumps_proposed=B
```

## Cross-references

- `90-Meta/log.md` — raw source.
- `90-Meta/heal-log.md` — heal-pass detail.
- `90-Meta/metrics.ndjson` — per-experiment.
- `harness traces --tail 200`.
- `docs/CONTEXT_LIFECYCLE.md` § Audit.
