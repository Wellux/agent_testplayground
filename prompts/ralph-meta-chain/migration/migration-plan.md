---
ralph_type: migration
memory_layer: migration
created: 2026-05-09
status: draft
summary: "The Round 8 migration plan in human-readable form."
---

# Migration Plan

The plan for Round 8 (per `docs/ROADMAP.md`): retire the Phase 1-6
reference implementation by moving every legacy root-level dir under
`prompts/ralph-meta-chain/`.

This document is the **narrative** plan. The machine-readable plan
lives in `proposed-moves.md` (regenerated each time).

## Goals

1. Bring the repo into compliance with the master spec's
   "TARGET ROOT: All primary implementation must be created under
   `prompts/ralph-meta-chain/`".
2. Preserve git history via `git mv`.
3. Update CI workflow paths.
4. Update plugin symlink targets.
5. Maintain self-test green throughout.

## Non-goals

- Do NOT move files that are already at master-spec target paths.
- Do NOT move the repo-root `.gitignore`, `LICENSE`, `README.md` (they
  are the **repo entry point**, classified `unrelated`).
- Do NOT delete anything. Every move is `git mv`; nothing is removed.

## Phase mapping

| Phase 1-6 path                          | Master-spec target                                          |
| --------------------------------------- | ----------------------------------------------------------- |
| `harness/`                               | `prompts/ralph-meta-chain/scripts/harness/`                  |
| `voice-server/`                          | `prompts/ralph-meta-chain/voice-server/`                    |
| `obsidian-ralph/`                        | `prompts/ralph-meta-chain/obsidian-plugin/`                  |
| `scripts/install.sh`                     | `prompts/ralph-meta-chain/install/install_cron.sh`           |
| `scripts/uninstall.sh`                   | `prompts/ralph-meta-chain/install/uninstall_cron.sh`         |
| `scripts/launchd/`                       | `prompts/ralph-meta-chain/install/launchd/`                  |
| `docs/voice-multidevice-design.md`       | `prompts/ralph-meta-chain/docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md` (already migrated in Round 1; conflict to resolve) |
| `CHANGELOG.md`                           | `prompts/ralph-meta-chain/CHANGELOG.md`                     |
| `.github/workflows/ci.yml`               | (stays at repo root; CI paths updated in-place)              |
| `.gitignore`                              | (stays at repo root)                                          |
| `README.md` (root)                        | (stays at repo root)                                          |
| `LICENSE`                                  | (stays at repo root)                                          |

## Phases of Round 8 itself

1. **Pre-flight** (LOW). Run inventory + classify + propose. Review every
   row in proposed-moves.md.
2. **Conflict resolution** (HIGH).
   - The voice-multidevice-design.md conflict: decide whether to drop
     the old `docs/voice-multidevice-design.md` (it was superseded by
     Round 1's `prompts/ralph-meta-chain/docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md`).
     Recommendation: append-archive the old to `_archive/` and remove
     it from migration scope.
3. **CI backup** (MEDIUM). Copy `.github/workflows/ci.yml` to
   `migration/ci-backup-<UTC-ts>.yml`.
4. **Apply** (CRITICAL). Six-gate `ralph_apply_migration.sh`.
5. **CI path update** (HIGH). Edit `.github/workflows/ci.yml` working
   directories to point at new paths.
6. **Plugin symlink update** (HIGH). User runs:
   `rm "$VAULT/.obsidian/plugins/ralph-meta-chain" && ln -s "$REPO/prompts/ralph-meta-chain/obsidian-plugin" "$VAULT/.obsidian/plugins/ralph-meta-chain"`.
7. **Cron update** (HIGH). User runs `./prompts/ralph-meta-chain/install/uninstall_cron.sh && ./prompts/ralph-meta-chain/install/install_cron.sh`.
8. **Verify** (LOW). `harness self-test` must be green.
9. **Open PR** (per repo standard).

## Risk class

The OVERALL Round 8 is CRITICAL per `docs/APPROVAL_GATES.md` §
Repo migration. Each individual phase has its own class above.

## Rollback contract

`rollback-plan.md` is generated alongside `proposed-moves.md`. If any
phase fails:

1. Run `ralph_rollback_migration.sh --apply --confirmed`.
2. Restore CI from backup: `cp migration/ci-backup-<ts>.yml .github/workflows/ci.yml`.
3. Restore plugin symlink to old path.
4. Restore cron via the OLD `scripts/install.sh`.
5. Run `harness self-test` to confirm.

## When

Round 8 is the LAST roadmap round. Don't run it until rounds 4-7 are
complete and every script + scaffold under
`prompts/ralph-meta-chain/scripts/` (Round 5) and
`prompts/ralph-meta-chain/obsidian-plugin/` (Round 6) is feature-
complete.

## Cross-references

- `docs/REPO_MIGRATION.md` — full design.
- `docs/ROADMAP.md` § Round 8.
- `docs/APPROVAL_GATES.md` § Repo migration.
- `proposed-moves.md`, `rollback-plan.md`, `conflicts.md`.

## Next actions

- For Round 4 (this round): no apply. Just confirm the read-only
  pipeline works.
- For Round 8: review this plan + run the pre-flight + resolve
  conflicts. The apply requires explicit user invocation.
