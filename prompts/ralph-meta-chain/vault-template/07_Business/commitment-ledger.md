---
ralph_type: business
memory_layer: business
created: 2026-05-09
status: scaffold
summary: "Append-only ledger of commitments (internal + external)."
---

# Commitment Ledger

> **Append-only.** Tracks every commitment made or proposed — internal
> ("we'll prioritize this in Q3") and external ("we'll deliver X by
> 2026-06-15").

External commitments are CRITICAL: they bind the user / company. Per
`docs/APPROVAL_GATES.md`, sending a commitment externally is never
autonomous.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: commitment
created: <ISO_TS>
audience: internal | external
counterparty: <name or anon>     # if external
due_date: <YYYY-MM-DD>            # if applicable
status: drafted | pending-approval | approved | sent | fulfilled | breached | withdrawn
risk_class: MEDIUM | HIGH | CRITICAL
related: ["[[<workflow>]]"]
summary: "One-line commitment."
---

# <Title>

## What
<the commitment>

## To whom
<internal team / external counterparty>

## When
<due date>

## How fulfilled
<acceptance criteria>

## Approval (if external)
- approver: ...
- approved_at: ...

## Sent (if external)
- channel: <email | proposal-tool | manual>
- sent_at: ...
- copy_filed: <link to external-communications.md entry>
```

## Open commitments

(populated by Round 3 — empty in Round 2)

## Cross-references

- `07_Business/approval-ledger.md` — for HIGH/CRITICAL approvals.
- `07_Business/external-communications.md` — when the commitment is sent.
- `business-entity/ledgers/commitments.md` — Round 3 deeper version.
