---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: scaffold
summary: "Auditability invariants for every business-entity operation."
---

# Audit Policy

The chain's append-only invariant means every action leaves a trail.
This policy says exactly which trails matter and how they're shaped.

## Invariants

1. **Every mutation appends to at least one ledger.**
2. **Append-only.** No ledger entry is ever rewritten or deleted; status
   field changes (`open → approved → applied`) are themselves append
   operations on a `## Ralph YYYY-MM-DD` block.
3. **Timestamps are UTC ISO-8601** (`2026-05-09T12:34:56+00:00`).
4. **Linkage is mandatory.** Every entry references at least one other
   ledger entry, proposal note, or workflow file via `[[wikilink]]`.
5. **Provenance is preserved.** Source = `manual | cron | plugin |
   harness | claude-code | import | migration | research`.

## Routing matrix

| Operation                                    | Logged in (ALL apply)                                |
| -------------------------------------------- | ---------------------------------------------------- |
| MEDIUM business draft                        | `ledgers/decisions.md`                               |
| MEDIUM commitment draft                      | `ledgers/commitments.md` (status: drafted)           |
| HIGH approval requested                      | `ledgers/pending-approvals.md`                       |
| HIGH approval granted                        | move from pending → `ledgers/decisions.md` (or commitments) |
| HIGH approval rejected                       | append to source proposal w/ `status: rejected`      |
| CRITICAL external communication              | `ledgers/external-communications.md` AND `ledgers/audit-log.md` |
| CRITICAL financial action                    | `ledgers/financial-actions.md` AND `ledgers/audit-log.md` |
| CRITICAL legal action                         | `ledgers/legal-actions.md` AND `ledgers/audit-log.md` |
| any rollback                                  | append-only `## Rollback YYYY-MM-DD` block to original entry; audit-log too |

The `audit-log.md` is the cross-cut log — every CRITICAL action
appears there in addition to its workflow-specific ledger.

## Required artifacts per CRITICAL apply

Per `docs/APPROVAL_GATES.md`, four artifacts must exist:

1. **Proposal note** in `30-Notes/<id>-<workflow>-<topic>.md` with
   `status: approved` AND `approver:` AND `approved_at:`.
2. **Audit-log entry** in `ledgers/audit-log.md` written BEFORE the apply.
3. **Ledger-specific entry** in
   `ledgers/{external-communications,financial-actions,legal-actions}.md`.
4. **Rollback plan** referenced by both proposal and audit entries.

If any of the four is missing, the apply refuses (Round 5+
`harness apply --proposal <id>` enforces this).

## Audit log entry shape

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
```

## Reviewing the trail

```bash
# Most-recent 50 audit entries
harness traces --tail 50 --axis interaction --filter audit  # Round 5+
```

For now (Round 1-3), open `ledgers/audit-log.md` directly.

## Tampering signals

If the audit-log's last entry's `diff_sha256` doesn't match the
current Markdown of the artifact it references, autoheal flags it as
ERROR severity and escalates to `60-Interactions/escalations.md`. The
chain refuses further CRITICAL applies until the user resolves.

## Cross-references

- `docs/APPROVAL_GATES.md` — risk classes.
- `governance/approval-gates.md` — business-specific matrix.
- `ledgers/audit-log.md` — the SOT.
- `docs/SECURITY_PRIVACY.md` § Audit — repo-wide audit guarantees.

## Next actions

- Audit policy is canonical; rarely needs editing.
- If you add a new CRITICAL operation type, add a routing row above
  AND a corresponding gate row in `governance/approval-gates.md`.
