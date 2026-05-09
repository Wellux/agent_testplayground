# harness/ — Phase 1-6 reference (retired in Round 8)

This directory is empty post-Round-8 (2026-05-09). The Python harness
moved via `git mv` to its master-spec target path:

> **Canonical location:** `prompts/ralph-meta-chain/scripts/harness/`

The original Phase 1-6 reference implementation is preserved at:

> **Archive:** `prompts/ralph-meta-chain/migration/_archive/_pre-migrated/harness/`

## Why this breadcrumb exists

Round 8's `ralph_apply_migration.sh --confirmed` performed 65 `git mv`
moves. Tooling, IDE link-following, and external pointers (search
results, prior PRs, blog references) may still expect `harness/` at the
repo root — this README catches them and routes them to the canonical
path.

## Migration mechanics

See `prompts/ralph-meta-chain/docs/ROUND_8_RUNBOOK.md` for the full
mechanics. Rollback is documented at
`prompts/ralph-meta-chain/migration/rollback-plan.md`.

## Do not add files here

New code should land at the canonical path. If you need to pin
something at this path for compatibility, open an issue first per
`CONTRIBUTING.md` so the approval gate is reviewed.
