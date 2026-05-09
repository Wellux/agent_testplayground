---
template_for: workflow:lead-intake
created: 2026-05-09
status: scaffold
summary: "Variable-slot client brief used by lead-intake."
---

# Client Brief Template

Filled by the lead-intake workflow.

---

# Client Brief — {{counterparty}} ({{subject_id}})

> **privacy: client.** HIGH risk to edit per
> `docs/APPROVAL_GATES.md` § Memory operations.

## Counterparty
- name: {{counterparty}}
- subject_id: {{subject_id}}     # gdpr pseudonym
- domain: {{domain}}
- contact role: {{role}}

## Source
- channel: {{capture_channel}}
- captured_at: {{captured_at}}
- inbox_ref: `[[{{inbox_capture_id}}]]`

## Ask
{{ask_paragraph}}

## Stage
- {{stage}}     # new | qualified | engaged | won | lost

## Priority
- {{priority}}   # low | medium | high

## Domain alignment (1-5)
- {{alignment_score}}

## Urgency
- {{urgency}}    # rush | this-quarter | this-year | open

## Fit notes
{{fit_notes_bullets}}

## Constraints (from counterparty)
{{constraints_bullets}}

## Suggested next step
{{next_step_one_line}}

## History
- prior engagements: {{prior_engagements_links}}

## Confidentiality
- nda in place: yes | no | requested

## GDPR
- consent: {{consent_status}}
- consent_captured_at: {{consent_at}}
- retention_window_days: {{retention_window_days}}
- data_categories: {{data_categories}}
