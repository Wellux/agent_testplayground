---
ralph_type: business
memory_layer: business
risk_class_default: MEDIUM
created: 2026-05-09
status: scaffold
summary: "Prepare invoice DRAFTS only. Sending and recording payment are NEVER autonomous."
---

# Invoice Preparation

Drafts invoices internally. Never sends, never records actual payment.

## Purpose

Given a client engagement with delivered work, produce an invoice
draft with line items, totals, and a one-line summary — ready for the
user to review, finalize, and send via their own invoicing tool /
accounting system.

## Inputs

- `business-entity/clients/<slug>/deliverables/` (the work done)
- `business-entity/clients/<slug>/proposal.md` (pricing reference)
- `business-entity/ledgers/commitments.md` (committed scope + price)
- optional: `business-entity/clients/<slug>/prior-invoices/` for
  numbering continuity

## Process

1. Read deliverables; map each to a line item.
2. Read proposal + commitments; cross-check line-item pricing.
3. Compute subtotal + tax (if applicable; default: NO tax — the user
   adds it in their accounting tool).
4. Render the invoice draft to
   `business-entity/clients/<slug>/invoices/<YYYY-MM>-<seq>.md`.
5. Append to `ledgers/commitments.md` (status: invoice-drafted).
6. Append HIGH approval to `ledgers/pending-approvals.md`: "Send
   invoice to <counterparty>".
7. **Refuse to send.** Refuse to record payment.

## Outputs

- `business-entity/clients/<slug>/invoices/<YYYY-MM>-<seq>.md` (draft)
- `ledgers/commitments.md` (append)
- `ledgers/pending-approvals.md` (append, HIGH gate)

## Approval gates

| Step | Class    | Gate                                              |
| ---- | -------- | ------------------------------------------------- |
| 1-4  | MEDIUM    | proposal-first (the draft IS the proposal)         |
| 5    | MEDIUM    | ledger append                                      |
| 6    | HIGH      | explicit user approval to send                     |
| 7    | CRITICAL  | sending the invoice is NEVER autonomous            |
| —    | CRITICAL  | recording a payment is NEVER autonomous (NEVER human-or-cron; the user uses their accounting tool) |

## Risk notes

- **Number off**: a wrong amount sent externally is hard to undo.
  Mitigation: Ralph cross-checks against `commitments.md` and refuses
  if the proposal price and the deliverables don't reconcile.
- **Tax**: Ralph never computes tax autonomously. User computes via
  their accounting tool / bookkeeper.
- **Currency**: Ralph carries through the currency from the proposal;
  refuses to convert.
- **Banking details**: NOT in the draft. The user's accounting tool
  injects these at send time. Ralph never touches banking details.

## Ledger update requirements

| Trigger                                  | Append to                              |
| ---------------------------------------- | -------------------------------------- |
| invoice drafted                          | `ledgers/commitments.md` (status drafted) |
| approval requested                        | `ledgers/pending-approvals.md`         |
| approval granted                          | `ledgers/decisions.md`                  |
| external send happens                    | `ledgers/external-communications.md` + `ledgers/audit-log.md` + `ledgers/financial-actions.md` (send-event only; payment is human) |
| payment received                         | NOT a Ralph operation; user logs in `ledgers/financial-actions.md` manually |

## Example output (excerpt of invoice draft)

```markdown
# Invoice — Acme Corp · 2026-05-001 (DRAFT)

> **DRAFT.** Send via your accounting tool. Banking details are NOT in
> this file. Currency: USD.

| Description                        | Qty  | Rate     | Amount     |
| ---------------------------------- | ---- | -------- | ---------- |
| Internal docs sprint 1 (8h × $X)   | 8    | $X       | $8X        |
| Internal docs sprint 2 (6h × $X)   | 6    | $X       | $6X        |
| **Subtotal**                       |      |          | $14X       |
| Tax (added by user in accounting tool) |  |          | TBD        |
| **Total (before tax)**              |      |          | $14X       |

## Reconciliation
- proposal scope: <link>
- commitments: <[[<commitment-id>]]>, <[[<commitment-id>]]>
- deliverables: <[[<deliverable>]]>, ...
```

## Cross-references

- `workflows/proposal-drafting.md` — upstream commitment.
- `ledgers/financial-actions.md` — where payments LATER get logged (by user).
- `governance/approval-gates.md` § Sends + Never autonomous.

## Next actions

- Review the draft. Open it. Read every line item. Cross-check the
  total against the proposal. Then OPEN YOUR ACCOUNTING TOOL and create
  the actual invoice there. Ralph stops here.
