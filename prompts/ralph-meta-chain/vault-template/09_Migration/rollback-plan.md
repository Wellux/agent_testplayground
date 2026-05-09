---
ralph_type: migration
memory_layer: migration
created: 2026-05-09
status: scaffold
summary: "Rollback plan — must exist before `harness migration apply`."
---

# Rollback Plan

> **Round 4+ scaffold.** Migration's `apply` step refuses to run unless
> this file is populated and not-stale.

## Generated header

```yaml
---
generated_for_apply_at: <ISO_TS>
estimated_rollback_seconds: <N>
artifacts_required:
  - migration/snapshot-<ts>.txt   # tree state pre-apply
  - migration/ci-backup-<ts>.yml  # CI workflow pre-apply
  - 90-Meta/log.md tail            # heal evidence pre-apply
---
```

## Inverse moves

For each entry in `proposed-moves.md`:

```text
mv prompts/ralph-meta-chain/scripts/harness/   → harness/
mv prompts/ralph-meta-chain/voice-server/      → voice-server/
mv prompts/ralph-meta-chain/obsidian-plugin/   → obsidian-ralph/
...
```

(populated by `harness migration propose --with-rollback`)

## Restore CI

```bash
cp migration/ci-backup-<ts>.yml .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "rollback: restore CI workflow"
```

## Restart cron

```bash
./scripts/uninstall.sh
./scripts/install.sh
```

(after migration, the install.sh path itself moves — rollback restores
the old path first.)

## Verify

```bash
harness self-test
```

If self-test green AND log.md shows expected last-runs, rollback is
complete.

## Cross-references

- `docs/REPO_MIGRATION.md` § Rollback.
- `09_Migration/proposed-moves.md` — what's being undone.
- `00_System/Repo Migration Control Panel.md`.
