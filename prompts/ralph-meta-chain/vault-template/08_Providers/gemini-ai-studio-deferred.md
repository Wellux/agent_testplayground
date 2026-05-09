---
ralph_type: provider
memory_layer: system
provider: gemini-ai-studio-deferred
status: deferred
created: 2026-05-09
summary: "Gemini AI Studio adapter — spec only, not active."
---

# Provider: Gemini AI Studio (DEFERRED)

Status: **DEFERRED** per user choice. Adapter spec target:
`providers/gemini-ai-studio/adapter-spec.md` (Round 4+).

## Reference

- https://aistudio.google.com — Google AI Studio (formerly MakerSuite).
- https://cloud.google.com/vertex-ai — Vertex AI (production runtime).

## Why deferred

1. User explicitly picked Claude Code only.
2. Cloud-only; ships code/data to Google infra.
3. No bandwidth in current rounds.

## What activation would require

Same gate shape as the Codex adapter — HIGH risk, 13-field spec
populated, threat-model review, explicit approval.

## Adapter sketch (for Round 4+ implementer)

Gemini's API is OpenAI-compatible (Generative Language API + Vertex
function-calling). Translation:

- `prompt_input_format`: Gemini's structured-content array
  (text + tool calls).
- `context_package_format`: parts array; CLAUDE.md becomes a system
  message.
- `tool_permission_model`: function-call allowlist; map our
  allow/deny to Gemini tool config.
- `file_read_write_model`: Vertex's file-handle API (Round 4 deeper).
- `evaluation_format`: parse Vertex telemetry → metrics.ndjson row
  with `provider: gemini-ai-studio`.

## Cross-references

- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` § Deferred provider: Gemini.
- `00_System/Provider Registry.md`.
