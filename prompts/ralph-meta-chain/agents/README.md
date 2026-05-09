# agents/ — Claude Code subagent definitions (one per Ralph axis)

Each `ralph-<axis>.md` file is a Claude Code subagent definition — a
specialist persona that the Agent tool can route to when the user
delegates an axis-specific task. These are *complementary* to the
slash commands in `commands/`:

- **Slash commands** (`/ralph-memory`, …) — interactive, type-this-now,
  read-only dashboards.
- **Subagents** (`Agent(ralph-memory, …)`) — invoked by Claude when
  it decides a task fits the specialist; the subagent runs the
  axis prompt to completion in its own context.

## Files

| Subagent           | Wraps prompt                       | When Claude routes to it |
| ------------------ | ---------------------------------- | ------------------------ |
| `ralph-research.md`     | `04-research-ingest.md`            | "fetch repos for topic X" / "ingest research" |
| `ralph-memory.md`       | `01-memory-optimizer.md`           | "promote inbox" / "MOC pass" / "memory promotion" |
| `ralph-skills.md`       | `02-skills-optimizer.md`           | "synthesize skill from N notes" / "Voyager step" |
| `ralph-interaction.md`  | `03-interaction-optimizer.md`      | "A/B this prompt" / "rewrite the system prompt" |
| `ralph-compress.md`     | `05-compress.md`                   | "compress this note" / "weekly rollup" |
| `ralph-autoheal.md`     | `06-autoheal.md`                   | "diagnose this red check" / "triage validator failure" |
| `ralph-evolve.md`       | `07-autoevolve.md`                 | "score the chain's fitness" / "propose mutation" |
| `ralph-update.md`       | `08-autoupdate.md`                 | "scan releases" / "draft a bump proposal" |

## Install

The installer (`install/install_claude_code.sh`) symlinks these into
`<target>/.claude/agents/<axis>.md`. After install, Claude can use
the Agent tool with `subagent_type: ralph-<axis>` to route.

## File shape

Each file is a Markdown document with YAML frontmatter:

```yaml
---
name: ralph-<axis>
description: Use this agent when ...
tools: Read, Edit, Bash(...)
model: inherit
---

You are a specialist for the <axis> axis of the Ralph meta-chain.

[axis-specific instructions; reference the prompt file]
```

## Cross-references

- `commands/README.md` — interactive slash commands.
- `0[1-8]-*.md` — the eight axis prompts the subagents reference.
- `providers/claude-code/runtime-notes.md` § Agent dispatch.
