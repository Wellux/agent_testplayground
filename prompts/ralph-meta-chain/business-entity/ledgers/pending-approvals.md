---
ralph_type: business
memory_layer: business
memory_temperature: hot
stability: canonical
created: 2026-05-09
status: active
summary: "Live queue of pending approval requests (HIGH + CRITICAL)."
---

# Pending Approvals

> The Obsidian status bar shows the count of items here. Open + approve
> as part of the weekly review.

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: approval
created: <ISO_TS>
proposer: ralph-cron-<axis> | ralph-plugin | user
risk_class: HIGH | CRITICAL
related: ["[[<workflow>]]", "[[<commitment-id>]]", "[[<proposal-note>]]"]
status: pending | approved | rejected | applied | rolled-back
deadline: <YYYY-MM-DD>             # optional; if action time-sensitive
summary: "One-line"
---

# <Title>

## What
What action needs approval, in user-facing language.

## Why
Why now (cite triggering note + risk).

## Risk classification
- class: HIGH | CRITICAL
- reversibility: low | medium | high | irreversible
- external visibility: yes | no

## What I'll do if approved
- step 1
- step 2

## What I'll do if rejected
- archive draft to `_rejected/`
- append to source proposal `status: rejected`

## Rollback (CRITICAL only)
<plan>
```

## Open

(append below; sorted by `created` DESC)

## Resolved (approved + applied)

When the user marks approved AND the apply happens, the entry moves
here (append-only — original entry is mirrored, never modified).

## Resolved (rejected)

When the user marks rejected, the entry is mirrored here with the
rejection rationale.

## Cross-references

- `governance/approval-gates.md` § Approval mechanics.
- `governance/audit-policy.md` § Required artifacts per CRITICAL apply.
- `ledgers/decisions.md` — where approved entries also land.
- `ledgers/audit-log.md` — cross-cut audit trail.
- `vault-template/00_System/Ralph Control Panel.md` — counts open approvals.
