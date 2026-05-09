---
ralph_type: migration
memory_layer: migration
created: 2026-05-09
status: active
summary: "Comprehensive preview of what Stage C apply will change. Read before invoking."
---

# Stage C Preview — what `--apply --confirmed` actually does

This document is the **plain-English preview** of Round 8 Stage C. The
machine-readable plan lives in `proposed-moves.md` (gitignored;
regenerated each run); this file is the authoring source for the
human-review pass.

Stage C is **CRITICAL** per `docs/APPROVAL_GATES.md` § Repo migration.
Six gates must pass; reversible via `ralph_rollback_migration.sh
--apply --confirmed` + restore of `ci-backup-<ts>.yml`.

## What changes (4 categories of moves)

### 1. Phase 1-6 → master-spec target (50 git mv operations)

The legacy code dirs at the repo root move under
`prompts/ralph-meta-chain/`:

| Source                              | Target                                                                          | Files |
| ----------------------------------- | ------------------------------------------------------------------------------- | ----- |
| `harness/`                           | `prompts/ralph-meta-chain/scripts/harness/`                                       | 22    |
| `voice-server/`                      | `prompts/ralph-meta-chain/voice-server/`                                          | 24    |
| `scripts/install.sh`                 | `prompts/ralph-meta-chain/install/install_cron.sh`                                | 1     |
| `scripts/uninstall.sh`               | `prompts/ralph-meta-chain/install/uninstall_cron.sh`                              | 1     |
| `scripts/launchd/ai.ralph.axis.plist.tmpl` | `prompts/ralph-meta-chain/install/launchd/ai.ralph.axis.plist.tmpl`         | 1     |
| `CHANGELOG.md`                        | `prompts/ralph-meta-chain/CHANGELOG.md`                                            | 1     |

Subtotal: 50 moves. Git history preserved (`git mv`).

### 2. Round 6-superseded → archive (13 git mv operations)

Every file under `obsidian-ralph/` (the Phase 1-6 reference plugin)
moves to the archive. The Round 6 greenfield plugin at
`prompts/ralph-meta-chain/obsidian-plugin/` stays as the active
plugin.

| Source pattern              | Target                                                                                | Files |
| --------------------------- | ------------------------------------------------------------------------------------- | ----- |
| `obsidian-ralph/*`           | `prompts/ralph-meta-chain/migration/_archive/_pre-migrated/obsidian-ralph/*`           | 13    |

### 3. Round 1-superseded → archive (1 git mv operation)

`docs/voice-multidevice-design.md` was migrated forward in Round 1 to
`prompts/ralph-meta-chain/docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md`.
The legacy file becomes archive evidence.

| Source                                | Target                                                                                                | Files |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----- |
| `docs/voice-multidevice-design.md`     | `prompts/ralph-meta-chain/migration/_archive/_pre-migrated/docs/voice-multidevice-design.md`            | 1     |

### 4. CI workflow update (1 file edit; opt-in)

`.github/workflows/ci.yml` keeps three of its `working-directory:`
paths pointing at the now-moved dirs. The post-Round-8 version lives
at `migration/STAGE_C_CI_WORKFLOW.yml`.

Three changes:

| Job             | Before                              | After                                                            |
| --------------- | ----------------------------------- | ---------------------------------------------------------------- |
| `python`         | `working-directory: harness`         | `working-directory: prompts/ralph-meta-chain/scripts/harness`      |
| `voice-server`   | `working-directory: voice-server`    | `working-directory: prompts/ralph-meta-chain/voice-server`         |
| `plugin`         | `working-directory: obsidian-ralph`  | `working-directory: prompts/ralph-meta-chain/obsidian-plugin`      |
| `plugin-greenfield` | (separate job)                    | (merged into `plugin` since obsidian-ralph/ is archived)            |

If `--update-ci` flag is passed to `ralph_apply_migration.sh`, the
script copies `STAGE_C_CI_WORKFLOW.yml` over `.github/workflows/ci.yml`
in the same apply atomic-step. Otherwise the user runs:

```bash
cp prompts/ralph-meta-chain/migration/STAGE_C_CI_WORKFLOW.yml \
   .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "ci: post-Round-8 working-directory updates"
```

## What does NOT change

Things Stage C deliberately leaves alone:

- `.github/workflows/ci.yml` (unless `--update-ci` is passed).
- `README.md` at repo root (Phase 1-6 entry point + new master-spec
  pointer; user updates this manually if desired).
- `LICENSE`.
- `.gitignore`.
- `prompts/ralph-meta-chain/**` content (already at target paths).

## Total tracked-file count delta

Before Stage C: **319 tracked files**.

After Stage C (without `--update-ci`):
- 0 net file count change (every move preserves the file).
- 0 file deletions.
- The directory structure is what changes:
  - `harness/` no longer at repo root.
  - `voice-server/` no longer at repo root.
  - `obsidian-ralph/` no longer at repo root.
  - `scripts/install.sh` etc no longer at repo root.
  - `docs/voice-multidevice-design.md` archived.

