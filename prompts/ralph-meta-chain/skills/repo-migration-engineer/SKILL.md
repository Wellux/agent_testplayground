---
name: repo-migration-engineer
description: |
  Triggers: "migration plan", "migration apply", "what would Round 8 do",
  "migration rollback", "inventory the repo".
when_to_use: |
  Any time the repo's structural evolution is the topic — Round 4-8
  migration mechanics, conflict resolution, rollback planning.
inputs:
  - stage: inventory | classify | propose | apply | rollback
  - args: per-stage arguments
steps:
  - "Run migration/scripts/<stage>.sh per the user's request."
  - "For 'apply' specifically: VERIFY all six gates are met. If any gate
     fails, refuse. Never run with --apply --confirmed unless ALL of:
     proposed-moves.md ✓, rollback-plan.md ✓, conflicts.md = empty,
     RALPH_MIGRATION_APPROVED matches sha256, git tree clean."
  - "Render the output report (proposed-moves / inventory / etc) for review."
tools:
  - "Read"
  - "Bash(bash:*,git:*,shasum:*)"
  - "Agent(Explore)"
failure_modes:
  - apply requested with conflicts present → REFUSE (rc 65 from script)
  - apply requested without RALPH_MIGRATION_APPROVED → REFUSE (rc 67)
  - dirty git tree → REFUSE (rc 68)
  - rollback requested without rollback-plan.md → REFUSE (rc 66)
  - any of the above: emit clear error pointing at docs/REPO_MIGRATION.md
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: [shell-safety-engineer]
is_prerequisite_of: []
links:
  - "[[docs/REPO_MIGRATION.md]]"
  - "[[migration/]]"
  - "[[docs/APPROVAL_GATES.md]]"
tags: [skill, specialist, migration]
---

# Repo Migration Engineer

The role you assume during Round 4-8 migration work. Discipline:
six-gate apply is non-negotiable; default-dry-run; always inventory
before classifying, classify before proposing, propose before applying.

## Canonical experiment

Given the current repo state (Round 4 already shipped), the skill
must:

1. Run `ralph_repo_inventory.sh` → confirm `inventory-report.md` written
   with at least 100 file rows.
2. Run `ralph_classify_repo_files.sh` → confirm 14 classes counted.
3. Run `ralph_propose_migration.sh` → 60 ± 10 moves; ≥ 1 conflict.
4. Run `ralph_apply_migration.sh` (no flags) → exit 64 (default dry-run)
   OR 65 (conflicts).
5. Run `ralph_apply_migration.sh --apply --confirmed` (no token) →
   exit 65/67/68.
6. Run `ralph_rollback_migration.sh` → exit 64 (dry-run).

Output: a Markdown report enumerating exit codes per step + naming
each gate that fired.
