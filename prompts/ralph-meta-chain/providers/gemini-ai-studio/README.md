---
ralph_type: provider
provider: gemini-ai-studio-deferred
status: deferred
created: 2026-05-09
summary: "Gemini AI Studio adapter — DEFERRED."
---

# Provider: Gemini AI Studio (DEFERRED)

The user picked Claude Code only. Gemini's API + Vertex AI Codey is
the mature Google option; AI Studio is the developer surface. Cloud-
only.

## Why deferred

1. User explicitly picked Claude Code only.
2. Cloud-only — ships code/data to Google infra. Privacy review
   required before activation.
3. Tool-calling shape differs (function-call schemas) — non-trivial
   adapter translation.
4. No bandwidth in current rounds.

## Files in this folder

- `README.md` ← you are here.
- `adapter-spec.md` — 13-field template.
- `deferred-implementation.md` — work estimate.

## Cross-references

- https://aistudio.google.com — AI Studio.
- https://cloud.google.com/vertex-ai — Vertex.
- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` § Deferred provider: Gemini.
