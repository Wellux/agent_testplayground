# INDEXING.md

## Purpose

Step-by-step bootstrap for the local vault embedding index. Ralph's
retrieval is `sqlite-vec` + FTS5 hybrid; the embeddings come from
local Ollama. Nothing leaves your machine.

This doc is **document-only** for CI environments without Ollama.
Run the steps below on your real host.

## Prerequisites

- Ollama installed and running. See <https://ollama.com/download>.
  - macOS: `brew install ollama && ollama serve &`
  - Linux: `curl -fsSL https://ollama.com/install.sh | sh`
- The harness uv environment synced:
  ```bash
  cd prompts/ralph-meta-chain/scripts/harness && uv sync
  ```
- A vault path resolved via either `$VAULT` env var or
  `prompts/ralph-meta-chain/config.yml` `vault_path:` key.

## Quick bootstrap (one command)

```bash
# Dry-run first (default)
./prompts/ralph-meta-chain/scripts/ralph_bootstrap_embed.sh

# Then for real
./prompts/ralph-meta-chain/scripts/ralph_bootstrap_embed.sh --apply
```

The script:
1. Verifies Ollama is on PATH (refuses with install command otherwise).
2. Verifies the vault path resolves and exists.
3. Pulls the embedding model (`nomic-embed-text` by default).
4. Runs `harness embed --vault <path> --vault-full`.

To use a different model:
```bash
RALPH_EMBED_MODEL=mxbai-embed-large \
  ./prompts/ralph-meta-chain/scripts/ralph_bootstrap_embed.sh --apply
```

## What gets indexed

`harness embed --vault-full` walks every `*.md` under the vault except:

- `90-Meta/_archive/` (excluded by config)
- Files matching `excluded_dirs` in `config.yml`
- Files where frontmatter has `embed: false`

For each file, the harness chunks the body, embeds each chunk via the
configured Ollama model, and writes vectors + FTS rows to
`$VAULT/90-Meta/embeddings.db` (sqlite-vec + FTS5 sidecar).

## Verifying the index

```bash
# Inspect the db
ls -lh "$VAULT/90-Meta/embeddings.db"
sqlite3 "$VAULT/90-Meta/embeddings.db" "SELECT count(*) FROM chunks;"

# Run a query
cd prompts/ralph-meta-chain/scripts/harness
uv run python -m harness query --vault "$VAULT" 'memory promotion criteria'
```

Expected: ≥ 1 chunk per `*.md` body section, queries return nearest
chunks ranked by hybrid score.

## Troubleshooting

### "Ollama not running"

```bash
ollama serve &
ollama list   # should show pulled models
```

If `ollama serve` errors with "address already in use", you already
have an instance running — proceed.

### "Model not pulled"

The bootstrap shim pulls the default model automatically. To pull a
different one manually:

```bash
ollama pull nomic-embed-text
```

### "Vault path mismatch"

The harness CLI accepts `--vault <path>` to override config.yml. The
plugin's `runHarness()` (post-Codex round-5 fix) auto-injects
`--vault` from the auto-detected `vaultRoot`. If you're invoking the
harness directly, pass `--vault` explicitly.

### "sqlite-vec missing"

`uv sync` in the harness directory installs `sqlite-vec` automatically.
If you see "no such module: vec0", reinstall:

```bash
cd prompts/ralph-meta-chain/scripts/harness && uv sync --reinstall
```

### "Embedding too slow on big vaults"

`harness embed --vault` (without `--vault-full`) caps at 5 minutes
per run; re-run until convergence. The cron at `:30 hourly` runs
incremental embeds based on `mtime`, so a one-time bootstrap is enough
for first install.

### "Embeddings drift from the source notes"

Run `harness self-test --check embeddings` to detect chunks whose
parent file no longer exists (orphans) or whose `mtime` is newer than
the chunk's stamp (stale). The autoheal pass at `:15 hourly` reports
both.

## Safety notes

- Embeddings are local. The default model `nomic-embed-text` runs
  inside Ollama at `localhost:11434` only.
- The bootstrap shim is **dry-run by default**. The user must pass
  `--apply` to execute pulls + indexing.
- The bootstrap shim **never modifies the vault** beyond writing
  `90-Meta/embeddings.db`.
- The privacy guard in CI ensures no embedding endpoint URL referencing
  an external service can be added without explicit review.

## Cross-references

- `prompts/ralph-meta-chain/docs/MEMORY_MODEL.md` — three-layer
  Karpathy LLM-Wiki memory.
- `prompts/ralph-meta-chain/docs/ARCHITECTURE.md` — system overview.
- `prompts/ralph-meta-chain/providers/local-models/ollama-notes.md` —
  provider-side adapter spec for local models.
- `prompts/ralph-meta-chain/scripts/harness/harness/embeddings.py` —
  the embed implementation.
- `prompts/ralph-meta-chain/scripts/ralph_bootstrap_embed.sh` — this
  shim's source.
- `prompts/ralph-meta-chain/docs/OPERATIONS_MANUAL.md` — daily checks
  + troubleshooting.

## Next actions

For first install: run the dry-run, review, then `--apply`. For an
existing install: the cron handles incremental embeds — only re-bootstrap
if `embeddings.db` is corrupt or you've switched embedding models.
