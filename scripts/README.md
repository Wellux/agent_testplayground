# scripts/ — Phase 1-6 reference (retired in Round 8)

This directory is empty post-Round-8 (2026-05-09). The cron / launchd
installer moved via `git mv` to its master-spec target path:

> **Canonical location:** `prompts/ralph-meta-chain/install/install_cron.sh`

The original Phase 1-6 reference implementation is preserved at:

> **Archive:** `prompts/ralph-meta-chain/migration/_archive/_pre-migrated/scripts/`

## Quick start (post-Round-8)

```bash
# Preview what cron entries would be installed
./prompts/ralph-meta-chain/install/install_cron.sh --dry-run

# Install
./prompts/ralph-meta-chain/install/install_cron.sh

# Uninstall (removes only `# RALPH-managed:` entries)
./prompts/ralph-meta-chain/install/install_cron.sh --uninstall
```

The shell shims that wrap the harness CLI live at
`prompts/ralph-meta-chain/scripts/ralph_*.sh` (note that
`prompts/ralph-meta-chain/scripts/` is a different directory — it
contains the shim layer, not the host installer).

## Why this breadcrumb exists

Round 8's `ralph_apply_migration.sh --confirmed` performed 65 `git mv`
moves. Tooling, IDE link-following, and external pointers may still
expect `scripts/` at the repo root — this README catches them and
routes them to the canonical paths.

## Migration mechanics

See `prompts/ralph-meta-chain/docs/ROUND_8_RUNBOOK.md`.
