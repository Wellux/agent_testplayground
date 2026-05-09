---
ralph_type: system
memory_layer: system
created: 2026-05-09
status: template
target: $VAULT/00_System/Provider Registry.md
summary: "Provider activation status + per-provider conformance scores."
---

# Provider Index — TEMPLATE

The runtime mirror lives at `$VAULT/00_System/Provider Registry.md`.
Maintained by hand (or by a future Round 7+ cron pass that reads
`providers/<vendor>/adapter-spec.md` and counts populated fields).

## Active vs deferred

| Provider              | Status   | Adapter spec                                 | 13-field score | Last reviewed |
| --------------------- | -------- | -------------------------------------------- | -------------- | ------------- |
| Claude Code           | ACTIVE   | `providers/claude-code/runtime-notes.md`     | 13/13          | 2026-05-09    |
| OpenAI Codex CLI      | DEFERRED | `providers/openai-codex/adapter-spec.md`     | 13/13 (template) | 2026-05-09  |
| Gemini AI Studio      | DEFERRED | `providers/gemini-ai-studio/adapter-spec.md` | 13/13 (template) | 2026-05-09  |
| Local models (Ollama) | PARTIAL  | `providers/local-models/adapter-spec.md`     | 13/13 (embeddings active) | 2026-05-09 |

## Conformance scoring

Per `providers/provider-interface.md` and
`config/provider-interface.schema.json`. Each adapter is scored on
the 13-field contract:

- **N/13 populated** — number of fields with non-trivial content.
- **Active** = all 13 populated AND fixtures replicate.
- **Partial** = subset populated; adapter handles a sub-domain
  (e.g. embeddings only).
- **Deferred-spec** = template only; not auto-routed.
- **Non-conformant** = harness refuses to run prompts through it.

## Capability matrix

|                          | Claude Code | Codex (deferred) | Gemini (deferred) | Local models (partial) |
| ------------------------ | ----------- | ---------------- | ----------------- | --------------------- |
| Tool use                 | ✓           | ✓                | ✓ (function-call) | model-dependent       |
| Hooks (lifecycle)        | ✓           | unknown          | unknown           | n/a                   |
| Slash commands           | ✓           | n/a              | n/a               | n/a                   |
| Skills (.md schema)      | ✓           | adapter-required | adapter-required  | n/a                   |
| Long context (≥ 200k)    | ✓           | ✓                | ✓ (1M-2M)         | model-dependent       |
| Local-first              | ✗ (API)     | ✗                | ✗                 | ✓                     |
| Free-tier embeddings     | ✗           | ✗                | ✗                 | ✓ (Ollama)            |

## Activation gate

Per `docs/APPROVAL_GATES.md` § Provider — HIGH risk, requires:

1. populated 13-field `<vendor>/adapter-spec.md`,
2. threat-model review (privacy + cost + capability),
3. fixtures pass under the new adapter,
4. explicit user approval in the activation proposal.

## Cross-references

- `providers/provider-interface.md` — the 13-field contract.
- `providers/claude-code/runtime-notes.md` — canonical conformant adapter.
- `vault-template/00_System/Provider Registry.md` — vault-side mirror.
- `harness/harness/memory_backends.py` — only currently-pluggable layer.
