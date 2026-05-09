---
description: |
  Triggers: "ralph migration plan", "migration dry run", "what would Round 8 do"
allowed-tools:
  - "Read"
  - "Bash(harness:*,git:*,bash:*)"
---

# /ralph-migration-plan

Run the migration pipeline read-only and summarize. MEDIUM risk: writes
proposal Markdown to `migration/`; never moves files.

## Inputs

`$ARGUMENTS` — optional `inventory | classify | propose` to stop after
that stage. Default: full read-only pipeline (`inventory → classify →
propose`).

## Process

1. Run `prompts/ralph-meta-chain/migration/scripts/ralph_repo_inventory.sh`.
2. Run `…/ralph_classify_repo_files.sh`.
3. Run `…/ralph_propose_migration.sh`.
4. Read the resulting `migration/proposed-moves.md` and
   `migration/conflicts.md`.

## Output

Render a Markdown report:

- **Inventory** — total files + class breakdown.
- **Proposed moves** — count + first 10 rows.
- **Conflicts** — count + each issue.
- **Required artifacts before any apply** — checklist (per
  `docs/REPO_MIGRATION.md` § Apply gate).
- **Recommendation** — typically "review proposed-moves.md before
  considering apply".

If conflicts > 0, the recommendation block names each conflict and
suggests the resolution path.

## Safety

- **Writes** Markdown proposals to `migration/proposed-moves.md`,
  `migration/rollback-plan.md`, `migration/conflicts.md` (if any),
  and appends an audit line to `migration/migration-log.md`.
  **Never moves files.** Revert with
  `git restore prompts/ralph-meta-chain/migration/`.
- The shell scripts honor their own gates: `apply` refuses six
  independent gates per `docs/APPROVAL_GATES.md` § Repo migration.
- This command never invokes `--apply --confirmed`. Round 8's apply
  step requires explicit user invocation.

## Cross-references

- `migration/README.md`.
- `migration/migration-plan.md`.
- `docs/REPO_MIGRATION.md`.
- `vault-template/00_System/Repo Migration Control Panel.md`.
