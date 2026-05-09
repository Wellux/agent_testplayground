---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: active
summary: "Append-only ledger of every legal-class action. ALWAYS HUMAN."
---

# Legal Actions Ledger

> **Append-only. ALWAYS HUMAN.** Per `governance/approval-gates.md` §
> Never autonomous, every entry here is created by the user (or the
> user's counsel), not by Ralph. The chain surfaces candidates and
> drafts review notes; the user records the action.

## Why human-only

Legal actions create binding obligations. Per
`docs/BUSINESS_ENTITY_SCOPE.md`, Ralph never:

- signs contracts,
- makes legal claims (legal advice, professional certification),
- binds the user or company legally,
- responds to legal demands (subpoenas, GDPR requests, etc.).

Ralph drafts and surfaces; the user (or counsel) acts.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: legal-action
ts: <ISO_TS>
actor: user@<host>      # always a human
action: contract-signed | nda-signed | gdpr-request-fulfilled | gdpr-request-received | legal-notice-sent | legal-notice-received | filing-submitted | counsel-engaged | dispute-opened | dispute-closed
counterparty: <name>
counterparty_subject_id: <gdpr-pseudonym>
jurisdiction: <country/region>
external_reference: <contract-id | filing-id | matter-number>
counsel_engaged: <name>      # if applicable
related: ["[[<commitment-id>]]", "[[<offer-review>]]", "[[<approval-id>]]"]
audit_log_ref: "[[<audit-log-id>]]"
retention_class: standard | legal-hold | indefinite
---

# <Action title>

## What
<verb + object + counterparty>

## When
<ISO_TS>

## How
- counsel: <name + firm>
- tool: <e-signature-tool | filing-system | manual>
- external reference: <id>

## Document hashes
For contracts and signed agreements, store the SHA256 of the executed
PDF here so future tampering attempts are detectable. The PDF lives
outside the vault (encrypted document store).

- pdf_sha256: <hex>
- counterparty_acknowledged_at: <ISO_TS>

## Retention class
- standard: per default retention.
- legal-hold: never erase until counsel releases.
- indefinite: kept forever.
```

## Active matters

(contract-signed, nda-signed, dispute-opened with status open)

## Closed matters

(dispute-closed; counsel engagement ended)

## GDPR-driven actions

(gdpr-request-fulfilled / received — separate section because they
have specific timeline obligations)

## Counsel engagements

Track who you engaged, when, and for what. The autoupdate cron can
surface dormant engagements (no contact in > 90 days) for review.

## Cross-references

- `workflows/offer-review.md` — pre-signing review.
- `governance/risk-register.md` § Legal/financial risks.
- `governance/gdpr-data-map.md` § Right-to-erasure procedure.
- `ledgers/audit-log.md` — cross-cut audit trail.
- `ledgers/financial-actions.md` — when legal action involves money.
