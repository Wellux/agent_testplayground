---
template_for: governance/risk-register.md
created: 2026-05-09
status: scaffold
summary: "Variable-slot risk-review form for periodic risk assessment."
---

# Risk Review Template

Used quarterly (or on demand) to assess a risk in
`governance/risk-register.md` and either confirm / adjust severity.
Output goes back into the risk-register as an updated entry (append-only).

---

# Risk Review — {{risk_id}} · {{review_date}}

## Risk under review
- id: `[[risk-register.md#{{risk_id}}]]`
- current severity: {{current_severity}}
- last reviewed: {{last_reviewed_date}}

## Trigger conditions check
For each trigger condition in the original entry, has it occurred
since last review?

| Trigger condition       | Occurred? | Frequency | Notes |
| ----------------------- | --------- | --------- | ----- |
| {{trigger_1}}             | yes / no  | {{n}}     | ...   |
| {{trigger_2}}             | yes / no  | {{n}}     | ...   |

## Mitigation effectiveness
For each mitigation, has it worked as intended?

| Mitigation              | Effective? | Evidence |
| ----------------------- | ---------- | -------- |
| {{mitigation_1}}          | yes / partial / no | {{evidence_link}} |

## Residual risk
- before this review: {{prev_residual}}
- proposed after this review: {{new_residual}}     # low | medium | high

## Likelihood update
- prev: {{prev_likelihood}}
- new: {{new_likelihood}}

## Impact update
- prev: {{prev_impact}}
- new: {{new_impact}}

## Severity (derived)
- prev: {{prev_severity}}
- new: {{new_severity}}     # use governance/risk-register.md severity table

## Action items
{{action_items_with_owner_and_due}}

## Approval
A severity DECREASE is HIGH-risk per `docs/APPROVAL_GATES.md`. A
severity INCREASE is MEDIUM (proposal-first). Decreasing severity
without approval is a CRITICAL violation.

- approver (if decreasing): {{user}}
- approved_at: {{approved_at}}

## Next review date
- {{next_review_date}}
