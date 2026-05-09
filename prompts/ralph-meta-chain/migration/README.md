# migration/

Repo-migration tooling for Round 8 (Phase 1-6 retirement) per
`docs/REPO_MIGRATION.md`. Five Bash scripts plus their Markdown
artifacts.

## Layout

```
migration/
├── README.md                    ← you are here
├── migration-plan.md            human-readable plan (Markdown)
├── inventory-report.md          ← written by ralph_repo_inventory.sh
├── file-classification.md       ← written by ralph_classify_repo_files.sh
├── proposed-moves.md            ← written by ralph_propose_migration.sh
├── rollback-plan.md             ← written by ralph_propose_migration.sh
├── conflicts.md                 ← written by ralph_propose_migration.sh
├── migration-log.md             ← appended by every script
└── scripts/
    ├── lib/common.sh            ← shared helpers
    ├── ralph_repo_inventory.sh        (LOW; read-only)
    ├── ralph_classify_repo_files.sh   (LOW; read-only)
    ├── ralph_propose_migration.sh     (MEDIUM; writes proposals only)
    ├── ralph_apply_migration.sh       (CRITICAL; six-gate apply)
    └── ralph_rollback_migration.sh    (HIGH; reverses prior apply)
```

## Pipeline

```
inventory ──► classify ──► propose ──► (review) ──► apply ──► self-test
                                            │
                                            └──► (or) rollback
```

Each step writes the artifact the next step reads. Skipping is OK
where the upstream artifact already exists; scripts re-run earlier
steps automatically when an artifact is missing.

## Quick start (read-only walk-through)

```bash
cd prompts/ralph-meta-chain/migration/scripts

./ralph_repo_inventory.sh         # writes inventory-report.md
./ralph_classify_repo_files.sh    # writes file-classification.md
./ralph_propose_migration.sh      # writes proposed-moves.md + rollback-plan.md + conflicts.md
```

After the third command:
- Open `migration/proposed-moves.md` and review every row.
- Open `migration/conflicts.md` — if non-empty, resolve before any apply.
- Open `migration/rollback-plan.md` — confirm it covers every move.

## Apply (CRITICAL — six gates)

```bash
# 1. Compute the approval token (sha256 of the proposed-moves.md)
EXPECTED=$(shasum -a 256 ../proposed-moves.md | awk '{print $1}')

# 2. Confirm git tree is clean
git status

# 3. Run with all gates
RALPH_MIGRATION_APPROVED="$EXPECTED" \
  ./ralph_apply_migration.sh --apply --confirmed
```

The six gates (per `docs/APPROVAL_GATES.md` § Repo migration):

1. proposed-moves.md present
2. rollback-plan.md present
3. conflicts.md reports zero conflicts
4. `--apply --confirmed` flags both present
5. `RALPH_MIGRATION_APPROVED` env matches sha256 of proposed-moves.md
6. git working tree is clean (apart from migration/ files themselves)

If any gate fails, the script exits with a class-specific code
(64 / 65 / 66 / 67 / 68) and refuses to move anything.

## Rollback

```bash
./ralph_rollback_migration.sh                    # dry-run; prints intended reverses
./ralph_rollback_migration.sh --apply --confirmed # actually rolls back
```

## Risk classes (per script)

| Script                          | Class    | Default behavior                    |
| ------------------------------- | -------- | ----------------------------------- |
| `ralph_repo_inventory.sh`        | LOW      | always-allowed read-only walk        |
| `ralph_classify_repo_files.sh`   | LOW      | always-allowed read-only             |
| `ralph_propose_migration.sh`     | MEDIUM   | writes Markdown proposals only       |
| `ralph_apply_migration.sh`       | CRITICAL | dry-run unless six gates pass        |
| `ralph_rollback_migration.sh`    | HIGH     | dry-run unless `--apply --confirmed` |

## Cross-references

- `docs/REPO_MIGRATION.md` — full design.
- `docs/APPROVAL_GATES.md` § Repo migration — gate matrix.
- `docs/ROADMAP.md` § Round 4 + Round 8 — when this gets used.
- `vault-template/00_System/Repo Migration Control Panel.md` — vault dashboard.
- `vault-template/09_Migration/` — vault-side mirror placeholders.

## Next actions

- Run the read-only pipeline (inventory → classify → propose) to see
  what migration WOULD look like today. Output is informational.
- Round 8 of the roadmap is when apply actually runs. Until then, the
  output exists for review only.
