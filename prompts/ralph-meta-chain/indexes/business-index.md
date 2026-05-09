---
ralph_type: system
memory_layer: business
created: 2026-05-09
status: template
target: $VAULT/00_System/Business Entity Control Panel.md
summary: "Business-entity ledgers + workflow status + open approvals."
---

# Business Index — TEMPLATE

The runtime mirror lives at
`$VAULT/00_System/Business Entity Control Panel.md`. Round 3+ cron
passes will populate it; for now this template documents the shape.

## Pending approvals

| Id              | Created    | Risk      | Subject                  | Action                |
| --------------- | ---------- | --------- | ------------------------ | --------------------- |
| `<id>`          | YYYY-MM-DD | HIGH      | Send proposal to <X>     | review + approve      |

## Open commitments (external)

| Id              | Counterparty   | Due        | Status              |
| --------------- | -------------- | ---------- | ------------------- |
| `<id>`          | `<name>`        | YYYY-MM-DD | drafted / approved / sent |

## Recent decisions

| Id              | Subject                         | Decided on  | Reversibility |
| --------------- | ------------------------------- | ----------- | ------------- |
| `<id>`          | `<one-line>`                     | YYYY-MM-DD  | low / med / high / irreversible |

## Workflow status

| Workflow                       | Active drafts | Pending approval | This week's count |
| ------------------------------ | ------------- | ---------------- | ------------------ |
| lead-intake                     | N             | N                | N                  |
| proposal-drafting               | N             | N                | N                  |
| invoice-preparation             | N             | N                | N                  |
| client-follow-up                | N             | N                | N                  |
| knowledge-work-delivery         | N             | N                | N                  |
| vendor-comparison               | N             | N                | N                  |
| meeting-summary                 | N             | N                | N                  |
| offer-review                    | N             | N                | N                  |
| task-delegation                 | N             | N                | N                  |

## Risk register (top 5 by severity)

| Risk                          | Severity   | Status     | Owner   |
| ----------------------------- | ---------- | ---------- | ------- |
| `<id>-<slug>`                  | critical   | mitigated  | owner   |

(See `business-entity/governance/risk-register.md` for full register.)

## Hard rules (mirror)

Per `docs/BUSINESS_ENTITY_SCOPE.md`:

- Ralph **MAY** draft / classify / summarize / structure / maintain ledgers.
- Ralph **MAY NOT** autonomously: send / sign / pay / accept / access
  CRM/banking/payroll without explicit per-system scope / hire / fire /
  make regulated professional claims.

## Cross-references

- `business-entity/README.md`.
- `business-entity/ledgers/{decisions,commitments,pending-approvals,
  audit-log,external-communications,financial-actions,legal-actions}.md`.
- `business-entity/governance/risk-register.md`.
- `vault-template/00_System/Business Entity Control Panel.md`.
- `docs/BUSINESS_ENTITY_SCOPE.md`.
