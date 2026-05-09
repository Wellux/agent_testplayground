---
ralph_type: provider
provider: gemini-ai-studio-deferred
status: deferred-spec
created: 2026-05-09
summary: "13-field provider-interface answers for Gemini AI Studio (template)."
---

# Gemini AI Studio — Adapter Spec (DEFERRED)

Fill in when activation is approved.

## 1. prompt_input_format

Gemini's API takes a structured-content array (parts: text + tool
calls + media). The adapter would:
- accept Markdown,
- wrap as `{ "parts": [{ "text": <markdown> }] }`.

## 2. context_package_format

System message for the vault `CLAUDE.md`. No auto-load equivalent.

## 3. memory_retrieval_package_format

Markdown bullets. Same as other adapters.

## 4. tool_permission_model

Gemini's function-call config has `mode: AUTO | ANY | NONE`. Map:
- LOW → AUTO
- MEDIUM → AUTO + adapter post-validation
- HIGH → adapter intercepts; routes through `pending-approvals.md`
- CRITICAL → never autonomous

## 5. file_read_write_model

Vertex's file-handle API for cloud-side artifacts. For Ralph's local-
first stance, the adapter mediates: reads from local disk, writes go
to local disk only; no Vertex storage.

## 6. shell_execution_model

Gemini doesn't expose a Bash tool natively; the adapter declares a
function `bash_exec` that runs locally on the host. Allowlist enforced
adapter-side.

## 7. approval_gate_model

Adapter intercepts function calls classified HIGH/CRITICAL and routes
through `pending-approvals.md`.

## 8. output_report_format

Markdown via the adapter's response decoder.

## 9. error_format

Standard exit codes. Gemini API errors translated adapter-side.

## 10. evaluation_format

`metrics.ndjson` row with `provider: "gemini-ai-studio"` and
`provider_version:` from the API.

## 11. logging_format

Karpathy LLM-Wiki format unchanged.

## 12. rollback_expectation

Same as Claude Code (vault `_archive/` + git revert).

## 13. provider_metadata

```yaml
id: gemini-ai-studio
version: <api-version>
capabilities:
  - tool-use (function-calling)
  - structured-output
  - long-context (1M-2M tokens depending on model)
  - cloud-only (security review)
```

## Open questions

- Does Vertex's function-calling support multi-turn tool use the way
  Claude Code does? Verify with a fixture replay during activation.
- Cost profile for long-context. Ralph reads vault content;
  context can grow.
- API key management. Where does the key live — `harness/.env` or a
  separate secret store?

## Cross-references

- `providers/provider-interface.md`.
- `providers/gemini-ai-studio/deferred-implementation.md`.
