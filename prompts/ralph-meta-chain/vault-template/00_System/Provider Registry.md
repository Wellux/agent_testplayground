---
ralph_type: system
memory_layer: system
memory_temperature: hot
created: 2026-05-09
status: active
summary: "Active and deferred Ralph runtime providers."
---

# Provider Registry

Per `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md`: Claude Code is the only
ACTIVE runtime. Codex, Gemini AI Studio, local-models have adapter
specs but no execution.

| Provider              | Status   | Adapter spec                                | Reference                                         |
| --------------------- | -------- | ------------------------------------------- | ------------------------------------------------- |
| Claude Code           | ACTIVE   | `providers/claude-code/runtime-notes.md`    | https://github.com/anthropics/claude-code         |
| OpenAI Codex CLI      | DEFERRED | `providers/openai-codex/adapter-spec.md`    | https://github.com/openai/codex                   |
| Gemini AI Studio      | DEFERRED | `providers/gemini-ai-studio/adapter-spec.md`| https://aistudio.google.com                        |
| Local models (Ollama) | PARTIAL  | `providers/local-models/ollama-notes.md`    | https://github.com/ollama/ollama                  |

## Activation gate

Activating a deferred adapter is HIGH-risk per
`docs/APPROVAL_GATES.md`. Required artifacts:

1. populated `providers/<vendor>/adapter-spec.md` answering all 13
   provider-interface fields,
2. threat-model review (privacy + cost + capability),
3. test fixtures that pass under the new adapter,
4. explicit user approval in the activation proposal.

## Embedding-only partials

Local Ollama is currently used for **embeddings only** (`nomic-embed-text`).
Promotion to **completion** would require setting up a local LLM (e.g.
Llama 3.x, gpt-oss-20b, or similar) and pointing the harness's judge
model at it. That's an explicit Round 5+ choice.

## Cross-references

- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` — full surface contract.
- `docs/APPROVAL_GATES.md` — activation gating.
- `harness/harness/memory_backends.py` — the only currently-pluggable layer.
