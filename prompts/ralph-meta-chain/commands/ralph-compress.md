---
description: |
  Triggers: "ralph compress", "compression report", "what got compressed",
  "wiki shape", "any bloat"
allowed-tools:
  - "Read"
  - "Bash(harness:*,grep:*,find:*,wc:*,jq:*)"
---

# /ralph-compress

Show the most-recent hourly compression pass: what got summarized,
what got rolled up into weekly digests, and which notes are now
flagged as "above the token threshold" but not yet compressed. LOW
risk; read-only.

## Inputs

`$ARGUMENTS` — optional. Acceptable values:

- `today` (default) — today's compression activity
- `last-hour` — only the most recent pass
- `this-week` — weekly rollup view
- a single ISO date

## Process

1. Read `$VAULT/06_Reports/compress-report-<date>.md` (if dated arg)
   or `$VAULT/06_Reports/compress-report.md` (today).
2. Read `$VAULT/90-Meta/log.md` and grep `## [<ts>] compress |` lines
   — sum `compressions=`, `weekly_rollups=`, `bytes_saved=`.
3. List candidates above `compress.token_threshold` (from
   `prompts/ralph-meta-chain/config.example.yml`) that have NOT been
   compressed yet — use `harness compress --dry-run --since
   <last-pass>` if available; otherwise read
   `$VAULT/90-Meta/compress-queue.ndjson`.
4. List the most-recent 5 notes that gained a `## Compressed
   YYYY-MM-DD` block.

## Output

Markdown report:

- **Counters** — `compressions=N weekly_rollups=N bytes_saved=KB`.
- **Recently compressed** (5 with [[wikilinks]] + bytes-before /
  bytes-after).
- **Pending candidates** (above-threshold, not yet compressed).
- **Recommended action** — one sentence: "no action" / "raise
  token_threshold by 25%" / "weekly rollup overdue — touch
  90-Meta/STOP-WEEKLY-ROLLUP to skip" / specific issue.

## Safety

LOW risk. Read-only. Never edits. The compression pass itself runs
hourly via the cron'd `05-compress.md` and obeys the per-axis budget
in `config.yml: budgets.compress`.

## Cross-references

- `prompts/ralph-meta-chain/05-compress.md`
- `prompts/ralph-meta-chain/scripts/ralph_context_compress.sh`
- `docs/MEMORY_MODEL.md` — hot/warm/cold/frozen layers + thresholds
