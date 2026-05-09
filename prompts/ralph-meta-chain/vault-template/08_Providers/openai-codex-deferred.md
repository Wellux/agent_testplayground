---
ralph_type: provider
memory_layer: system
provider: openai-codex-deferred
status: deferred
created: 2026-05-09
summary: "OpenAI Codex CLI adapter — spec only, not active."
---

# Provider: OpenAI Codex CLI (DEFERRED)

Status: **DEFERRED** per user choice (Claude-Code-only runtime).
Adapter spec target: `providers/openai-codex/adapter-spec.md` (Round 4+).

## Reference

- https://github.com/openai/codex (75k stars, Apr 2026; Rust CLI).
- https://developers.openai.com/codex/cli — official docs.

## Why deferred

1. User explicitly picked Claude Code only.
2. Cloud-sandboxed agent variant ships code to OpenAI infra (privacy
   concern documented in `docs/SECURITY_PRIVACY.md`).
3. No bandwidth in current rounds.

## What activation would require

Per `docs/APPROVAL_GATES.md`: HIGH risk, requires:

1. populated 13-field `providers/openai-codex/adapter-spec.md`
2. threat-model review (cloud sandbox cost + privacy + capability),
3. fixtures pass under the new adapter (use existing
   `harness/fixtures/*.yml`),
4. explicit user approval.

## Adapter sketch (for Round 4+ implementer)

Codex's CLI accepts a Markdown prompt + a config file. Translation:

- `prompt_input_format`: Markdown with Codex preamble.
- `context_package_format`: same Markdown but flattened (Codex doesn't
  auto-load CLAUDE.md).
- `tool_permission_model`: Codex approval mode (`auto`, `unsafe-auto`,
  `read-only`). Map our LOW/MEDIUM/HIGH to these.
- `file_read_write_model`: Codex sandboxed by default; use the
  repo-write mode.
- `evaluation_format`: parse Codex telemetry → harness metrics.ndjson row
  with `provider: openai-codex`.

## Cross-references

- `docs/PROVIDER_NEUTRAL_ARCHITECTURE.md` § Deferred provider: OpenAI Codex.
- `00_System/Provider Registry.md`.
