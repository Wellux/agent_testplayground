---
ralph_type: migration
memory_layer: migration
created: 2026-05-09
status: scaffold
summary: "Proposed file moves — populated by `harness migration propose` (Round 4+)."
---

# Proposed Moves

> **Round 4+ scaffold.** Run `harness migration inventory && harness
> migration classify && harness migration propose` to populate.

## Generated header

```yaml
---
generated: <ISO_TS>
total_moves: <N>
target_root: prompts/ralph-meta-chain
risk_class: CRITICAL
---
```

## Phase 1-6 reference → master-spec target paths

(populated by Round 4+; the Round 8 migration apply uses this list)

```text
mv harness/                  → prompts/ralph-meta-chain/scripts/harness/
mv voice-server/             → prompts/ralph-meta-chain/voice-server/
mv obsidian-ralph/           → prompts/ralph-meta-chain/obsidian-plugin/
mv scripts/install.sh        → prompts/ralph-meta-chain/install/install_cron.sh
mv scripts/uninstall.sh      → prompts/ralph-meta-chain/install/uninstall_cron.sh
mv scripts/launchd/          → prompts/ralph-meta-chain/install/launchd/
mv CHANGELOG.md              → prompts/ralph-meta-chain/CHANGELOG.md
```

## Conflicts

(populated by `harness migration validate`)

## Apply gate

CRITICAL per `docs/APPROVAL_GATES.md`. Required:

1. inventory-report present + reviewed,
2. file-classification present + reviewed,
3. proposed-moves present (this file),
4. rollback-plan present,
5. audit-log entry created,
6. `--apply --confirmed` invocation,
7. `harness self-test` green AFTER apply.

## Cross-references

- `docs/REPO_MIGRATION.md` — full design.
- `09_Migration/inventory-report.md`, `09_Migration/rollback-plan.md`.
- `00_System/Repo Migration Control Panel.md`.
