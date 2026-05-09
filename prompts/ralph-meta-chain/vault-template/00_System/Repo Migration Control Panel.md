---
ralph_type: system
memory_layer: migration
memory_temperature: warm
created: 2026-05-09
status: scaffold
summary: "Migration plan + inventory + rollback (Round 4+ scaffold)."
---

# Repo Migration Control Panel

> **Status:** SCAFFOLD ONLY. Per `docs/REPO_MIGRATION.md` migration
> stays DEFERRED until separately authorized. The CRITICAL "apply"
> phase requires explicit invocation per `00_System/Approval Gates.md`.

## Phase 1-6 reference vs master-spec target

The user has six phases of working code at root paths. The master spec
wants them under `prompts/ralph-meta-chain/`. The migration moves them
in Round 8 — the last round.

| Current path                  | Master-spec target                                  |
| ----------------------------- | --------------------------------------------------- |
| `harness/`                     | `prompts/ralph-meta-chain/scripts/harness/`          |
| `voice-server/`                | `prompts/ralph-meta-chain/voice-server/`              |
| `obsidian-ralph/`              | `prompts/ralph-meta-chain/obsidian-plugin/`           |
| `scripts/install.sh`           | `prompts/ralph-meta-chain/install/install_cron.sh`    |
| `scripts/uninstall.sh`         | `prompts/ralph-meta-chain/install/uninstall_cron.sh`  |
| `scripts/launchd/`             | `prompts/ralph-meta-chain/install/launchd/`           |
| `docs/voice-multidevice-design.md` | `prompts/ralph-meta-chain/docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md` (already migrated in Round 1) |
| `CHANGELOG.md`                 | `prompts/ralph-meta-chain/CHANGELOG.md`               |
| `.gitignore`                   | (stays at repo root)                                  |
| `.github/workflows/ci.yml`     | (stays at repo root; CI paths updated by migration)   |

## Migration commands (Round 4+)

| Command                                | Class    | Effect                                  |
| -------------------------------------- | -------- | --------------------------------------- |
| `harness migration inventory`           | LOW      | scan repo                                |
| `harness migration classify`            | LOW      | tag every file                            |
| `harness migration propose`             | MEDIUM   | proposed-moves.md                         |
| `harness migration validate`            | LOW      | conflict check                            |
| `harness migration apply --confirmed`   | CRITICAL | actually move files (Round 8)            |
| `harness migration rollback`             | HIGH     | restore from rollback plan                |

## Required artifacts before any apply

1. `migration/inventory-report.md` (LOW — auto)
2. `migration/file-classification.md` (LOW — auto)
3. `migration/proposed-moves.md` (MEDIUM — proposed)
4. `migration/rollback-plan.md` (mandatory; refused without it)
5. Audit-log entry created BEFORE any move
6. `--apply --confirmed` invocation
7. `harness self-test` green AFTER apply

## Cross-references

- `docs/REPO_MIGRATION.md` — full design.
- `docs/APPROVAL_GATES.md` § Repo migration — CRITICAL gates.
- `docs/ROADMAP.md` § Round 4 + Round 8.
- `migration/` — Round 4+ scaffold target.
