---
ralph_type: provider
provider: local-models-deferred
status: partial
created: 2026-05-09
summary: "Ollama / local LLMs — embeddings ACTIVE; completion DEFERRED."
---

# Provider: Local Models (PARTIAL)

The most-aligned-with-master-spec provider: **local-first by design**.
Embeddings (`nomic-embed-text` via Ollama on localhost) are already
integrated. Completion (the harness's judge model) is deferred.

## Current integration

- `harness/harness/embeddings.py` calls Ollama at
  `http://localhost:11434/api/embeddings`.
- `harness/harness/memory_backends.py` exposes:
  - `LocalSqliteVec` (default; uses Ollama embeddings),
  - `CogneeBackend` (opt-in; local graph reasoning),
  - `LettaBackend` (opt-in; OS-style tiered memory).
- All embedding traffic stays local. No external endpoint by default.

## Deferred work

- The harness's **judge model** (used by `harness ab`,
  `harness reflect`, `harness compress`) currently calls the Anthropic
  SDK exclusively. Routing the judge to a local Ollama completion
  model is the deferred promotion.
- Recommended candidates (per `08-autoupdate.md`'s release-feed scan):
  - llama3.x-70b-instruct
  - gpt-oss-20b
  - mixtral
  - gemma3-27b

## Files in this folder

- `README.md` ← you are here.
- `adapter-spec.md` — 13-field template (mostly populated for
  embeddings; completion section deferred).
- `ollama-notes.md` — operational notes for the Ollama runtime.
- `deferred-implementation.md` — work estimate for completion path.

## Cross-references

- https://github.com/ollama/ollama — host runtime.
- `harness/harness/memory_backends.py` — current integration.
- `harness/harness/embeddings.py` — embedding path.
- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` § Deferred provider: Local models.
