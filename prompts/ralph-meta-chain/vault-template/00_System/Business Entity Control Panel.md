---
ralph_type: system
memory_layer: business
memory_temperature: hot
created: 2026-05-09
status: scaffold
summary: "Top-level dashboard for the business-entity layer (Round 3+)."
---

# Business Entity Control Panel

> **Status:** SCAFFOLD ONLY. Per `docs/BUSINESS_ENTITY_SCOPE.md`,
> Ralph drafts/organizes business workflows; it never autonomously
> sends, signs, pays, or accepts. Round 3 ships the full
> `business-entity/` Markdown tree; Round 1-2 only set up this panel.

## Pending approvals

(routed from `business-entity/ledgers/pending-approvals.md` once Round 3
lands)

## Open commitments

(routed from `business-entity/ledgers/commitments.md`)

## Recent decisions

(routed from `business-entity/ledgers/decisions.md`)

## Workflows

(routed from `business-entity/workflows/`):

- Lead intake
- Proposal drafting
- Invoice preparation (DRAFT ONLY)
- Client follow-up (DRAFT ONLY)
- Knowledge-work delivery
- Vendor comparison
- Meeting summary
- Offer review
- Task delegation

## Hard rules (mirrored from `docs/BUSINESS_ENTITY_SCOPE.md`)

Ralph **MAY** draft, summarize, classify, prepare, structure, and
maintain ledgers.

Ralph **MAY NOT** autonomously:

- sign contracts,
- send offers / invoices externally,
- make or accept payments,
- bind the user or company legally,
- make tax filings,
- access bank / accounting / payroll systems,
- access CRM / email / calendar without explicit consent + scope,
- communicate with clients without per-message approval,
- purchase software or services,
- hire or fire,
- make regulated professional claims.

These are CRITICAL gates per `00_System/Approval Gates.md`. They stay
gated even with `approvalMode: auto-medium`.

## Cross-references

- `docs/BUSINESS_ENTITY_SCOPE.md` — full scope contract.
- `docs/GOVERNANCE.md` § Roles — single-user vs multi-user (deferred).
- `business-entity/` — Round 3 scaffold target.
- `07_Business/` — daily-use ledgers (to be linked from Round 3).
