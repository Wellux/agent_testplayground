---
ralph_type: provider
provider: local-models-deferred
created: 2026-05-09
status: active
summary: "Operational notes for the Ollama runtime."
---

# Ollama Operational Notes

How Ollama is set up for the embedding path that's already shipped;
what would change for the completion path.

## Install

```bash
# macOS (Mac mini per Phase 3 voice-server design)
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

## Pull the embedding model

```bash
ollama pull nomic-embed-text
```

Default model in `prompts/ralph-meta-chain/config.example.yml`:

```yaml
embeddings:
  provider: ollama
  base_url: http://localhost:11434
  model:    nomic-embed-text   # 768 dims
```

## Verify

```bash
curl -s http://localhost:11434/api/embeddings \
  -d '{"model":"nomic-embed-text","prompt":"hello world"}' \
  | jq '.embedding | length'
# expected: 768
```

## launchd (macOS)

Ollama installs a launchd agent that keeps the server alive. Verify:

```bash
launchctl list | grep ollama
```

If the voice-server's `/healthz` reports `tools.ollama: false` while
the agent is loaded, restart Ollama:

```bash
launchctl kickstart -k user/$(id -u)/com.ollama.ollama
```

## Resource tuning

`ollama serve` uses `OLLAMA_KEEP_ALIVE` (default 5m). The Ralph
embedding path is bursty — set:

```bash
launchctl setenv OLLAMA_KEEP_ALIVE 30m
```

So the model stays warm during overnight cron runs.

## For future completion path (deferred)

Pull a completion model:

```bash
ollama pull llama3.1:70b-instruct-q4   # ~40 GB; needs 64 GB RAM
# or smaller:
ollama pull llama3.1:8b-instruct
```

Then in `config.yml`:

```yaml
harness:
  judge_model: ollama/llama3.1:70b-instruct-q4
```

The harness's judge code (Round 5+) checks for `ollama/` prefix and
routes to `/v1/chat/completions` instead of the Anthropic SDK.

## Cross-references

- `harness/harness/embeddings.py` — current integration.
- `harness/harness/memory_backends.py` — `LocalSqliteVec` backend.
- `voice-server/voice_server/whisper.py` — local-only transcription
  (same local-first pattern).
