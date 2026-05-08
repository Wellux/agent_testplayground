# Repo schema (Karpathy LLM-Wiki style)

This file is the *schema* layer for the Ralph meta-chain repo. Any Claude
Code session opened in this repo loads this file into context. It is the
counterpart of `$VAULT/CLAUDE.md` (the vault's own schema).

## What lives where

- `prompts/ralph-meta-chain/` — five Ralph prompts + config + crontab.
- `scripts/` — idempotent install/uninstall for cron (Linux) / launchd (macOS).
- `obsidian-ralph/` — TypeScript Obsidian plugin (UI for the chain).
- `harness/` — Python CLI: A/B (`promptfoo`-shaped fixtures), embeddings
  (`Ollama` → `sqlite-vec`), ingest, compress.
- `docs/` — design docs (Phase G voice/multi-device sketch only).

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
