---
ralph_type: provider
provider: openai-codex-deferred
status: deferred-spec
created: 2026-05-09
summary: "13-field provider-interface answers for OpenAI Codex CLI (template)."
---

# OpenAI Codex CLI — Adapter Spec (DEFERRED)

Template; fill in when activation is approved. The 13 fields below are
the canonical contract; conformance to the format IS the test.

## 1. prompt_input_format

Codex's CLI accepts a Markdown prompt + a config file. Translation:
Ralph would invoke `codex run --prompt-file <file>` (or stdin pipe).
Markdown frontmatter must be preserved.

## 2. context_package_format

Codex doesn't auto-load `CLAUDE.md`. The adapter would:
- read the vault `CLAUDE.md` at adapter init,
- prepend its content as a system message,
- use Codex's working-directory context to get project files.

## 3. memory_retrieval_package_format

Same as Claude Code: `harness query` returns Markdown. Codex accepts
Markdown unchanged.

## 4. tool_permission_model

Codex approval modes:
- `read-only`
- `auto` (suggest changes; user approves)
- `unsafe-auto` (auto-applies)

Map Ralph classes:
- LOW → `auto`
- MEDIUM → `auto`
- HIGH → require pre-approved proposal in `30-Notes/`
- CRITICAL → never autonomous (consistent with Claude Code adapter)

## 5. file_read_write_model

Codex sandboxed by default; use the repo-write mode. Sandbox the
adapter to repo + `$VAULT` only.

## 6. shell_execution_model

Codex's tool-call model (similar to Claude's Bash). Allowlist enforced
adapter-side.

## 7. approval_gate_model

Codex pauses on tool-approval prompts in `auto` mode; the adapter
intercepts and routes through Ralph's `pending-approvals.md`.

## 8. output_report_format

Stdout = Markdown. Codex's structured output mode helps generate the
expected `## [<date>] axis | k=v` log lines.

## 9. error_format

Standard exit codes (0/1/64/65/66/67/68 per provider-interface.md).
Codex's error JSON gets parsed adapter-side and translated.

## 10. evaluation_format

`metrics.ndjson` row gets `provider: "openai-codex"` and
`provider_version:` from `codex --version`.

## 11. logging_format

Karpathy LLM-Wiki format unchanged. Adapter writes to
`90-Meta/log.md` directly (same as Claude Code).

## 12. rollback_expectation

- Vault changes: `_archive/` mv (always reversible).
- Repo changes: git revert.
- Same as Claude Code.

## 13. provider_metadata

```yaml
id: openai-codex
version: <output of `codex --version`>
capabilities:
  - tool-use
  - structured-output
  - cloud-sandbox (security review needed)
  - long-context
```

## Open questions

- Does Codex CLI support custom hook scripts (pre/post-tool-use
  equivalents)? If not, Ralph's hooks become Claude-Code-only.
- Does Codex pass the Claude Mythos benchmark (92.1% Terminal-Bench
  2.0)? If yes, parity is achievable.
- Cost profile: per-call vs per-token vs subscription. The autoupdate
  cron would need cost-aware routing.

## Cross-references

- `providers/provider-interface.md` — the 13-field contract.
- `providers/openai-codex/deferred-implementation.md` — work estimate.
