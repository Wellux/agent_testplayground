---
description: |
  Triggers: "ralph memory", "today's memory", "what got promoted overnight",
  "open the memory panel"
allowed-tools:
  - "Read"
  - "Bash(grep:*,find:*,wc:*,jq:*,git status,git log:*)"
---

# /ralph-memory

Open the daily memory report and the most-recent atomic-note promotions.
Read-only; LOW risk.

## Inputs

`$ARGUMENTS` — optional. If empty, defaults to "today". Acceptable
values: `today` | `yesterday` | `this-week` | a single ISO date
(`YYYY-MM-DD`).

## Process

1. Read `$VAULT/06_Reports/daily-memory-report.md` (or the dated
   archive entry that matches `$ARGUMENTS`).
2. Read `$VAULT/90-Meta/log.md` and grep for the `## [<date>] memory |`
   line.
3. List the most-recent files written under `$VAULT/30-Notes/` (use
   `find … -newer` against the report timestamp).
4. List any open hypotheses tagged `axis: memory` from
   `$VAULT/30-Notes/<id>-hypothesis-*.md`.

## Output

Render a single Markdown report with sections:

- **Counts** (today's `## [<date>] memory |` line)
- **Promotions** (with `[[wikilinks]]`)
- **Open hypotheses**
- **Orphans flagged**
- **Next-day recommendations**

## Safety

Read-only. Never edits. Re-running is a no-op.

## Cross-references

- `prompts/ralph-meta-chain/01-memory-optimizer.md`
- `vault-template/06_Reports/daily-memory-report.md`
- `docs/MEMORY_MODEL.md`
