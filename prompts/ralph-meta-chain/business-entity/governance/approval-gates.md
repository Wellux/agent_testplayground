---
ralph_type: business
memory_layer: business
stability: canonical
created: 2026-05-09
status: scaffold
summary: "Business-entity-specific gate matrix (mirrors docs/APPROVAL_GATES.md § Business)."
---

# Approval Gates — Business Entity

Authoritative source: `docs/APPROVAL_GATES.md` § Business entity. This
copy is reproduced in the entity scaffold so cron prompts and human
operators see the same matrix without cross-folder navigation.

## Class shorthand

| Class    | Auto-applies?                  | Audit?                  |
| -------- | ------------------------------ | ----------------------- |
| LOW      | yes (within budget)             | log.md only             |
| MEDIUM   | yes (proposal recorded)         | log.md + state.json     |
| HIGH     | no                              | log + state + escalations |
| CRITICAL | no                              | log + state + audit + ledger + rollback |

## Operations

### Drafts (LOW / MEDIUM)

| Operation                                              | Class    |
| ------------------------------------------------------ | -------- |
| draft proposal (internal)                              | LOW      |
| draft client follow-up (internal)                       | LOW      |
| draft meeting summary                                   | LOW      |
| draft vendor comparison                                  | LOW      |
| draft internal SOP                                       | LOW      |
| draft invoice (internal — never sent autonomously)      | MEDIUM   |
| draft offer (internal)                                   | MEDIUM   |
| classify a lead                                          | LOW      |
| update an open commitment's status                       | MEDIUM   |

### Sends (CRITICAL)

| Operation                                              | Class    |
| ------------------------------------------------------ | -------- |
| send proposal externally                               | CRITICAL |
| send invoice externally                                 | CRITICAL |
| send offer externally                                   | CRITICAL |
| send any client follow-up externally                    | CRITICAL |
| respond to a vendor RFI externally                      | CRITICAL |
| make any binding commitment in writing                  | CRITICAL |

### Never autonomous

These are always human. Ralph refuses outright:

- accept payment
- make payment
- sign contract
- make tax filing
- access bank account
- access accounting / payroll system
- access CRM / email / calendar without explicit per-system scope
- communicate with clients without per-message approval
- purchase software / services
- hire or fire
- make regulated professional claims (legal / medical / financial advice)

The "Never autonomous" set is the spec's `CRITICAL: NEVER autonomous`
class. Even with `approvalMode: auto-medium` they refuse.

## Approval mechanics

Per the master spec, "approval" means one of:

- **MEDIUM** auto-apply: the chain writes a proposal note and
  proceeds; the audit-log entry references the proposal-id.
- **HIGH** explicit: the user edits the proposal note's frontmatter
  to `status: approved` AND triggers the apply (typically next cron
  firing or `harness apply --proposal <id>` in Round 5+).
- **CRITICAL** explicit + audit + rollback: same as HIGH plus
  - an entry in `ledgers/audit-log.md` BEFORE the apply,
  - a rollback plan in the proposal note,
  - the user sets `RALPH_BUSINESS_CRITICAL_APPROVED=<proposal-id>` in
    the env of the manual apply.

## Override mechanism

Documented in `docs/APPROVAL_GATES.md` § Override mechanism. Three
artifacts required:
1. entry in `60-Interactions/overrides.md`,
2. `RALPH_OVERRIDE_<axis>=1` in env,
3. revert override after operation.

CRITICAL overrides without all three are CRITICAL violations.

## Cross-references

- `docs/APPROVAL_GATES.md` — full matrix.
- `governance/human-in-the-loop-policy.md` — where Ralph stops.
- `governance/delegated-authority-matrix.md` — who approves.
- `ledgers/pending-approvals.md` — open approval queue.

## Next actions

- This file rarely needs editing — the matrix is policy.
- If you add a new workflow that introduces a new operation type,
  classify it here AND in `docs/APPROVAL_GATES.md` (HIGH risk to add).
