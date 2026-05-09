# REPO_MIGRATION.md

## Purpose

Specify how repo-wide migration would work — inventory → classify →
propose → apply → rollback — with the master spec's safety contract.
Currently DEFERRED per user choice; this doc captures the design so
Round 4+ can implement it without re-deriving.

## Migration classes

Every file in the repo gets classified into one of:

- `ralph-core` — prompts, harness, voice-server, plugin, scripts.
- `prompts` — anything matching `*ralph*` or under `prompts/`.
- `scripts` — `scripts/`, `*.sh`.
- `docs` — `*.md` outside the above.
- `research` — `RESEARCH_*`, `research/`.
- `experiments` — `experiments/`, `harness/fixtures/`.
- `memory` — Markdown with `ralph_type: memory` frontmatter.
- `skills` — Markdown with `ralph_type: skill`.
- `provider-adapters` — `providers/`.
- `business-entity` — `business-entity/`.
- `migration` — `migration/`.
- `archive` — anything in `_archive/`, `_processed/`, `_rejected/`.
- `unrelated` — files clearly outside Ralph scope (LICENSE, README at
  root, etc.).
- `unknown` — couldn't classify; manual review required.

## Migration commands (Round 4+ target)

| Command                                         | Class     | Effect                                      |
| ----------------------------------------------- | --------- | ------------------------------------------- |
| `harness migration inventory`                    | LOW       | scan repo; write `migration/inventory-report.md` |
| `harness migration classify`                     | LOW       | tag every file; write `migration/file-classification.md` |
| `harness migration propose`                      | MEDIUM    | generate `migration/proposed-moves.md`      |
| `harness migration validate`                     | LOW       | check proposed moves for conflicts          |
| `harness migration apply --confirmed`            | CRITICAL  | execute the proposed moves                  |
| `harness migration rollback`                      | HIGH      | restore from `migration/rollback-plan.md`   |

`apply` requires:

- `--confirmed` flag (no defaults),
- a recent `validate` pass with zero conflicts,
- a present `rollback-plan.md`,
- explicit user invocation,
- audit-log entry created before any move.

## Inventory output

```yaml
# migration/inventory-report.md
---
generated: 2026-05-09T12:00:00+00:00
total_files: 187
classes:
  ralph-core: 76
  docs: 23
  scripts: 5
  archive: 0
  unrelated: 4
  unknown: 1
---

# Inventory

## ralph-core
- harness/harness/ab.py  (current path)
- ...

## docs
- ...

## unknown
- ./obsolete-thing.md  (no frontmatter; needs review)
```

## Proposed-moves output

```yaml
# migration/proposed-moves.md
---
generated: 2026-05-09T12:00:00+00:00
total_moves: 42
target_root: prompts/ralph-meta-chain
risk_class: CRITICAL
---

# Proposed moves

## Phase 1-6 reference → master-spec target paths

- mv harness/                  → prompts/ralph-meta-chain/scripts/harness/
- mv voice-server/             → prompts/ralph-meta-chain/voice-server/
- mv obsidian-ralph/           → prompts/ralph-meta-chain/obsidian-plugin/
- mv scripts/install.sh        → prompts/ralph-meta-chain/install/install_cron.sh
- ...

## Conflicts
- prompts/ralph-meta-chain/scripts/harness/ already contains files
  → REJECT this move; manual reconciliation required.

## Rollback plan
- For each move: `git mv <new-path> <old-path>`.
- Restore CI workflow paths from backup at migration/ci-backup-<ts>.yml.
- Restart cron after restore: scripts/uninstall.sh && scripts/install.sh.
```

## Conflict handling

A move is rejected if:

- the destination path exists and isn't empty,
- the source path is git-untracked (run `git status` first),
- the destination path is outside the repo,
- the source contains the user-identifier needle (privacy guard).

Rejected moves go in `migration/conflicts.md` for manual resolution.

## Apply mechanics

`harness migration apply --confirmed` does:

1. Snapshot the current tree (`git status --porcelain` + commit
   hash + `migration/snapshot-<ts>.txt`).
2. For each proposed move: `git mv <src> <dst>` (preserves history).
3. Update CI workflow paths if any source/destination matches a known
   CI input.
4. Update the Obsidian plugin's repo-path setting (from prior path to
   new).
5. Update `prompts/ralph-meta-chain/CLAUDE.md` paths.
6. Write `migration/migration-log.md` with the action sequence.
7. Run `harness self-test` and refuse to commit if anything regresses.
8. Open a draft PR via `mcp__github__create_pull_request` — never
   pushes directly to main.

## Rollback

`harness migration rollback`:

1. Read `migration/rollback-plan.md`.
2. For each entry: `git mv <new-path> <old-path>`.
3. Restore CI workflow from backup.
4. Restart cron.
5. Run `harness self-test` to confirm restoration.

## Safety contract

The master spec rules, paraphrased:

- **Default dry-run.** Inventory + classify + propose are LOW/MEDIUM.
  Apply is CRITICAL.
- **Inventory entire repo before any move.** No partial moves.
- **Never move files outside the repo.** Hard refuse.
- **Never overwrite files.** Reject every move where destination
  exists.
- **Preserve git history via `git mv`.** Never `cp` + `rm`.
- **Create rollback plan before apply.** Validation refuses without it.
- **Require `--apply --confirmed`.** Two flags.
- **Log every action.** `migration/migration-log.md`.
- **Produce Markdown report.** `migration/migration-plan.md` is the
  audit artifact.

## Why deferred today

Per user choice in the prior plan:

> Migrating existing repo files outside `prompts/ralph-meta-chain/`
> remains DEFERRED.

Round 1 documents the design only. Round 4+ ships the inventory/
classify/propose path (LOW/MEDIUM only, no `apply` flag wired). Round
5+ wires `apply` behind the explicit gate.

## Safety notes

- **Migration apply changes CI paths.** A botched migration breaks the
  privacy guard, which breaks every PR. Test in a feature branch first.
- **Plugin paths matter.** `obsidian-ralph/` symlinked into
  `.obsidian/plugins/` will break if migrated; the migration must
  prompt the user to re-symlink.
- **Tags on Markdown move with the file.** Frontmatter `related:
  [[wikilinks]]` does NOT auto-rewrite; a follow-up `harness migrate
  --rewrite-links` (future) handles that.

## Cross-references

- `APPROVAL_GATES.md` — migration apply is CRITICAL.
- `GOVERNANCE.md` — risk-class policy.
- `ARCHITECTURE.md` — current Phase 1-6 reference paths.
- `OPERATIONS_MANUAL.md` — migration playbook (Round 4+).
- Round 4+ scaffold target: `migration/scripts/`,
  `migration/migration-plan.md`, etc.

## Next actions

For Round 1: nothing to do today. The Phase 1-6 reference implementation
stays at root paths; the docs reference both the current path and the
master-spec target. When Round 4 lands and you want to migrate, start
with `harness migration inventory` and review `inventory-report.md`
before considering anything more.
