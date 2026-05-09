---
description: |
  Triggers: "ralph evolve", "fitness report", "what should change", "evolution proposals",
  "weekly evolve"
allowed-tools:
  - "Read"
  - "Bash(harness:*,grep:*,find:*,wc:*,jq:*)"
---

# /ralph-evolve

Show the most recent weekly autoevolve pass: fitness scores per axis,
proposed mutations to prompts/skills/budgets, and any spawned
A/B-population entries that need user judgement before promotion. LOW
risk; read-only.

## Inputs

`$ARGUMENTS` — optional. Acceptable values:

- `latest` (default) — most recent weekly pass
- `this-month` — last 4 passes
- `axis:<name>` — filter to one axis (memory|skills|interaction|...|update)
- a single ISO date `YYYY-MM-DD`

## Process

1. Read `$VAULT/06_Reports/evolve-report-<date>.md` (latest if no arg).
2. Read `$VAULT/90-Meta/metrics.ndjson` for the trailing window
   (default 7d) and pull per-axis fitness deltas.
3. Read `$VAULT/30-Notes/<id>-evolve-proposal-*.md` for any proposals
   with `status: open` (not yet accepted/rejected).
4. List spawned population candidates from
   `$VAULT/50-Logs/ab/<axis>/population.ndjson` whose `winner` field
   is null (still pending).

## Output

Markdown report:

- **Per-axis fitness** (table: `axis | last week | this week | delta`).
- **Open proposals** — title, axis, [[wikilink]], rationale (1 line).
- **Pending population winners** — A/B variant pairs awaiting promotion.
- **Recommended action** — one sentence:
  - "no action; next pass is Sunday 05:00 UTC"
  - "axis X is regressing — review last proposal"
  - "N proposals open >7d — accept or reject before next pass"

## Safety

LOW risk. Read-only. The actual mutations are PROPOSALS — never
applied automatically; user accepts/rejects via
`harness evolve --accept <proposal-id>` (separate command). The
weekly pass owns its own budget cap (`evolve.max_proposals`).

## Cross-references

- `prompts/ralph-meta-chain/07-autoevolve.md`
- `docs/EVOLUTION_MODEL.md` — fitness contract + Voyager curriculum
- `prompts/ralph-meta-chain/benchmarks/` — scorecards used as input
