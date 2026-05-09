---
ralph_type: business
memory_layer: business
created: 2026-05-09
status: scaffold
summary: "Operating model summary — what the business does, who it serves, what Ralph does for it."
---

# Operating Model

> **Round 3+ scaffold.** Round 1-2 only outline the surface; Round 3
> populates the full `business-entity/governance/operating-model.md`.

## What the business does

(fill in: services / products / value proposition)

## Who it serves

(fill in: client segments / market)

## How Ralph helps

Ralph **drafts and organizes**:

- Lead intake from inbox / voice captures.
- Proposal drafts from templates.
- Invoice drafts (never sent autonomously).
- Client follow-up drafts.
- Vendor comparisons.
- Meeting summaries.
- Internal SOPs.

Ralph **never autonomously**:

- Sends client communications.
- Signs contracts.
- Makes / accepts payments.
- Accesses external systems (CRM / banking / email / calendar)
  without explicit per-system authorization.

See `docs/BUSINESS_ENTITY_SCOPE.md` for the full list.

## Approval responsibilities

| Role            | Approves                                    |
| --------------- | ------------------------------------------- |
| Owner (default) | every class up to CRITICAL                   |
| Operator         | LOW + MEDIUM autonomously; HIGH with co-sign |
| Auditor          | read-only; can challenge any approval        |

(Single-user mode: user holds all roles. Multi-user: deferred.)

## Cross-references

- `docs/BUSINESS_ENTITY_SCOPE.md` — full scope contract.
- `docs/GOVERNANCE.md` — risk classes.
- `00_System/Business Entity Control Panel.md` — dashboard.
- `business-entity/governance/operating-model.md` — Round 3 deeper version.
