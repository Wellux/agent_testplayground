# commands/ — Claude Code slash-command templates

Markdown templates that the user symlinks (or copies) into
`.claude/commands/<name>.md`. Per
`docs/CLAUDE_CODE_INTEGRATION.md` § Slash commands.

## Files in this folder

| Slash command                  | Wraps                                            | Risk class |
| ------------------------------ | ------------------------------------------------ | ---------- |
| `ralph-memory.md`               | open the memory panel; show today's promotions    | LOW        |
| `ralph-skill.md`                | propose a new skill from the current note         | MEDIUM     |
| `ralph-experiment.md`           | generate an A/B fixture from the current note     | MEDIUM     |
| `ralph-autoheal.md`              | invoke `harness self-test` + summarize            | LOW        |
| `ralph-autoupdate.md`            | open the latest weekly digest                     | LOW        |
| `ralph-business-review.md`       | open the pending-approvals ledger                  | LOW        |
| `ralph-migration-plan.md`        | invoke `harness migration --dry-run`               | MEDIUM     |

## Install

```bash
# Per-project install:
ln -s "$REPO/prompts/ralph-meta-chain/commands" .claude/commands

# Per-user install:
mkdir -p ~/.claude/commands
ln -sf "$REPO/prompts/ralph-meta-chain/commands"/*.md ~/.claude/commands/
```

After install, type `/ralph-memory` etc. in any Claude Code session.

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
