---
template_for: workflow:proposal-drafting
created: 2026-05-09
status: scaffold
summary: "Variable-slot offer template used by proposal-drafting."
---

# Offer Template

Variables in `{{ }}` are filled by the proposal-drafting workflow. Edit
the template body to match your voice; the cron prompt reads it
verbatim.

## Source-of-truth rule

Every concrete claim below MUST be traceable to either:
- a sentence in `business-entity/clients/<slug>/brief.md`, or
- a fact in `business-entity/governance/operating-model.md`.

Anything not traceable gets flagged `(uncited)` so the user can resolve
before approving the send.

---

# Proposal — {{counterparty}} · {{engagement_name}}

> **Status: DRAFT — internal only. Sending requires HIGH approval per
> `governance/approval-gates.md`.**

## Engagement summary
We propose {{scope_summary}} over {{timeline_summary}}, delivering
{{deliverables_summary}}.

## Scope (from brief)
{{scope_bullets}}

## Out of scope
{{out_of_scope_bullets}}

## Approach
{{approach_paragraph}}

## Timeline (proposed; not yet committed)
{{timeline_table}}

## Deliverables
{{deliverables_table}}

## Pricing (proposed)
{{pricing_table}}

## Acceptance criteria
{{acceptance_bullets}}

## Open questions (need counterparty input)
{{open_questions_bullets}}

## Provenance
- brief: `[[business-entity/clients/{{slug}}/brief.md]]`
- operating-model: `[[business-entity/governance/operating-model.md]]`
- prior proposals consulted: {{prior_proposals_links}}
- uncited claims: {{uncited_count}}

## Approval
- approver: {{user}}
- approved_at: {{approved_at}}
- next-step: send via {{channel}} (CRITICAL — manual)
