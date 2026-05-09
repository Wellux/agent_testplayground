---
ralph_type: business
memory_layer: business
created: 2026-05-09
status: scaffold
summary: "Append-only ledger of business decisions."
---

# Decision Ledger

> **Append-only.** Decisions are facts; once made, they live here
> forever. The autoevolve cron may propose revisiting a decision but
> never rewrites a logged entry.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: decision
created: <ISO_TS>
proposer: ralph-cron | user | ralph-plugin
status: proposed | committed | reversed
related: ["[[<related-note>]]"]
summary: "One-line decision."
---

# <Title>

## Decision
<one sentence>

## Context
<what led to this>

## Alternatives considered
- ...
- ...

## Reasoning
<why this over alternatives>

## Reversibility
- low | medium | high | irreversible

## Review date
<YYYY-MM-DD> — the autoevolve cron will surface this for review.
```

## Recent decisions

(append below — chronological)

## Cross-references

- `07_Business/approval-ledger.md` — for HIGH/CRITICAL approvals.
- `07_Business/commitment-ledger.md` — for binding commitments.
- `business-entity/ledgers/decisions.md` — Round 3 deeper version.
