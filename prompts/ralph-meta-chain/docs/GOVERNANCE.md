# GOVERNANCE.md

## Purpose

Risk classes for every Ralph operation, the approval requirements per
class, and the audit trail expected. Pairs with `APPROVAL_GATES.md`
(which is the operational matrix) — this doc is the policy.

## Risk classes

### LOW
Read-only or non-destructive scaffold creation. Auto-applies inside
budget.

Examples:
- generating reports,
- creating placeholder docs,
- dry-runs,
- local validation,
- tagging an orphan note,
- appending to log.md.

### MEDIUM
Mutations to non-canonical state. Recorded as proposals; auto-applies
with audit.

Examples:
- changing prompts in `50-Prompts/`,
- changing skills in `40-Skills/`,
- modifying non-canonical Markdown,
- generating migration plans (not applying),
- updating indexes.

### HIGH
Mutations to canonical state, system surface, or anything externally
visible. Explicit user approval required.

Examples:
- changing Claude Code hooks,
- modifying cron / launchd entries,
- moving files (repo migration apply),
- modifying canonical memory (`stability: canonical`),
- applying prompt promotions to incumbent,
- business communications **drafts intended for external use**.

### CRITICAL
Irreversible or externally-binding actions. Explicit user approval +
audit trail + rollback plan required.

Examples:
- external communications (sending emails, posting),
- legal commitments,
- financial actions (invoicing, paying),
- credentials / API access changes,
- voice always-listening enablement,
- remote execution endpoints,
- repo-wide migration **apply**.

## Approval requirements

| Class    | Auto-applies?                  | Requires?                                   | Audit?                  |
| -------- | ------------------------------ | ------------------------------------------- | ----------------------- |
| LOW      | yes (within budget)             | budget.<axis> remaining                     | log.md only             |
| MEDIUM   | yes (proposal recorded)         | proposal in `30-Notes/`                     | log.md + state.json     |
| HIGH     | no                              | explicit user approval                      | log.md + state.json + escalations.md |
| CRITICAL | no                              | explicit user approval + rollback + audit   | log.md + state.json + audit-log + ledger |

## What "explicit approval" means

- Writing a comment in the proposal note's frontmatter:
  `status: approved` (HIGH).
- Adding the proposal's id to `60-Interactions/approvals.md` AND running
  the apply command (CRITICAL).
- For repo-wide migration: invoking `migration/scripts/ralph_apply_migration.sh`
  with `--apply` AND a non-empty `--confirmed` flag (CRITICAL).

The chain never **infers** approval from silence. Absence of a NO is
not a YES.

## Audit trail

Every mutation appends:

1. one line to `90-Meta/log.md` (Karpathy `## [YYYY-MM-DD] axis | k=v`),
2. updated entry in `90-Meta/ralph-state.json` (atomic temp+rename),
3. for HIGH/CRITICAL: a `## Ralph YYYY-MM-DD` block in the affected
   file,
4. for HIGH/CRITICAL: an entry in
   `60-Interactions/escalations.md` (heal-style) AND
   `business-entity/ledgers/audit-log.md` (Round 3+).

## Append-only invariant

The chain **never deletes**. Every "delete" is a `mv` to `_archive/`.
Restoring is `mv` back. This is non-negotiable across all risk classes.

## Approval modes

`config.yml` exposes an `approvalMode` setting (defaults to `proposal-first`):

- `proposal-first` — every MEDIUM+ change opens a proposal first
  (recommended).
- `auto-medium` — MEDIUM auto-applies without proposal (only safe for
  experienced users on a personal vault).
- `paranoid` — even LOW changes ask first (useful for audited/regulated
  contexts; slows the chain considerably).

Future round 3+ extends with `business-only-paranoid` for selective
gating.

## Roles

In single-user mode, the user IS:
- Operator (runs cron / responds to escalations),
- Reviewer (approves HIGH/CRITICAL proposals),
- Auditor (reads audit-log and challenges decisions),
- Owner (sets approval mode + risk-class definitions).

Multi-user / business-entity mode (deferred): roles separate per
`business-entity/governance/delegated-authority-matrix.md`.

## Escalation routing

Escalations land in `60-Interactions/escalations.md`. The Obsidian status
bar shows the highest-severity open escalation (BLOCKER / ERROR / WARN).
Future rounds add desktop notifications via the notification hook.

## Rollback expectations

Every HIGH/CRITICAL apply must include:

- a brief rollback plan in the proposal (e.g., "revert commit X" or
  "mv _archive/<id>-original.md back").
- identification of the inverse operation,
- estimated time-to-revert.

If a rollback isn't trivially specifiable, the proposal should be
re-classified CRITICAL and routed to a multi-step approval.

## Safety notes

- The risk classes are intentionally conservative. Most users will run
  `proposal-first` and approve weekly.
- When in doubt, choose the higher class.
- Risk-class downgrades (e.g., moving an operation from HIGH to MEDIUM)
  is itself a HIGH-risk change to this doc.

## Cross-references

- `APPROVAL_GATES.md` — the operational matrix that maps every
  operation to its class.
- `SECURITY_PRIVACY.md` — privacy concerns layer onto risk classes.
- `BUSINESS_ENTITY_SCOPE.md` — same governance applies to business
  ledgers (Round 3+).
- `REPO_MIGRATION.md` — migration apply is CRITICAL.
- Phase 1-6 reference: the existing prompts / harness already honor
  these classes; this doc formalizes them.

## Next actions

Read `APPROVAL_GATES.md` for the matrix mapping every operation to its
risk class, then `OPERATIONS_MANUAL.md` for the daily/weekly playbook.
