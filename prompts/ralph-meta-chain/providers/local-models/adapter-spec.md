---
ralph_type: provider
provider: local-models-deferred
status: partial-spec
created: 2026-05-09
summary: "13-field provider-interface answers for local models (Ollama)."
---

# Local Models (Ollama) — Adapter Spec (PARTIAL)

Embeddings: ACTIVE. Completion: deferred. The 13 fields below cover
both; the embeddings rows are populated from
`harness/harness/embeddings.py`.

## 1. prompt_input_format

Ollama's `/v1/chat/completions` is OpenAI-compatible. The adapter
would accept the harness's standard JSON-only judge prompt and POST
to `http://localhost:11434/v1/chat/completions`.

Embedding endpoint: `/api/embeddings` (already used).

## 2. context_package_format

For embeddings: nothing; we send raw note text per-call.
For completion (deferred): same as Claude Code — the vault `CLAUDE.md`
is included as the system message.

## 3. memory_retrieval_package_format

Local Markdown; no transport.

## 4. tool_permission_model

For embeddings: no tools.
For completion (deferred): no tool calls today; Ollama models with
function-calling support (some llama3.x variants) could do tool use,
but mapping to Ralph's tool surface is deferred.

## 5. file_read_write_model

Adapter operates locally; reads/writes pass through Python directly.

## 6. shell_execution_model

Not applicable for embeddings. For completion: deferred.

## 7. approval_gate_model

For embeddings: no approval needed (no mutations).
For completion (deferred): same as Claude Code for HIGH/CRITICAL.

## 8. output_report_format

For embeddings: float[768] vectors.
For completion (deferred): Markdown.

## 9. error_format

HTTP 4xx/5xx from Ollama → harness translates to standard exit codes.

## 10. evaluation_format

`metrics.ndjson` row: `provider: "local-models"`,
`provider_version: "ollama/<model-tag>"`.

## 11. logging_format

Karpathy LLM-Wiki format unchanged.

## 12. rollback_expectation

No external state to roll back; Ollama is stateless per call.

## 13. provider_metadata

```yaml
id: local-models
version: ollama/<model-tag>      # e.g. ollama/nomic-embed-text:latest
capabilities:
  - embeddings (active)
  - structured-output (model-dependent)
  - function-calling (some models, deferred)
```

## Sub-providers

| Capability     | Backend                                       | Status  |
| -------------- | --------------------------------------------- | ------- |
| Embeddings     | Ollama / `nomic-embed-text`                    | ACTIVE  |
| Embeddings     | Cognee (graph reasoning)                       | OPT-IN  |
| Embeddings     | Letta (OS-tiered)                              | OPT-IN  |
| Completion     | Ollama / llama3.x-70b-instruct                 | DEFERRED|
| Completion     | Ollama / gpt-oss-20b                           | DEFERRED|
| Completion     | Ollama / mixtral                               | DEFERRED|

## Cross-references

- `providers/provider-interface.md`.
- `providers/local-models/ollama-notes.md` — operational details.
- `providers/local-models/deferred-implementation.md` — work estimate.
