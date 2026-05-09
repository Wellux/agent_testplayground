---
template_for: workflow:meeting-summary
created: 2026-05-09
status: scaffold
summary: "Variable-slot meeting summary used by meeting-summary workflow."
---

# Meeting Summary Template

Filled by the meeting-summary workflow. Every quote / decision / action
item references the source transcript line range.

---

# Meeting — {{counterparty}} · {{date}} · "{{topic}}"

> **privacy: {{privacy}}** ({{privacy}} | client | private | work | public)

## Participants
{{participants_bullets}}

## Decisions
{{decisions_numbered_with_line_refs}}

## Action items
{{action_items_with_owner_and_due}}

## Open questions
{{open_questions_bullets}}

## Commitments identified
{{commitments_with_drafted_link}}     # cross-listed in ledgers/commitments.md

## Risks surfaced
{{risks_bullets}}

## Provenance
- Source transcript: `[[{{transcript_id}}]]`
- Lines cited: {{cited_line_ranges}}
- Speaker attribution confidence: {{attribution_confidence}}     # 0.0-1.0

## Uncertainty
- (uncertain attribution): {{uncertain_quotes_bullets}}
- missing context: {{missing_context_bullets}}

## Forwarding
- forwarded to participants: yes | no | partial
- forwarding logged in: `[[external-communications.md#{{external-comm-id}}]]`     # if yes