After Stage C (with `--update-ci`):
- Same as above + 1 file edit (.github/workflows/ci.yml).

## User-side changes (NOT done by the apply script)

These are out of scope for the Bash apply script:

### Plugin symlink (per-user vault)

The user's vault has a symlink to the plugin. After Stage C:

```bash
# Remove the old symlink (still pointing at the old path).
rm "$VAULT/.obsidian/plugins/ralph-meta-chain"

# Re-link to the new path.
ln -sfn "$REPO/prompts/ralph-meta-chain/obsidian-plugin" \
        "$VAULT/.obsidian/plugins/ralph-meta-chain"
```

Reload Obsidian; verify the status bar appears.

### Cron / launchd re-install

The `scripts/install.sh` path moved. User runs:

```bash
# Uninstall via the OLD path (use a tag-based crontab cleanup if even the script vanished).
crontab -l | grep -v '# RALPH-managed:' | crontab -

# Install via the NEW path.
./prompts/ralph-meta-chain/install/install_cron.sh
```

### Pause first if cron is active

```bash
touch "$VAULT/90-Meta/STOP"   # pause every cron firing at next tick
# ... run Stage C apply + CI update + plugin symlink + cron re-install ...
rm "$VAULT/90-Meta/STOP"      # resume
```

## Six gates (per `docs/APPROVAL_GATES.md` § Repo migration)

`ralph_apply_migration.sh` enforces ALL six independently. Each
failure has its own exit code:

| Gate | What it checks                                            | Exit if fails |
| ---- | --------------------------------------------------------- | ------------- |
| 1    | `proposed-moves.md` present                                | 66            |
| 2    | `rollback-plan.md` present                                 | 66            |
| 3    | `conflicts.md` reports zero conflicts                      | 65            |
| 4    | `--apply --confirmed` flags both present                   | 64            |
| 5    | `RALPH_MIGRATION_APPROVED` env = sha256(`proposed-moves.md`) | 67          |
| 6    | git working tree clean (apart from migration/ files)       | 68            |

## Invocation (single-command)

When ALL preconditions verified (see RUNBOOK § "Stage C precondition
checklist"):

```bash
cd prompts/ralph-meta-chain/migration/scripts

# Regenerate (idempotent; sha256 stable across runs).
./ralph_propose_migration.sh

# Compute the approval token.
EXPECTED="$(shasum -a 256 ../proposed-moves.md | awk '{print $1}')"
echo "RALPH_MIGRATION_APPROVED=$EXPECTED"

# Run apply (without CI auto-update; recommended for first-time):
RALPH_MIGRATION_APPROVED="$EXPECTED" \
  ./ralph_apply_migration.sh --apply --confirmed

# OR with CI auto-update (single-step):
RALPH_MIGRATION_APPROVED="$EXPECTED" \
  ./ralph_apply_migration.sh --apply --confirmed --update-ci
```

Expected output: 64 `moved: <src> → <dst>` lines + final summary.

## Rollback (HIGH risk)

```bash
cd prompts/ralph-meta-chain/migration/scripts

# Reverse every git mv.
./ralph_rollback_migration.sh --apply --confirmed

# Restore CI from the most-recent backup.
ls ../ci-backup-*.yml  # pick the latest
cp ../ci-backup-<ts>.yml ../../../../.github/workflows/ci.yml

# Re-link plugin to the old path:
ln -sfn "$REPO/obsidian-ralph" "$VAULT/.obsidian/plugins/ralph-meta-chain"

# Re-install cron at the old path:
./scripts/install.sh
```

Verify: `harness self-test` green from the OLD path.

## Cross-references

- `docs/REPO_MIGRATION.md` — full design.
- `docs/APPROVAL_GATES.md` § Repo migration — the six gates.
- `docs/ROUND_8_RUNBOOK.md` — staged plan (A → B → C).
- `migration/STAGE_B_SUMMARY.md` — Stage B audit anchor.
- `migration/STAGE_C_CI_WORKFLOW.yml` — post-apply CI workflow.
- `migration/scripts/ralph_apply_migration.sh` — implementation.
- `migration/scripts/ralph_rollback_migration.sh` — rollback.

## Decision checklist (before invoking Stage C)

- [ ] All 89 harness tests + 9 voice-server tests pass on `main` /
      this branch.
- [ ] CI on the latest pushed commit is green (all 7 jobs).
- [ ] You've reviewed every row in `proposed-moves.md`.
- [ ] You've reviewed `STAGE_C_CI_WORKFLOW.yml` against `.github/workflows/ci.yml`.
- [ ] You've paused cron firings (`touch $VAULT/90-Meta/STOP`).
- [ ] You have the post-apply procedure ready (plugin symlink + cron
      re-install).
- [ ] You have rollback knowledge in case anything regresses.

If any unchecked → don't invoke Stage C yet. Continue staging.
