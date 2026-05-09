---
ralph_type: business
memory_layer: business
risk_class_default: LOW
created: 2026-05-09
status: scaffold
summary: "Capture a new lead from inbox / voice and classify it."
---

# Lead Intake

The simplest workflow — captures a new lead and classifies it. Pure
internal; everything is LOW-risk.

## Purpose

When a new prospect lands (via voice capture, inbox text, or manual
entry), produce a structured lead record + initial classification +
suggested next step.

## Inputs

- raw text or voice transcript (in `00-Inbox/voice-<UTC>.md` or
  `01_Inbox/Daily Capture.md` below the `## Today` separator)
- optional: known counterparty name / domain
- optional: source (referral, inbound, RFP, …)

## Process

1. Read inbox item; identify likely lead.
2. Extract: counterparty name, role, ask, urgency, fit.
3. Classify: stage (`new | qualified | engaged | won | lost`),
   priority (`low | medium | high`), domain alignment (1-5).
4. Draft a lead record at
   `business-entity/clients/<slug>/brief.md` (using
   `templates/client-brief-template.md`).
5. Append to `ledgers/decisions.md` with the classification.
6. Suggest next step (one sentence) and append to
   `ledgers/pending-approvals.md` IF the next step is non-LOW
   (e.g. drafting a proposal).
7. Tag the original inbox item `#lead` and let the memory pass
   promote it.

## Outputs

- `business-entity/clients/<slug>/brief.md` (new file)
- `ledgers/decisions.md` (append)
- `ledgers/pending-approvals.md` (append IF non-LOW next step)

## Approval gates

| Step | Class  | Gate                                              |
| ---- | ------ | ------------------------------------------------- |
| 1-3  | LOW    | always allowed                                     |
| 4    | LOW    | always allowed (internal note)                     |
| 5    | LOW    | append-only ledger                                  |
| 6    | LOW (if next step LOW) / MEDIUM (else) | proposal-first |
| 7    | LOW    | tag-only                                            |

## Risk notes

- **Privacy**: counterparty name + ask are `privacy: client`. Never
  surface in cron-output reports or `90-Meta/log.md` summaries.
- **Misclassification**: a lead marked `priority: high` triggers
  proposal-drafting; if mis-classified, that's wasted work but not
  irreversible.

## Ledger update requirements

| Trigger                                                     | Append to                              |
| ----------------------------------------------------------- | -------------------------------------- |
| classification done                                         | `ledgers/decisions.md`                 |
| non-LOW next step proposed                                  | `ledgers/pending-approvals.md`         |
| follow-up workflow triggered                                | `ledgers/commitments.md`               |

## Example output

```markdown
# Lead: Acme Corp (subject-001)

- counterparty: Acme Corp
- role: VP Eng
- ask: technical writing for their internal docs
- urgency: low (no deadline)
- fit: 4/5 (matches our domain)
- stage: qualified
- priority: medium
- next step: draft a proposal (proposal-drafting workflow) — gated
```

## Cross-references

- `templates/client-brief-template.md` — format the brief uses.
- `workflows/proposal-drafting.md` — typical follow-up.
- `ledgers/decisions.md`, `ledgers/pending-approvals.md`.
- `governance/gdpr-data-map.md` § Per-subject schema.

## Next actions

- This is the smallest workflow — start here when sanity-checking the
  full surface end-to-end.
- Once the lead has a brief, the proposal-drafting workflow takes
  over (HIGH risk for external send).
