---
template_for: workflow:task-delegation
created: 2026-05-09
status: scaffold
summary: "Variable-slot task delegation form."
---

# Task Delegation Template

Filled by the task-delegation workflow. Internal-only; sending the
delegation externally is CRITICAL.

---

# Delegation — {{topic}} · {{date}}

> **privacy: {{privacy}}** (often inherits from client engagement)

## Delegator
- {{delegator}}     # the user

## Delegate
- name: {{delegate_name}}
- role: {{delegate_role}}
- compensation context: {{compensation_context}}     # link to existing engagement; never new payment authorization

## Scope
{{scope_paragraph}}

## Acceptance criteria
{{acceptance_bullets}}

## Deadline
- {{deadline}} ({{timezone}})

## Dependencies
{{dependencies_bullets}}

## Risks
{{risks_bullets}}

## Handoff artifacts
{{handoff_artifacts_links}}

## Acknowledgment expected
{{acknowledgment_format}}

## Approval (if external + paid)
- approver: {{user}}
- approved_at: {{approved_at}}
- approval_id: `[[pending-approvals.md#{{approval_id}}]]`

## Cross-refs
- commitment: `[[commitments.md#{{commitment_id}}]]`
- client engagement: `[[business-entity/clients/{{slug}}/brief.md]]`
