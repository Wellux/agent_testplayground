---
ralph_type: report
memory_layer: report
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Heal-pass status (every 6 hours)."
---

# Autoheal Report

Updated every 6 hours by `06-autoheal.md`. Read this when you see a
`…` in the Obsidian status bar that should be `✓`.

## Latest heartbeat

| Axis        | Last run        | Status   | Heal action                |
| ----------- | --------------- | -------- | -------------------------- |
| research    | —               | —        | —                          |
| memory      | —               | —        | —                          |
| skills      | —               | —        | —                          |
| interaction | —               | —        | —                          |
| compress    | —               | —        | —                          |
| heal        | —               | —        | —                          |
| evolve      | —               | —        | —                          |
| update      | —               | —        | —                          |

## Latest self-test (`harness self-test`)

| Check       | OK?  | Duration | Detail                          |
| ----------- | ---- | -------- | ------------------------------- |
| privacy     | —    | —        | —                               |
| shell       | —    | —        | —                               |
| python      | —    | —        | —                               |
| unit-tests  | —    | —        | —                               |
| plugin      | —    | —        | —                               |

## Recent fixes (LOW-risk auto-applied)

(populated by the cron)

## Open escalations

See `60-Interactions/escalations.md` for the full list. Top-of-list
appears in the Obsidian status bar.

## Cross-references

- `06-autoheal.md` — the source cron prompt.
- `harness/harness/self_test.py` — local CI mirror.
- `90-Meta/heal-log.md` — per-pass detail.
- `90-Meta/heal-checks.ndjson` — per-check ndjson.
- `60-Interactions/escalations.md` — needs your attention.
