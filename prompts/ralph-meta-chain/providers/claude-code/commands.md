---
ralph_type: provider
provider: claude-code
created: 2026-05-09
status: scaffold
summary: "Claude Code slash-command surface — patterns + planned commands."
---

# Claude Code Slash Commands

Slash commands let the user invoke Ralph workflows from Claude Code's
prompt without typing the full underlying instruction. Files live at
`.claude/commands/<name>.md` (user-scoped) or
`prompts/ralph-meta-chain/commands/<name>.md` (Round 5+ shipped).

## Command file shape

```markdown
---
description: |
  Triggers: "<phrase 1>", "<phrase 2>"
allowed-tools: ["Read", "Edit", "Bash(harness:*)"]
---

# /<command-name>

<one-paragraph description of what the command does>

## Inputs
$ARGUMENTS    # ← the slash command's arguments substitute here

## Process
1. ...
2. ...

## Output
- ...
```

## Planned commands (Round 5+)

| Slash command                  | Wraps                                            | Risk |
| ------------------------------ | ------------------------------------------------ | ---- |
| `/ralph-memory`                 | open the memory panel; show today's promotions    | LOW  |
| `/ralph-skill`                  | propose a new skill from the current note         | MEDIUM |
| `/ralph-experiment`             | generate an A/B fixture from the current note     | MEDIUM |
| `/ralph-autoheal`                | invoke `harness self-test` + summarize            | LOW  |
| `/ralph-autoupdate`              | open the latest weekly digest                     | LOW  |
| `/ralph-business-review`         | open the pending-approvals ledger                  | LOW  |
| `/ralph-migration-plan`          | invoke `harness migration --dry-run`               | MEDIUM |

## Argument handling

Slash commands accept `$ARGUMENTS` (single string of everything after
the command). Multi-arg parsing happens inside the command file; per
master spec, Ralph commands stay simple and accept either a single
string or a single named argument.

## Cross-references

- `docs/CLAUDE_CODE_INTEGRATION.md` § Slash commands.
- Round 5+ ships these as `.md` files under
  `prompts/ralph-meta-chain/commands/`.

## Next actions

- For Round 4 (this round): no slash commands shipped; the planned
  list above is the spec.
- Round 5 wires the commands as Markdown files; users symlink them
  into `.claude/commands/`.
