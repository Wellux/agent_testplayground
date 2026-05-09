---
description: |
  Triggers: "ralph cron", "what's the chain doing", "axis status", "ralph master",
  "list ralph axes", "is the cron healthy"
allowed-tools:
  - "Read"
  - "Bash(harness:*,grep:*,find:*,wc:*,jq:*,test:*)"
---

# /ralph-cron

Master command. Render a single dashboard of all eight Ralph axes —
last-run timestamp, success/fail, key counters, and which axis is up
next. LOW risk; pure read; never invokes a chain step.

## Inputs

`$ARGUMENTS` — optional. One of:

- _empty_ (default) — render the dashboard
- `axis:<name>` — drill into one axis (delegates to `/ralph-<name>`
  semantics; renders the per-axis report)
- `next` — print the next-scheduled axis + the absolute UTC firing time
- `health` — like default, but only the rows where last run !=
  `success` (compact alert view)

## Axes (canonical order)

The chain has eight axes. Daily axes fire at 01:00→04:00 UTC; the
hourly compressor and 6-hourly autoheal fire continuously; evolve and
update fire weekly.

| #  | Axis        | Cron (UTC)         | Prompt file                        | Slash command          |
| -- | ----------- | ------------------ | ---------------------------------- | ---------------------- |
| 1  | research    | `0 1 * * *`        | `04-research-ingest.md`            | `/ralph-research`      |
| 2  | memory      | `0 2 * * *`        | `01-memory-optimizer.md`           | `/ralph-memory`        |
| 3  | skills      | `0 3 * * *`        | `02-skills-optimizer.md`           | `/ralph-skill`         |
| 4  | interaction | `0 4 * * *`        | `03-interaction-optimizer.md`      | `/ralph-experiment`    |
| 5  | compress    | `30 * * * *`       | `05-compress.md`                   | `/ralph-compress`      |
| 6  | heal        | `15 */6 * * *`     | `06-autoheal.md`                   | `/ralph-autoheal`      |
| 7  | evolve      | `0 5 * * 0` (Sun)  | `07-autoevolve.md`                 | `/ralph-evolve`        |
| 8  | update      | `0 6 * * 1` (Mon)  | `08-autoupdate.md`                 | `/ralph-autoupdate`    |

## Process

1. Read the last 50 lines of `$VAULT/90-Meta/log.md`.
2. For each axis, find the most-recent matching
   `## [<ts>] <axis> | …` line; extract its key counters.
3. Read `$VAULT/90-Meta/heal-checks.ndjson` (last 20 entries) for
   axes whose `op=propose moves=N conflicts=M` indicates failure.
4. Compute the next firing time per axis (parse the cron schedule;
   UTC). Sort by soonest.
5. If `$ARGUMENTS == "next"`: print only the soonest axis.
6. If `$ARGUMENTS == "health"`: filter rows whose last status is not
   "success".
7. If `$ARGUMENTS == "axis:<name>"`: defer to that axis's slash
   command's report sections.

## Output

Default view — single Markdown table:

```
| axis        | last run (UTC)     | status   | key counter           | next firing (UTC) |
| ----------- | ------------------ | -------- | --------------------- | ----------------- |
| research    | 2026-05-09T01:00Z  | success  | repos=18              | 2026-05-10T01:00Z |
| memory      | 2026-05-09T02:00Z  | success  | promotions=4 mocs=1   | 2026-05-10T02:00Z |
| skills      | 2026-05-09T03:00Z  | success  | new=1 amended=2       | 2026-05-10T03:00Z |
| interaction | 2026-05-09T04:00Z  | success  | rewrites=3 ab=1       | 2026-05-10T04:00Z |
| compress    | 2026-05-09T19:30Z  | success  | compressions=2        | 2026-05-09T20:30Z |
| heal        | 2026-05-09T18:15Z  | success  | fixes=0               | 2026-05-10T00:15Z |
| evolve      | 2026-05-03T05:00Z  | success  | proposals=2           | 2026-05-10T05:00Z |
| update      | 2026-05-04T06:00Z  | success  | bumps=1 news=4        | 2026-05-11T06:00Z |
```

Followed by:

- **Recent failures** (if any) — axis + last-fail timestamp + first
  line of the matching heal-check entry.
- **Recommended action** — one sentence (e.g. "no action — chain
  green for 14 days" / "axis X regressed; run `/ralph-X` for detail").

## Safety

LOW risk. Pure read. Never runs a chain step. The cron itself owns
execution; this command is for the human to glance at the system.

## Cross-references

- `prompts/ralph-meta-chain/crontab.example`
- `prompts/ralph-meta-chain/install/install_cron.sh` (Linux/macOS schedule)
- `prompts/ralph-meta-chain/docs/OPERATIONS_MANUAL.md`
- All eight axis prompts (`0[1-8]-*.md`) and their per-axis slash commands.
