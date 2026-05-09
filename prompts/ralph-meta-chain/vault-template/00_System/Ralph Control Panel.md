---
ralph_type: system
memory_layer: system
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Top-level dashboard linking every Ralph subsystem."
---

# 🌀 Ralph Control Panel

The single Markdown surface the user opens to see everything Ralph is
doing right now.

## Status

> The Obsidian plugin's status bar mirrors this. Refresh: every 30 s.

```dataview
TABLE
  WITHOUT ID
  axis AS "Axis",
  status AS "Status",
  date AS "Last run",
  counts AS "Counts"
FROM "00_System"
WHERE file.name = "Ralph Control Panel"
SORT axis ASC
```

(The dataview is illustrative; the live state lives in
`90-Meta/ralph-state.json`. The plugin reads that file directly.)

## Quick links

- Pending approvals → [[pending-approvals]] in `07_Business/`
- Open escalations → `60-Interactions/escalations.md`
- This week's autoupdate → `00-Inbox/futuretools-YYYY-Www.md`
- This week's autoevolve proposals → `30-Notes/<id>-evolve-*.md`
- Last 50 metrics → `harness traces --tail 50`
- Heal-checks tail → `90-Meta/heal-checks.ndjson`

## Quick actions

| Want to                          | Do this                                          |
| -------------------------------- | ------------------------------------------------ |
| Pause the chain                  | `touch 90-Meta/STOP` or palette: `Ralph: Pause`   |
| Resume                            | `rm 90-Meta/STOP` or palette: `Ralph: Resume`     |
| Run memory pass NOW              | palette: `Ralph: Run memory pass`                 |
| Run self-test                    | palette: `Ralph: Run self-test (local CI mirror)` |
| See today's promotions           | open `30-Notes/` filtered by today's date         |
| Capture from voice                | iOS Shortcut "Tell Ralph"                          |

## Cron schedule (UTC)

| Time         | Axis                    | Hard cap |
| ------------ | ----------------------- | -------- |
| `0 1 * * *`  | research-ingest          | 25 min   |
| `0 2 * * *`  | memory                   | 25 min   |
| `0 3 * * *`  | skills                   | 25 min   |
| `0 4 * * *`  | interaction               | 25 min   |
| `30 * * * *` | compress (hourly :30)    | 10 min   |
| `15 */6 *`   | autoheal                  | 10 min   |
| `0 5 * * 0`  | autoevolve (Sun)          | 30 min   |
| `0 6 * * 1`  | autoupdate (Mon)          | 25 min   |

## Cross-references

- `docs/ARCHITECTURE.md` — full system map.
- `docs/CRON_JOBS.md` — schedule reference.
- `docs/OPERATIONS_MANUAL.md` — daily / weekly / emergency playbook.
- `00_System/Approval Gates.md` — what needs your approval.
- `00_System/Skill Registry.md`, `Prompt Registry.md`,
  `Provider Registry.md`, `Experiment Registry.md`.
