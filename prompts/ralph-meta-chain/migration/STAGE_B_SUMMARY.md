---
ralph_type: migration
memory_layer: migration
created: 2026-05-09
status: active
summary: "Stage B audit artifacts — pre-apply dry-run + ci backup + token. Stage C is the next user-staged step."
---

# Stage B Summary — pre-apply audit artifacts

This file is the **tracked audit anchor** for Round 8 Stage B. It
documents the dry-run + the artifacts the apply gate will require.
Stage B is reversible: nothing has been moved.

## Generated at

- UTC: 2026-05-09T13:38:38Z
- branch: `claude/ralph-obsidian-cron-jobs-Mb4A9`
- commit (HEAD before Stage B): see `git log` immediately preceding this commit.

## Artifacts produced

### 1. CI workflow backup

`prompts/ralph-meta-chain/migration/ci-backup-20260509T133812Z.yml`

Tracked. Used by `scripts/ralph_rollback_migration.sh` if Stage C
needs to revert. Restore command (post-rollback):

```bash
cp prompts/ralph-meta-chain/migration/ci-backup-20260509T133812Z.yml \
   .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "rollback: restore CI workflow"
```

### 2. Approval token (for Stage C)

The sha256 of `proposed-moves.md` at this moment:

```
5f7a197950349a3cb0c36920ca9a68dde1cf03fd322232199d39addbaf367d22
```

Apply gate 5 requires
`RALPH_MIGRATION_APPROVED=5f7a197950349a3cb0c36920ca9a68dde1cf03fd322232199d39addbaf367d22`
in the Stage C invocation env.

Note: `proposed-moves.md` is gitignored (regenerated each run). The
token will change if propose runs again. To re-compute:

```bash
prompts/ralph-meta-chain/migration/scripts/ralph_propose_migration.sh
shasum -a 256 prompts/ralph-meta-chain/migration/proposed-moves.md
```

### 3. Dry-run apply output

`scripts/ralph_apply_migration.sh` (no flags) → exit code **64**
(default-dry-run-correct).

64 git mv operations would execute:

| Class                       | Count |
| --------------------------- | ----- |
| Phase 1-6 → master-spec       | 50    |
| `obsidian-ralph/` → `_archive/_pre-migrated/` | 13 |
| `docs/voice-multidevice-design.md` → `_archive/_pre-migrated/` | 1 |
| **TOTAL**                     | **64** |

Source / target pairs (full list lives in `proposed-moves.md`).

## Six-gate readiness

| Gate | Requirement                                | This commit  |
| ---- | ------------------------------------------ | ------------ |
| 1    | `proposed-moves.md` present                 | ✓ (regenerable) |
| 2    | `rollback-plan.md` present                  | ✓ (regenerable) |
| 3    | `conflicts.md` reports zero conflicts       | ✓ `(none)`   |
| 4    | `--apply --confirmed` flags both present    | (Stage C)    |
| 5    | `RALPH_MIGRATION_APPROVED` env matches token | (Stage C)    |
| 6    | git tree clean (apart from migration/)      | (Stage C)    |

Gates 1–3 are satisfied at every dry-run. Gates 4–6 only matter at
apply time.

## Stage C precondition checklist

Before invoking
`ralph_apply_migration.sh --apply --confirmed`:

- [ ] All 73 harness tests + 9 voice-server tests pass.
- [ ] Both plugins (Phase 1-6 reference + Round 6 greenfield) tsc
      clean + build.
- [ ] CI on the latest pushed commit is green.
- [ ] `git status` is clean (only `migration/` artifacts, if any).
- [ ] `propose` re-run; sha256 matches the token (or recompute).
- [ ] User has reviewed `proposed-moves.md` end-to-end.
- [ ] User has reviewed `rollback-plan.md` end-to-end.
- [ ] User has confirmed in-flight cron firings are paused (touch
      `$VAULT/90-Meta/STOP`).
- [ ] User has plugin symlink update + cron re-install commands ready
      (post-apply).

## Stage C invocation

When the checklist is fully checked:

```bash
cd prompts/ralph-meta-chain/migration/scripts

# Recompute the token (proposed-moves.md is gitignored; it must exist locally).
./ralph_propose_migration.sh
EXPECTED="$(shasum -a 256 ../proposed-moves.md | awk '{print $1}')"

# Run the apply with all six gates.
RALPH_MIGRATION_APPROVED="$EXPECTED" \
  ./ralph_apply_migration.sh --apply --confirmed
```

Expected output: 64 lines of `moved: <src> → <dst>` + final summary.

## Reversibility

Stage B is **fully reversible** (nothing moved):

```bash
# Discard this commit if the user changes their mind:
git revert HEAD~1   # the Stage B commit
```

Stage C is reversible via the rollback script:

```bash
./ralph_rollback_migration.sh --apply --confirmed
cp ../ci-backup-20260509T133812Z.yml ../../../../.github/workflows/ci.yml
git add . && git commit -m "rollback: Round 8 Stage C"
```

## Cross-references

- `docs/ROUND_8_RUNBOOK.md` — full staged plan.
- `docs/REPO_MIGRATION.md` — design.
- `docs/APPROVAL_GATES.md` § Repo migration.
- `migration/migration-plan.md` — narrative plan.
- `migration/ci-backup-20260509T133812Z.yml` — the backup.
- `migration/proposed-moves.md` — the live (gitignored) move list.
