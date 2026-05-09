# ROUND_8_RUNBOOK.md

## Purpose

Step-by-step execution plan for Round 8 — the **Phase 1-6 retirement**.
This is the only round that uses `git mv` to move legacy root-level
dirs into the master-spec target paths under
`prompts/ralph-meta-chain/`. Six independent gates per
`docs/APPROVAL_GATES.md` § Repo migration. Each stage is independently
committable; revert any one stage with `git revert`.

## Pre-flight (post-audit state, 2026-05-09)

After the audit (commit `377f403`), the read-only pipeline produces:

- 64 total moves
- 14 retargets to `_archive/_pre-migrated/` (every `obsidian-ralph/`
  file + `docs/voice-multidevice-design.md` — superseded by Round 6 +
  Round 1 respectively)
- 50 actual moves (`harness/` × 22, `voice-server/` × 24,
  `scripts/` × 3, `CHANGELOG.md` × 1)
- **0 conflicts**
- `harness migration apply` six gates intact

## Stage A — Read-only pipeline (DONE, this commit)

Already executed. Output:

```bash
cd prompts/ralph-meta-chain/migration/scripts
./ralph_repo_inventory.sh        # → migration/inventory-report.md (gitignored)
./ralph_classify_repo_files.sh   # → migration/file-classification.md (gitignored)
./ralph_propose_migration.sh     # → migration/proposed-moves.md (gitignored)
                                 #   migration/rollback-plan.md (gitignored)
                                 #   migration/conflicts.md (gitignored)
```

Result: pipeline emits `(none)` in `conflicts.md`. The 14 pre-migrated
retargets are surfaced in `proposed-moves.md` with the explanatory
banner.

**Stage A is reversible**: nothing has been moved. Re-running re-generates
the same artifacts.

## Stage B — Pre-apply audit + dry-run (NEXT)

Goal: produce the artifacts the apply gate requires, without moving
any files yet.

```bash
cd prompts/ralph-meta-chain/migration/scripts

# 1. Re-generate (idempotent) and review.
./ralph_propose_migration.sh
$EDITOR ../proposed-moves.md
$EDITOR ../rollback-plan.md
$EDITOR ../conflicts.md   # should be (none)

# 2. CI workflow backup.
ts="$(date -u +%Y%m%dT%H%M%SZ)"
cp ../../../../.github/workflows/ci.yml \
   ../ci-backup-"$ts".yml

# 3. Compute the approval token (sha256 of proposed-moves.md).
EXPECTED="$(shasum -a 256 ../proposed-moves.md | awk '{print $1}')"
echo "RALPH_MIGRATION_APPROVED=$EXPECTED"

# 4. Audit-log entry BEFORE apply.
cat >> ../migration-log.md <<EOF
## [$(date -u +%Y-%m-%dT%H:%M:%SZ)] migration | op=pre-apply ts=$ts sha256=$EXPECTED
- inventory:       OK ($(grep -cE '^\| ' ../inventory-report.md) files)
- classify:        OK
- propose:         64 moves, 14 retargets, 0 conflicts
- rollback-plan:   present
- ci-backup:       ci-backup-$ts.yml
EOF

# 5. Dry-run the apply (no flags or --apply only — never both with --confirmed).
./ralph_apply_migration.sh
# Expected: exit 64 (default dry-run) — prints intended moves.
```

**Stage B is reversible**: still no `git mv`. The audit-log + ci-backup
files are tracked but additive.

Optional: commit the audit-log + ci-backup so the apply gate has the
required artifacts in git history.

## Stage C — Apply (CRITICAL)

Goal: actually move 50 files via `git mv` + 14 to `_archive/_pre-migrated/`.

