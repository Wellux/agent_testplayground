---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: active
summary: "Append-only ledger of every financial-class action. ALWAYS HUMAN."
---

# Financial Actions Ledger

> **Append-only. ALWAYS HUMAN.** Per `governance/approval-gates.md` §
> Never autonomous, every entry here is created by the user, not by
> Ralph. The chain may surface candidates for human action; the user
> records the action.

## Why human-only

Financial actions touch the bank / accounting / payroll system. Per
`docs/BUSINESS_ENTITY_SCOPE.md`, Ralph never:

- accepts payment,
- makes payment,
- accesses banking,
- accesses accounting / payroll,
- makes tax filings.

Therefore Ralph cannot truthfully log financial actions — only the
user can, after performing them in their actual financial tool.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: financial-action
ts: <ISO_TS>
actor: user@<host>      # always a human
action: invoice-sent | payment-received | payment-made | refund-issued | refund-received | tax-filing | bank-transfer
amount: <decimal>
currency: <ISO-4217>
counterparty: <name>
counterparty_subject_id: <gdpr-pseudonym>
external_reference: <invoice-id | tx-id | filing-id>      # from accounting tool
related: ["[[<commitment-id>]]", "[[<external-communication-id>]]"]
audit_log_ref: "[[<audit-log-id>]]"
---

# <Action title>

## What
<verb + amount + currency + counterparty>

## When
<ISO_TS>

## How
- tool: <accounting-tool-name>
- external reference: <id>

## Tax / regulatory
- jurisdiction: <country/region>
- tax category: <if applicable>
- requires-1099 / similar: <if applicable>

## Reconciliation
- linked commitment: <[[<commitment-id>]]>
- reconciled-in-accounting: yes | no | partial
```

## Inflows (received)

(payment-received, refund-received)

## Outflows (sent)

(payment-made, refund-issued, tax-filing)

## Tax filings

(separate section — tax filings are HIGH-frequency-but-low-volume)

## Cross-references

- `workflows/invoice-preparation.md` — drafts only; user sends and
  records here after.
- `governance/approval-gates.md` § Never autonomous.
- `ledgers/audit-log.md` — cross-cut audit trail.
- `governance/gdpr-data-map.md` § Right-to-erasure procedure §
  legal-minimum retention.
