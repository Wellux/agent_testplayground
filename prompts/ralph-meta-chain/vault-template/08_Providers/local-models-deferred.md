---
ralph_type: provider
memory_layer: system
provider: local-models-deferred
status: partial
created: 2026-05-09
summary: "Ollama / local LLMs — embeddings active; completion deferred."
---

# Provider: Local models (PARTIAL)

Status: **PARTIAL** — embeddings already use Ollama (`nomic-embed-text`).
Completion path is deferred. Adapter spec target:
`providers/local-models/adapter-spec.md` (Round 4+).

## What's already integrated

- `harness/harness/embeddings.py` reads from Ollama at
  `http://localhost:11434/api/embeddings`.
- `harness/harness/memory_backends.py` has `LocalSqliteVec` (default,
  uses Ollama embeddings) + `CogneeBackend` + `LettaBackend` opt-ins.
- All embedding flow stays local.

## What's NOT integrated

- The harness's **judge model** (`harness/harness/judge.py`,
  `harness/harness/reflect.py`, `harness/harness/compress.py`) calls the
  Anthropic SDK exclusively.
- Round 4+ would add `judge_model: ollama/<name>` routing to a local
  Ollama completion endpoint.

## Reference

- https://github.com/ollama/ollama — host.
- https://ollama.com/library/nomic-embed-text — current embedding model.
- Recommended local LLM candidates for Round 4+ judge:
  llama3.x:70b-instruct, gpt-oss-20b, mixtral, gemma3.

## What activation would require

Per `docs/APPROVAL_GATES.md`: HIGH risk per adapter.
- pick a model + version + memory budget.
- benchmark rubric quality vs Claude judge (must score ≥ 3.5/5 on a
  control fixture set).
- update fixtures to opt in via `--judge-model ollama/<name>`.

## Adapter sketch

Ollama's completion API is OpenAI-compatible at `/v1/chat/completions`.
The harness's judge prompt is JSON-only — works on any decent local
model.

```python
# harness/judge.py — Round 4+ extension
if judge_model.startswith("ollama/"):
    return _ollama_judge(text, judge_model.split("/", 1)[1])
```

## Cross-references

- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` § Deferred provider: Local models.
- `harness/harness/memory_backends.py`.
- `00_System/Provider Registry.md`.
