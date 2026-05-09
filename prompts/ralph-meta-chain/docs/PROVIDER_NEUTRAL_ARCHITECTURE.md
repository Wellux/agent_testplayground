# PROVIDER_NEUTRAL_ARCHITECTURE.md

## Purpose

Specify the provider-neutral *architecture* without activating any
non-Claude runtime. Claude Code is the **only active runtime** today.
Codex, Gemini AI Studio, and local models have adapter specs documented
here so a future round can light them up without redesigning the chain.

The master spec rule: "Provider-neutral architecture must not
accidentally execute non-Claude runtimes."

## Provider interface

A provider adapter must implement the following surface:

```yaml
# providers/<vendor>/adapter-spec.md
prompt_input_format: |
  How the adapter accepts a Ralph prompt.md file.
context_package_format: |
  How $VAULT/CLAUDE.md + retrieved notes get attached to the call.
memory_retrieval_package_format: |
  Format of the harness query result that goes in.
tool_permission_model: |
  How the adapter enforces config.yml's allow/deny.
file_read_write_model: |
  How the adapter mutates vault files.
shell_execution_model: |
  Subprocess execution model + Bash allow/deny.
approval_gate_model: |
  How the adapter pauses on HIGH/CRITICAL operations.
output_report_format: |
  Markdown report shape.
error_format: |
  Error rendering shape.
evaluation_format: |
  metrics.ndjson schema produced by the adapter.
logging_format: |
  log.md line shape.
rollback_expectation: |
  How the adapter supports rollback on apply.
provider_metadata: |
  ID, version, capabilities.
```

Every adapter that wants to host a Ralph axis MUST satisfy this surface.
Format conformance is the test for "Ralph runs on this provider".

## Active provider: Claude Code

Status: ACTIVE.

- Tool surface: Read / Edit / Write / Bash / Grep / Glob / TodoWrite /
  Agent (Explore + general-purpose) / Skill / Task / WebSearch /
  WebFetch / mcp__github__* (when MCP available).
- Hooks: pre-tool-use, post-tool-use, session-end, notification (all
  optional).
- Skills: `.claude/skills/<name>.md` per Anthropic spec.
- Slash commands: `.claude/commands/<name>.md`.
- Settings: `.claude/settings.json` permissions allow/deny.

The Phase 1-6 reference implementation runs entirely on this surface.
Every prompt at `prompts/ralph-meta-chain/0[1-8]-*.md` is shaped for
Claude Code.

## Deferred provider: OpenAI Codex

Status: DEFERRED. Adapter spec target: `providers/openai-codex/`.

- Reference: https://github.com/openai/codex (75k stars, Apr 2026).
- Surface: Rust CLI; cloud-sandboxed agent variant.
- Why deferred: user picked Claude-Code-only; cloud sandbox sends code
  to vendor.
- What the adapter would do (when activated):
  - Translate Ralph prompts (Markdown + frontmatter) to Codex's input
    format.
  - Map permissions allow/deny to Codex's approval mode.
  - Mirror metrics.ndjson schema by Codex telemetry → harness format.
  - Fixtures stay portable: `harness/fixtures/*.yml` already work via
    `promptfoo eval` against any provider.
- What it does NOT do today: nothing. No code calls Codex.

## Deferred provider: Gemini / AI Studio

Status: DEFERRED. Adapter spec target: `providers/gemini-ai-studio/`.

- Reference: AI Studio + Vertex AI Codey.
- Why deferred: same — Claude Code only by user choice.
- Adapter would do: translate to Gemini's tool spec; map vault file ops
  to Vertex's file API; preserve metrics.ndjson schema.

## Deferred provider: Local models (Ollama)

Status: PARTIAL — embeddings already use Ollama (`nomic-embed-text`).
Adapter spec target: `providers/local-models/`.

- Reference: `ollama/ollama` for hosting; specific models swappable.
- What's already integrated: embeddings (Ollama is the embedding
  backend).
- What's NOT integrated: prompt completion. The harness `judge` and
  `compress` calls go through Anthropic API exclusively.
- Adapter would: route `harness ab --judge-model <local-llm>` to a
  local Ollama completion endpoint. The format is already JSON-only
  rubric; LLM-agnostic.

## Provider metadata

Every experiment/proposal carries provider metadata:

```yaml
provider: claude-code
provider_version: "<sdk-version>"
model: claude-sonnet-4-6
```

This makes A/B comparisons portable: a future round could compare
"Claude Code on prompt v3" vs "Codex on prompt v3" with no fixture
changes.

## Rules

1. **Claude Code is active. Period.** No code in this repo calls Codex,
   Gemini, or non-Anthropic models. If a user wires up an external
   adapter, they do it explicitly via `providers/<vendor>/`.
2. **Prompt + memory formats stay portable.** Markdown with YAML
   frontmatter; `[[wikilinks]]`. No Claude-specific tokens.
3. **metrics.ndjson schema is provider-agnostic.** Each row carries
   `provider`, `model`, `judge_model`. A/B across providers works
   trivially.
4. **Adapter activation is HIGH-risk.** Per `APPROVAL_GATES.md`, lighting
   up a deferred adapter requires explicit invocation + threat-model
   review.
5. **Cloud-sandboxed variants need extra review.** Codex's cloud agent
   ships code to OpenAI's infra; that's a separate threat-model exercise.

## Safety notes

- **No accidental routing.** The `provider:` frontmatter field is
  authoritative. If a prompt declares `provider: claude-code`, the
  harness refuses to run it through any other adapter.
- **No defaults to "first available".** If `embeddings.backend: cognee`
  is set but Cognee isn't installed, the harness errors clearly rather
  than falling back to a different (possibly cloud) backend.
- **Deferred ≠ skeleton.** The adapter specs are real; future rounds
  populate them. Do not interpret deferral as "we'll figure this out
  later" — the contract above is the contract.

## Cross-references

- `ARCHITECTURE.md` — Claude Code's place in the system.
- `MEMORY_MODEL.md` — `provider:` frontmatter field.
- `AB_HARNESS.md` — provider metadata in metrics rows.
- `APPROVAL_GATES.md` — adapter activation is HIGH/CRITICAL.
- Phase 1-6 reference: `harness/harness/memory_backends.py` is the only
  pluggable layer today; everything else is Claude-Code-specific.

## Next actions

If you only run Claude Code, ignore this doc — the Phase 1-6 reference
implementation has you covered. If you want to compare against another
runtime, populate `providers/<vendor>/adapter-spec.md` (Round 4+) and
follow the adapter activation gate in `APPROVAL_GATES.md`.
