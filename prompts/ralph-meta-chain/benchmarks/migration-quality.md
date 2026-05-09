---
ralph_type: system
created: 2026-05-09
status: active
summary: "Quality rubric for repo-migration reliability (Round 4 + Round 8)."
---

# Migration Quality Scorecard

Grades the migration pipeline's reliability. Every migration script
under `migration/scripts/` must pass these tests before
`ralph_apply_migration.sh` is allowed to run with
`--apply --confirmed`.

## Scored axes (1-5 each)

### inventory completeness (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | every tracked file appears in inventory-report.md          |
| 4     | ≥ 99% coverage; missing files are excluded by gitignore-style rules |
| 3     | ≥ 95% coverage                                            |
| 1     | < 95% coverage (refuse apply)                             |

### classification accuracy (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | every file classified into a non-`unknown` class           |
| 4     | ≥ 99% classified; remaining `unknown` are flagged          |
| 3     | ≥ 95% classified                                            |
| 1     | < 95% (target paths uncertain → refuse apply)              |

### conflict detection (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | every conflict (existing destination / outside-repo target) caught |
| 4     | most caught; one false-negative                             |
| 1     | ≥ 1 missed conflict (apply would silently overwrite)         |

### rollback completeness (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | rollback-plan.md inverts every apply move; CI-restore steps |
| 3     | covers moves but not CI workflow restore                    |
| 1     | rollback-plan missing required steps (refuse apply)          |

### gate strictness (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | apply refuses on every individual gate-failure scenario   |
| 4     | refuses on conflicts + token + dirty-tree                  |
| 1     | apply runs with any gate not enforced                      |

### audit completeness (1-5)

| Score | Criterion                                                |
| ----- | -------------------------------------------------------- |
| 5     | every apply preceded by audit-log entry; sha256 recorded   |
| 3     | audit-log entry exists but no diff_sha256                  |
| 1     | apply runs without audit entry (BLOCKER)                    |

## Composite

`rubric_migration = mean(inventory, classification, conflict,
rollback, gate, audit)`.

## Pass thresholds

- **rubric ≥ 4.5** required before any `ralph_apply_migration.sh
  --apply --confirmed` invocation.
- **gate strictness < 5** → BLOCKER; refuses apply.
- **audit completeness < 5** → BLOCKER; refuses apply.
- **rollback completeness < 4** → BLOCKER; refuses apply.

## Tests covering this scorecard

- `prompts/ralph-meta-chain/tests/test_migration_dry_run.bats` — bats.
- `harness/tests/test_migration.py` — Python unittest mirror.

Both verify:
- exit codes per gate (64 / 65 / 66 / 67 / 68);
- `--help` documentation;
- read-only pipeline produces all 3 artifacts;
- `--apply` refuses without `--confirmed`;
- `--apply --confirmed` refuses without `RALPH_MIGRATION_APPROVED`.

## Round 8 readiness

Before invoking the apply for real (Round 8), the user should verify
the rubric passes via:

```bash
cd prompts/ralph-meta-chain
bats tests/test_migration_dry_run.bats        # local
# OR (CI-equivalent without bats)
cd ../../harness && python3 -m unittest tests.test_migration
```

## Cross-references

- `docs/REPO_MIGRATION.md`.
- `docs/APPROVAL_GATES.md` § Repo migration.
- `migration/README.md`.
- `migration/scripts/*.sh`.
- `vault-template/00_System/Repo Migration Control Panel.md`.
