---
ralph_type: business
memory_layer: business
created: 2026-05-09
status: scaffold
summary: "Append-only ledger of every business approval (HIGH + CRITICAL)."
---

# Approval Ledger

> **Append-only. Round 3+ wired.** Every HIGH or CRITICAL business
> action requires an entry here BEFORE it's applied.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: approval
created: <ISO_TS>
proposer: ralph-cron-<axis> | ralph-plugin | user
risk_class: HIGH | CRITICAL
related: ["[[<workflow>]]", "[[<commitment-id>]]"]
status: pending | approved | rejected | applied | rolled-back
summary: "One-line"
---

# <Title>

## What
...

## Why
...

## Approval
- approver: <user>
- approved_at: <ISO_TS>
- method: explicit | overridden

## Action
- action_taken: <description>
- action_at: <ISO_TS>

## Rollback (CRITICAL only)
<plan>
```

## Open approvals

(populated by Round 3 — empty in Round 2)

## Resolved approvals

(append below — never delete)

## Cross-references

- `docs/APPROVAL_GATES.md` § Business entity.
- `00_System/Approval Gates.md`.
- `07_Business/decision-ledger.md` — for non-approval decisions.
- `07_Business/audit-log.md` — broader audit trail.
- `business-entity/ledgers/pending-approvals.md` — Round 3 deeper version.