```bash
cd prompts/ralph-meta-chain/migration/scripts

# 1. Confirm git tree is clean.
git status

# 2. Set the approval token.
EXPECTED="$(shasum -a 256 ../proposed-moves.md | awk '{print $1}')"

# 3. Run apply with all six gates.
RALPH_MIGRATION_APPROVED="$EXPECTED" \
  ./ralph_apply_migration.sh --apply --confirmed
# Expected output: "moved: <src> → <dst>" per move; final summary with
# total move count.

# 4. The script auto-runs a sanity self-test post-apply. If it returns
#    non-zero, the apply is half-committed; run rollback immediately.

# 5. Update CI workflow paths (one edit; the harness Python paths
#    moved from `harness/` to `prompts/ralph-meta-chain/scripts/harness/`).
$EDITOR ../../../../.github/workflows/ci.yml

# 6. Update plugin symlinks (each user's vault separately).
echo "Run on the user's machine:"
echo '  ln -sfn "$REPO/prompts/ralph-meta-chain/obsidian-plugin" \'
echo '          "$VAULT/.obsidian/plugins/ralph-meta-chain"'

# 7. Update cron entries (run install.sh, which now lives at the new path).
echo "Run on the user's machine:"
echo "  ./prompts/ralph-meta-chain/install/uninstall_cron.sh"
echo "  ./prompts/ralph-meta-chain/install/install_cron.sh"

# 8. Verify.
cd ../../../../  # repo root
harness self-test     # if your shell still finds it
# OR (if PATH stale):
python3 -m harness --help    # from prompts/ralph-meta-chain/scripts/harness/
```

**Stage C is reversible** (HIGH risk):

```bash
./ralph_rollback_migration.sh --apply --confirmed
# Restores original paths from rollback-plan.md.
cp ../ci-backup-<ts>.yml ../../../../.github/workflows/ci.yml
git add . && git commit -m "rollback: restore CI workflow"
# Then re-run uninstall + install on user machine.
```

## Six gates (per `docs/APPROVAL_GATES.md`)

`ralph_apply_migration.sh` enforces ALL six independently:

| Gate | What it checks                                                  | Exit if missing |
| ---- | --------------------------------------------------------------- | --------------- |
| 1    | `proposed-moves.md` present                                      | 66              |
| 2    | `rollback-plan.md` present                                       | 66              |
| 3    | `conflicts.md` reports zero conflicts                            | 65              |
| 4    | `--apply --confirmed` flags both present                         | 64              |
| 5    | `RALPH_MIGRATION_APPROVED` env = sha256 of `proposed-moves.md`   | 67              |
| 6    | git working tree clean (apart from migration/ files)             | 68              |

Any gate fails → the script refuses. No partial applies.

## Post-apply checklist

After Stage C succeeds:

- [ ] `harness self-test` (now at the new path) reports green.
- [ ] CI on the next push goes green (privacy + shell + harness +
      voice-server + plugin + plugin-greenfield jobs all pass at the
      new paths).
- [ ] Plugin symlink updated; reload Obsidian; status bar appears.
- [ ] Cron re-installed; `~/.ralph.log` shows next firing at expected
      time.
- [ ] Round 8 entry appended to `CHANGELOG.md` with sha256 of
      proposed-moves.md as audit anchor.
- [ ] `obsidian-ralph/` no longer at root; corresponding files live
      at `prompts/ralph-meta-chain/migration/_archive/_pre-migrated/obsidian-ralph/`.
- [ ] `prompts/ralph-meta-chain/obsidian-plugin/` is the only active plugin.

## Risk table

| Risk                                              | Mitigation                                       |
| ------------------------------------------------- | ------------------------------------------------ |
| Apply runs on a dirty tree                          | Gate 6 refuses                                    |
| Approval token mismatch                            | Gate 5 refuses                                    |
| Conflicts re-emerge between propose and apply       | Gate 3 re-checks `conflicts.md` at apply         |
| CI breaks after apply                              | `ci-backup-<ts>.yml` + rollback                   |
| Plugin symlink stale                                | User re-runs `ln -sfn …`                          |
| Cron entries point at old paths                    | User re-runs install.sh                           |
| Self-test regression after apply                   | rollback; investigate; re-attempt                  |

## When NOT to run Round 8

- If you have uncommitted local work outside `migration/`.
- If CI is currently red on the branch (fix CI first).
- If the user's vault has any in-flight cron firings (touch
  `90-Meta/STOP` first; run apply; remove STOP).
- If Round 7's tests aren't all green (run `python3 -m unittest
  discover -s harness/tests` first).

## Cross-references

- `docs/REPO_MIGRATION.md` — full design.
- `docs/APPROVAL_GATES.md` § Repo migration — the six gates.
- `docs/ROADMAP.md` § Round 8 — high-level plan.
- `migration/migration-plan.md` — narrative plan.
- `migration/scripts/*.sh` — implementation.
- `harness/tests/test_migration.py` — gate verification.
- `vault-template/00_System/Repo Migration Control Panel.md` — vault dashboard.
- `benchmarks/migration-quality.md` — rubric.
