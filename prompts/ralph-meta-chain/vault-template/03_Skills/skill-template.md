---
ralph_type: skill
memory_layer: procedural
created: 2026-05-09
status: template
name: <slug>
description: |
  Triggers: "<phrase 1>", "<phrase 2>", "<phrase 3>"
when_to_use: |
  Brief description of when this skill is appropriate.
inputs:
  - input_name: type / default / description
steps:
  - "1. ..."
  - "2. ..."
  - "3. ..."
tools:
  - "Bash(cmd1:*,cmd2:*)"
  - "mcp__github__create_pull_request"
failure_modes:
  - condition → response
last_validated: 2026-05-09
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: []
is_prerequisite_of: []
links: []
tags: [skill, template]
---

# <Skill Name>

One-paragraph description of what the skill does.

## Canonical experiment

Replay format: how to test that this skill still works. Time-cap:
`ralph.experiment_minutes`. The `02-skills-optimizer` cron runs this
when the skill's `last_validated` is > 14d old.

## Examples

### Example 1: <case>

Input:
```
...
```

Expected output:
```
...
```

## Cross-references

- `docs/CLAUDE_CODE_INTEGRATION.md` § Skills.
- `00_System/Skill Registry.md` — index of every active skill.
- `02-skills-optimizer.md` — how skills get amended.
- Voyager curriculum: link to `prerequisites:` and from `is_prerequisite_of:`.
