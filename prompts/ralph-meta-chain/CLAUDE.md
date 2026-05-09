# Repo schema (Karpathy LLM-Wiki style)

This file is the *schema* layer for the Ralph meta-chain repo. Any Claude
Code session opened in this repo loads this file into context. It is the
counterpart of `$VAULT/CLAUDE.md` (the vault's own schema).

## What lives where

Round 8 (2026-05-09) made `prompts/ralph-meta-chain/` the canonical
master-spec layout. Phase 1-6 reference paths are archived under
`prompts/ralph-meta-chain/migration/_archive/_pre-migrated/`; the old
root-level paths (`harness/`, `voice-server/`, `obsidian-ralph/`,
`scripts/`) now contain breadcrumb `README.md` files only.

- `prompts/ralph-meta-chain/` — canonical layout (everything below):
    - `0[1-8]-*.md` — eight Ralph prompts (memory / skills / interaction
      / research-ingest / compress / autoheal / autoevolve / autoupdate).
    - `config.example.yml`, `config.yml` — chain configuration.
    - `crontab.example` — UTC schedule template.
    - `research/` — research notes, synthesis, watchlist, rubric.
    - `docs/` — 18+ canonical design docs (architecture, memory model,
      cron jobs, governance, indexing, Round 8 runbook, etc.).
    - `scripts/harness/` — Python CLI: A/B (`promptfoo`-shaped
      fixtures), embeddings (`Ollama` → `sqlite-vec`), ingest, compress,
      reflect, traces, self-test, migration.
    - `scripts/ralph_*.sh` — Bash shims wrapping the harness CLI +
      validators (`ralph_validate_frontmatter.sh`,
      `ralph_check_links.sh`, `ralph_provider_validate.sh`,
      `ralph_business_ledger_check.sh`).
    - `scripts/lib/` — shared shell helpers.
    - `voice-server/` — FastAPI dispatcher (Phase 3). Voice
      multi-device runtime stays gated per
      `docs/VOICE_MULTI_DEVICE_FUTURE_SCOPE.md`.
    - `obsidian-plugin/` — TypeScript Obsidian plugin (UI for the
      chain).
    - `install/install_cron.sh` — idempotent install/uninstall for
      cron (Linux) / launchd (macOS).
    - `commands/`, `skills/`, `hooks/` — Claude-Code slash commands,
      specialist skills, and pre/post-tool hooks per master spec.
    - `indexes/`, `benchmarks/`, `experiments/` — Round 7 catalogs +
      scorecards + fixture/output/report buckets.
    - `business-entity/`, `migration/`, `providers/`,
      `vault-template/` — Round 3-4 scaffolds.

See `docs/ROADMAP.md` for the round-by-round shipping log and
`docs/OPERATIONS_MANUAL.md` for daily/weekly playbook.

## Operating rules (copied from vault `CLAUDE.md`)

- Append-only writes inside `$VAULT/`. Never delete. Edits add a
  `## Ralph YYYY-MM-DD` block at the bottom.
- Backlinks: every promotion touches 10–15 related pages.
- Promotions ≥ 3 same-tag → MOC.
- Mandatory files in `$VAULT/90-Meta/`: `index.md`, `log.md`,
  `ralph-state.json`, `metrics.ndjson`, `embeddings.db`.
- Exit contract: emit `<promise>COMPLETE</promise>` on stdout when done.

## Privacy

- Never write real user identifiers (email, full name, account IDs) into
  any tracked file. Local secrets live in `*.local.yml` / `.env*`
  (gitignored) only.
- Embedding/RAG runs **local-first** via Ollama. No external embedding
  endpoints by default.

## Cron order (UTC)

| Time   | Prompt                          | Why this slot                        |
| ------ | ------------------------------- | ------------------------------------ |
| 01:00  | `04-research-ingest.md`         | Feeds inbox before memory wakes      |
| 02:00  | `01-memory-optimizer.md`        | Promotes inbox → atomic notes        |
| 03:00  | `02-skills-optimizer.md`        | Reads fresh atomic notes for patterns|
| 04:00  | `03-interaction-optimizer.md`   | A/B-tests with skills + memory ready |
| :30 hr | `05-compress.md`                | Continuously fights bloat            |
