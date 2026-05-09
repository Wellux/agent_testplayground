---
template_for: ledgers/pending-approvals.md
created: 2026-05-09
status: scaffold
summary: "Variable-slot approval-request form."
---

# Approval Request Template

Filled by any workflow that needs HIGH/CRITICAL approval. Lands in
`ledgers/pending-approvals.md`.

---

```yaml
---
id: {{approval_id}}            # YYYYMMDDHHMMSS
ledger: approval
created: {{created_at}}
proposer: {{proposer}}
risk_class: {{risk_class}}     # HIGH | CRITICAL
related:
  - "[[{{workflow_ref}}]]"
  - "[[{{commitment_or_proposal_ref}}]]"
status: pending
deadline: {{deadline_or_none}}
summary: "{{one_line}}"
---
```

# Approval — {{title}}

## What
{{what_paragraph}}

## Why
{{why_paragraph}}     # cite triggering note + risk

## Risk classification
- class: {{risk_class}}
- reversibility: {{reversibility}}     # low | medium | high | irreversible
- external visibility: {{external_visibility}}     # yes | no

## What I'll do if approved
{{if_approved_steps}}

## What I'll do if rejected
- archive draft to `_rejected/`
- append to source proposal `status: rejected`
- emit one-line note in `60-Interactions/escalations.md`

## Rollback (CRITICAL only)
{{rollback_plan_or_NA}}

## Audit reference
- audit_log_ref will be created BEFORE apply (per `governance/audit-policy.md`)
- proposal_ref: `[[{{proposal_id}}]]`

## How to approve
1. Read the workflow + triggering note.
2. Edit this entry's frontmatter:
   ```yaml
   status: approved
   approver: <user>
   approved_at: <ISO_TS>
   ```
3. The next cron firing (or `harness apply --proposal {{approval_id}}`
   in Round 5+) applies it.

## How to reject
1. Edit frontmatter:
   ```yaml
   status: rejected
   ```
2. Add a `## Rejected on YYYY-MM-DD` block with a one-line rationale.
3. The proposal is archived to `_rejected/`, never deleted.
