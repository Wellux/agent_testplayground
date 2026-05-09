---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: active
summary: "Append-only ledger of every business decision."
---

# Decisions Ledger

> **Append-only.** Decisions are facts; once made, they live here
> forever. The autoevolve cron may propose revisiting a decision but
> never rewrites a logged entry.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: decision
created: <ISO_TS>
proposer: ralph-cron-<axis> | ralph-plugin | user
status: proposed | committed | reversed
risk_class: LOW | MEDIUM | HIGH | CRITICAL
related: ["[[<related-note>]]", "[[<other-ledger-id>]]"]
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

## Open / pending decisions

(committed via append below)

## Recent decisions

(append below — chronological)

## Reversed decisions

When reversing, append a NEW entry with `status: reversed` and a
`related: [[<original-id>]]`. The original entry stays in place; the
chain treats both as historical record.

## Cross-references

- `ledgers/pending-approvals.md` — for HIGH/CRITICAL approvals.
- `ledgers/commitments.md` — for binding commitments.
- `ledgers/audit-log.md` — for the cross-cut audit trail.
- `governance/audit-policy.md` § Routing matrix.
