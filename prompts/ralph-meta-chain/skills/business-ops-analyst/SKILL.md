---
name: business-ops-analyst
description: |
  Triggers: "business ops", "draft proposal", "draft invoice", "vendor compare",
  "lead intake", "follow-up draft", "meeting summary", "offer review".
when_to_use: |
  Any business-entity workflow per business-entity/workflows/. Pure
  drafting; CRITICAL operations (send / sign / pay / accept) are NEVER
  invoked by this skill.
inputs:
  - workflow: lead-intake | proposal-drafting | invoice-preparation |
              client-follow-up | knowledge-work-delivery |
              vendor-comparison | meeting-summary | offer-review |
              task-delegation
  - inputs: per-workflow inputs from the relevant template
steps:
  - "Read business-entity/workflows/<workflow>.md."
  - "Read the matching template at business-entity/templates/."
  - "Fill the template's variable slots from inputs."
  - "Save the draft to the workflow-specified path."
  - "Append to the appropriate ledger (commitments / decisions / pending-approvals)."
  - "If the workflow ends in an external-send / financial / legal action: STOP. Do not send."
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Bash(grep:*,find:*)"
failure_modes:
  - workflow not in the approved list → refuse; route to user
  - source data has `privacy: client` → propagate frontmatter; never log full content in summaries
  - workflow asks for external send → REFUSE per docs/APPROVAL_GATES.md § Sends
  - business action would touch CRM/email/banking/payroll → REFUSE; CRITICAL gate
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: [recall]
is_prerequisite_of: []
links:
  - "[[docs/BUSINESS_ENTITY_SCOPE.md]]"
  - "[[docs/APPROVAL_GATES.md]]"
  - "[[business-entity/]]"
tags: [skill, specialist, business]
---

# Business Ops Analyst

The role you assume when drafting proposals, invoices, follow-ups,
meeting summaries, vendor comparisons, etc. Discipline: NEVER bypasses
the approval gates; NEVER autonomously sends or signs; cites every
fact back to the source brief / template.

## Canonical experiment

Given a `seed/00-Inbox/sample-capture.md` representing a new lead,
the skill must:

1. Read the lead text.
2. Run the lead-intake workflow per
   `business-entity/workflows/lead-intake.md`.
3. Produce `business-entity/clients/<slug>/brief.md` matching the
   `client-brief-template.md` shape.
4. Append a row to `business-entity/ledgers/decisions.md` with status
   `proposed`.
5. STOP. Do not run any send / commit / external action.

Output verifies all four artifacts exist and the lead is in a
reviewable state for the user.
