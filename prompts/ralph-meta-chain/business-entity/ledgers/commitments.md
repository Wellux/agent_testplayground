---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: active
summary: "Append-only ledger of commitments (internal + external)."
---

# Commitments Ledger

> **Append-only.** Tracks every commitment made or proposed —
> internal ("we'll prioritize this in Q3") and external ("we'll
> deliver X by 2026-06-15").
>
> External commitments are CRITICAL: they bind the user / company. Per
> `governance/approval-gates.md` § Sends, sending a commitment
> externally is never autonomous.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: commitment
created: <ISO_TS>
audience: internal | external
counterparty: <name or anon>     # if external
counterparty_subject_id: <gdpr-pseudonym>   # if external + privacy: client
due_date: <YYYY-MM-DD>            # if applicable
status: drafted | pending-approval | approved | sent | fulfilled | breached | withdrawn
risk_class: MEDIUM | HIGH | CRITICAL
related: ["[[<workflow>]]", "[[<proposal-note>]]"]
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

## Approval (if external + sent)
- approver: ...
- approved_at: ...

## Sent (if external)
- channel: <email | proposal-tool | manual>
- sent_at: ...
- copy_filed: <[[external-communications.md entry id]]>

## Fulfillment
- fulfilled_at: ...
- fulfilled_by: <delivery-checklist link>
- evidence: <[[<delivery-note>]]>
```

## Open commitments

(append below; status `drafted | pending-approval | approved | sent`)

## Fulfilled commitments

(status `fulfilled` or `withdrawn`)

## Breached commitments

(status `breached` — keep visible; never archive without explicit
approval)

## Cross-references

- `workflows/proposal-drafting.md`, `invoice-preparation.md`,
  `task-delegation.md`, `meeting-summary.md` — frequent producers.
- `ledgers/pending-approvals.md` — gate before status: sent.
- `ledgers/external-communications.md` — when status flips to sent.
- `governance/audit-policy.md` § Routing matrix.
