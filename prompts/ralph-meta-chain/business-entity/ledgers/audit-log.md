---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: active
summary: "Append-only timestamped record of every CRITICAL business action."
---

# Audit Log

> **Append-only.** The cross-cut log of every CRITICAL action. Per
> `governance/audit-policy.md`, entries here are mandatory BEFORE any
> CRITICAL apply (not after).

## Schema

```yaml
---
id: <YYYYMMDDHHMMSS>
ledger: audit
ts: <ISO_TS>
actor: ralph-cron-<axis> | ralph-plugin | user@<host>
operation: <verb noun>
risk_class: HIGH | CRITICAL
proposal_ref: "[[<proposal-id>]]"
artifacts:
  - "[[<ledger-entry>]]"
  - "[[<rollback-plan>]]"
diff_sha256: <hex>     # of the resulting Markdown after apply
---

# <Action title>

## What
<verb + object>

## Why
<one sentence>

## Approval reference
- approver: <user>
- approved_at: <ISO_TS>
- method: explicit | overridden

## Result
- action_taken: <description>
- action_at: <ISO_TS>
- artifacts_produced: <[[<artifact>]]>, ...

## Rollback (CRITICAL only)
<plan>

## Tampering check
- diff_sha256: <hex>
```

## Open

(audit entries created BEFORE the apply; status: pending-apply)

## Applied

(once the action runs; updated with result + diff_sha256)

## Rolled back

(append-only `## Rollback YYYY-MM-DD` block to the original entry; do
NOT remove the original)

## Tampering signals

If the audit-log's last entry's `diff_sha256` doesn't match the
current Markdown of the artifact it references, autoheal flags ERROR
severity and refuses further CRITICAL applies until the user
resolves.

## Cross-references

- `governance/audit-policy.md` § Routing matrix.
- `ledgers/external-communications.md`, `financial-actions.md`,
  `legal-actions.md` — workflow-specific ledgers (audit-log is the
  cross-cut).
- `docs/SECURITY_PRIVACY.md` § Audit guarantees.
