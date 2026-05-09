---
ralph_type: provider
provider: claude-code
stability: canonical
created: 2026-05-09
status: active
summary: "13-field provider-interface answers for Claude Code."
---

# Claude Code — Runtime Notes

13-field conformance to `providers/provider-interface.md`.

## 1. prompt_input_format

`claude -p "<prompt-text>"` accepts the prompt on the command line.
Markdown with YAML frontmatter is preserved end-to-end. For long
prompts, pipe via stdin: `cat 01-memory-optimizer.md | claude -p`.

## 2. context_package_format

Claude Code auto-loads `CLAUDE.md` files from cwd-up and from
`~/.claude/CLAUDE.md`. The vault `CLAUDE.md` is read explicitly by each
Ralph prompt at runtime via the Read tool; the repo CLAUDE.md is
auto-loaded.

## 3. memory_retrieval_package_format

`harness query --semantic "<q>"` returns Markdown bullets with
`[[wikilinks]]`. Claude Code's Read tool fetches the linked targets
on demand.

## 4. tool_permission_model

`.claude/settings.json` `permissions.allow` / `deny`. Per-call user
approval for non-allowed patterns. The Ralph chain adds an explicit
allowlist in `prompts/ralph-meta-chain/config.example.yml`:

```yaml
permissions:
  allow:
    - "Read(**)"
    - "Write($VAULT/**)"
    - "Edit($VAULT/**)"
    - "Bash(mkdir:*,grep:*,find:*,wc:*,jq:*,git status,git log:*,test:*,touch:*,mv:*)"
    - "Bash(uv:*,python:*,python3:*,node:*,npm:*)"
    - "Bash(harness:*,ollama:*)"
    - "Agent(Explore)"
    - "Agent(general-purpose)"
    - "TodoWrite"
  deny:
    - "Bash(rm:*)"
    - "Bash(git push:*)"
    - "Bash(git reset:*)"
    - "Bash(curl:*)"
    - "Bash(wget:*)"
    - "Bash(ssh:*)"
```

## 5. file_read_write_model

Edit / Write tools, sandboxed to repo + `$VAULT`. Read can fetch any
allowed path.

## 6. shell_execution_model

Bash tool with allow/deny patterns. argv-array semantics; no shell
string injection by default.

## 7. approval_gate_model

User prompt for non-allowed tools (interactive sessions). Stop hook
for the Ralph-Wiggum loop (`<promise>COMPLETE</promise>` exit
contract). For headless cron runs: refuses non-allowed tools outright.

## 8. output_report_format

Stdout = Markdown. The Ralph prompts emit a Karpathy `## [<date>] axis
| k=v` line at end of pass into `90-Meta/log.md`.

## 9. error_format

Stderr = error message; exit code from `claude -p` reflects the
agent's last-iteration state. The Ralph loop converts:

- `<promise>COMPLETE</promise>` emitted → exit non-zero (so outer
  `until !` halts).
- otherwise exit 0 → loop re-feeds the same prompt.

## 10. evaluation_format

`harness ab` writes `metrics.ndjson` rows with `provider:
"claude-code"` and `provider_version:` from `claude --version`.
Schema per `docs/AB_HARNESS.md`.

## 11. logging_format

`90-Meta/log.md` Karpathy format. Ralph prompts emit one line at the
end of each pass:
```
## [YYYY-MM-DD] <axis> | <k>=<v> ...
```

## 12. rollback_expectation

- Vault changes: `_archive/` mv (always reversible).
- Repo changes: git revert.
- Round 8 migration: `ralph_rollback_migration.sh`.

## 13. provider_metadata

```yaml
id: claude-code
version: <output of `claude --version`>
capabilities:
  - tool-use
  - structured-output
  - long-context
  - hooks (pre-tool-use / post-tool-use / session-end / notification)
  - skills (.claude/skills/<name>.md)
  - slash-commands (.claude/commands/<name>.md)
  - ralph-wiggum-plugin (Stop hook + completion-promise)
  - mcp
```

## Cross-references

- `providers/provider-interface.md` — the 13-field contract.
- `docs/CLAUDE_CODE_INTEGRATION.md` — full surface.
- `claude-code/{hooks,commands,skills}.md` — sub-surface details.
