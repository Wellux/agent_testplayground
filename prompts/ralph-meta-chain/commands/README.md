# commands/ — Claude Code slash-command templates

Markdown templates that the user symlinks (or copies) into
`.claude/commands/<name>.md`. Per
`docs/CLAUDE_CODE_INTEGRATION.md` § Slash commands.

## Files in this folder

| Slash command                  | Wraps                                            | Risk class |
| ------------------------------ | ------------------------------------------------ | ---------- |
| `ralph-cron.md`                 | dashboard of all 8 axes (last run, status, next)  | LOW        |
| `ralph-memory.md`               | open the memory panel; show today's promotions    | LOW        |
| `ralph-skill.md`                | propose a new skill from the current note         | MEDIUM     |
| `ralph-experiment.md`           | generate an A/B fixture from the current note     | MEDIUM     |
| `ralph-research.md`             | show last research-ingest pass + topic coverage   | LOW        |
| `ralph-compress.md`             | show last hourly compression + pending bloat      | LOW        |
| `ralph-evolve.md`               | weekly fitness + open evolution proposals         | LOW        |
| `ralph-autoheal.md`              | invoke `harness self-test` + summarize            | LOW        |
| `ralph-autoupdate.md`            | open the latest weekly digest                     | LOW        |
| `ralph-business-review.md`       | open the pending-approvals ledger                  | LOW        |
| `ralph-migration-plan.md`        | invoke `harness migration --dry-run`               | MEDIUM     |

## Install

Use the canonical installer (idempotent; merges settings.json):

```bash
# Default: user-scoped (~/.claude/)
prompts/ralph-meta-chain/install/install_claude_code.sh

# Project-scoped (<repo>/.claude/)
prompts/ralph-meta-chain/install/install_claude_code.sh --scope project

# Vault-scoped ($VAULT/.claude/, reads vault_path from config.yml)
prompts/ralph-meta-chain/install/install_claude_code.sh --scope vault
```

The installer also wires up `agents/`, `skills/`, `hooks/`, the
permissions allowlist, and (if `--with-mcp`) the `ralph` MCP server.
See `install/CLAUDE_CODE_INSTALL.md` for the full surface map.

After install, type `/ralph-cron` (master dashboard) or any per-axis
command (`/ralph-memory`, `/ralph-research`, etc.) in any Claude Code
session whose cwd matches the install scope.

## File shape

Each command is a Markdown file with YAML frontmatter:

```yaml
---
description: |
  Triggers: "<phrase 1>", "<phrase 2>"
allowed-tools: ["Read", "Edit", "Bash(...)"]
---

# /<command-name>

<one-paragraph description>

## Inputs
$ARGUMENTS    # the slash command's arguments substitute here

## Process
1. ...

## Output
- ...
```

## Cross-references

- `docs/CLAUDE_CODE_INTEGRATION.md` § Slash commands.
- `providers/claude-code/commands.md` — the canonical list.
- `obsidian-plugin/src/main.ts` — many of these mirror plugin commands.
