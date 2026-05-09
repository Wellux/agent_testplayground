---
name: shell-safety-engineer
description: |
  Triggers: "shell safety", "review this script", "is this Bash safe",
  "harden script", "audit shell".
when_to_use: |
  Reviewing or hardening Bash scripts. Allowlist enforcement, dry-run
  defaults, lockfiles, refusal of force-push / no-verify.
inputs:
  - script_path: scripts/<name>.sh or migration/scripts/<name>.sh
steps:
  - "Run bash -n; refuse if syntax errors."
  - "Check for: --help support, --dry-run default, --apply gating, set -euo pipefail."
  - "Check for forbidden patterns: rm -rf, eval $arg, unquoted $var, curl/wget without explicit auth review."
  - "Check that mutating ops route through git_safety.sh (no bare git push, no --force, no --no-verify)."
  - "Check that cron-fired scripts acquire a lock via lib/locks.sh."
  - "Output a Markdown report scoring the script (1-5) per: safety, idempotency, auditability."
tools:
  - "Read"
  - "Bash(bash -n:*,grep:*,shellcheck:*)"
failure_modes:
  - script lacks --dry-run and mutates files → BLOCKER; escalate
  - script invokes destructive git commands without approval gate → BLOCKER
  - script reads/writes paths outside repo → ERROR; require allowlist
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: []
is_prerequisite_of: [repo-migration-engineer]
links:
  - "[[scripts/lib/git_safety.sh]]"
  - "[[scripts/lib/locks.sh]]"
  - "[[docs/APPROVAL_GATES.md]]"
tags: [skill, specialist, bash, safety]
---

# Shell Safety Engineer

The role you assume when a Bash script enters review or when the
autoheal pass surfaces a script-related ERROR. Discipline: every
mutating script must support `--dry-run` AND `--apply`; defaults to
dry-run; documents exit codes; uses `set -euo pipefail`.

## Canonical experiment

Given the five migration scripts under `migration/scripts/`, the skill
must:

1. Run `bash -n` on each.
2. Verify each supports `--help` AND prints exit codes for mutating
   operations.
3. Verify each refuses without `--apply --confirmed` (CRITICAL paths).
4. Verify each writes to `migration/migration-log.md` with timestamp +
   operation.

All five should pass; output is a one-table report.
