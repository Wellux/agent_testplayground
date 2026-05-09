---
ralph_type: provider
memory_layer: system
provider: claude-code
status: active
created: 2026-05-09
summary: "The active runtime — Claude Code. All prompts shaped for this surface."
---

# Provider: Claude Code

Status: **ACTIVE**. Phase 1-6 reference implementation runs entirely on
this surface.

## Surface

- **Tool surface**: Read / Edit / Write / Bash / Grep / Glob /
  TodoWrite / Agent (Explore + general-purpose) / Skill / Task /
  WebSearch / WebFetch / `mcp__github__*` (when available).
- **Hooks**: pre-tool-use, post-tool-use, session-end, notification
  (all optional).
- **Skills**: `.claude/skills/<name>.md` per Anthropic spec.
- **Slash commands**: `.claude/commands/<name>.md`.
- **Settings**: `.claude/settings.json` permissions allow/deny.
- **CLAUDE.md**: project + vault-level operating rules.

## 13-field conformance

```yaml
prompt_input_format:           file:// URL or stdin via `claude -p`
context_package_format:        CLAUDE.md auto-loaded + Read tool fetches
memory_retrieval_package_format: `harness query` returns Markdown bullets with [[wikilinks]]
tool_permission_model:          .claude/settings.json allow/deny
file_read_write_model:          Edit / Write tools; sandboxed to repo
shell_execution_model:          Bash tool; allow/deny per settings
approval_gate_model:            user prompt for non-allowed tools
output_report_format:           Markdown to stdout
error_format:                   exit code + stderr
evaluation_format:              metrics.ndjson via `harness ab`
logging_format:                  90-Meta/log.md (Karpathy schema)
rollback_expectation:           git revert + vault `_archive/` mv
provider_metadata:              id="claude-code"; version=`claude --version`
```

## Cross-references

- `docs/CLAUDE_CODE_INTEGRATION.md` — full integration surface.
- `prompts/ralph-meta-chain/CLAUDE.md` — repo-level instructions.
- `seed/CLAUDE.md` — vault-level instructions.
- https://github.com/anthropics/claude-code — upstream.
