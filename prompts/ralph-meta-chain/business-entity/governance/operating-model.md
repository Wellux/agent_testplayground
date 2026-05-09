---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: scaffold
summary: "What this business does, who it serves, what Ralph does for it."
---

# Operating Model

> **Authoring template.** Fill in the project-specific blanks; the
> structure is canonical so cron prompts can read this consistently.

## What this entity does

(One paragraph: the value the business creates. Replace with your
domain. Example: "We deliver async knowledge work — research briefs,
technical writing, and architecture review — to a small set of long-
term clients.")

## Who it serves

| Segment            | Description                                          | Active? |
| ------------------ | ---------------------------------------------------- | ------- |
| (segment 1)        | (one-line description)                                | yes     |
| (segment 2)        | (one-line description)                                | (no)    |

## How Ralph helps

Ralph **drafts and organizes** these workflows (one workflow file each
in `business-entity/workflows/`):

- Lead intake from inbox / voice captures.
- Proposal drafting from `business-entity/templates/offer-template.md`.
- Invoice preparation (DRAFT ONLY).
- Client follow-up drafts.
- Knowledge-work delivery checklists.
- Vendor comparisons.
- Meeting summaries.
- Offer reviews (internal).
- Task delegation drafts.

Ralph **never autonomously**:

- sends client communications,
- signs contracts,
- makes / accepts payments,
- accesses bank / accounting / payroll,
- accesses CRM / email / calendar without explicit per-system scope,
- purchases software or services,
- hires or fires,
- makes regulated professional claims (legal, medical, financial).

See `governance/approval-gates.md` for the full matrix.

## Approval surfaces

Every Ralph-initiated action lands in one of:

- `ledgers/decisions.md` — choices made.
- `ledgers/commitments.md` — promises made or proposed.
- `ledgers/pending-approvals.md` — awaiting human OK.
- `ledgers/audit-log.md` — append-only timestamped trail.
- `ledgers/external-communications.md` — anything sent outside the entity.
- `ledgers/financial-actions.md` — financial-class actions (always human).
- `ledgers/legal-actions.md` — legal-class actions (always human).

## Cadence

Operating-model review: quarterly (the autoevolve cron flags this if
`updated:` is > 90 days old).

## Cross-references

- `governance/human-in-the-loop-policy.md` — where Ralph stops.
- `governance/approval-gates.md` — risk-class matrix.
- `governance/delegated-authority-matrix.md` — who approves what.
- `docs/BUSINESS_ENTITY_SCOPE.md` — master spec.

## Next actions

- Replace placeholder text with project-specific content.
- Add at least one segment row.
- Confirm the "Ralph never autonomously" list matches your risk
  posture. Adding new "never" rules is LOW risk; removing one is HIGH
  risk per `docs/APPROVAL_GATES.md`.
