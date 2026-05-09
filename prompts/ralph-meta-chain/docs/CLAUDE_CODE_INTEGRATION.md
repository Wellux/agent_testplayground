# CLAUDE_CODE_INTEGRATION.md

## Purpose

How Ralph Meta Chain plugs into Claude Code's surface: the project
`CLAUDE.md`, hooks, skills, slash commands, settings, and permissions.
Claude Code is the **active runtime**; provider-neutral specs are kept
in `PROVIDER_NEUTRAL_ARCHITECTURE.md` for future adapters.

## Project CLAUDE.md

Two CLAUDE.md files matter:

- **Repo CLAUDE.md** at `prompts/ralph-meta-chain/CLAUDE.md` — loaded
  by any Claude Code session opened in this repo. Documents safety
  boundaries, file boundaries, dry-run-first, approval gates, and the
  Phase 1-6 reference implementation paths.
- **Vault CLAUDE.md** at `$VAULT/CLAUDE.md` — Karpathy "schema" layer.
  Loaded by every Ralph cron firing via `Read`. Documents the
  Zettelkasten layout, frontmatter contracts, append-only invariants,
  and Voyager / MAP-Elites / Reflexion rules.

The repo CLAUDE.md teaches Claude Code about *the codebase*; the vault
CLAUDE.md teaches Ralph (a Claude Code session) about *the user's
second brain*.

## Slash commands

Defined under `.claude/commands/<name>.md` in the user's project (NOT in
this repo, since slash commands are user-scoped). Reference templates
live in `prompts/ralph-meta-chain/commands/` (Round 5+):

- `/ralph-memory` — open the memory panel; show today's promotions.
- `/ralph-skill` — propose a new skill from the current note.
- `/ralph-experiment` — generate an A/B fixture from the current note.
- `/ralph-autoheal` — invoke `harness self-test` + summarize.
- `/ralph-autoupdate` — open the latest weekly digest.
- `/ralph-business-review` — open the pending-approvals ledger.
- `/ralph-migration-plan` — invoke `harness migration --dry-run`.

Each command is a Markdown file with a YAML frontmatter `description:`
that contains trigger phrases.

## Skills

Skill files live at `$VAULT/40-Skills/<slug>.md` and follow the
charlie947/ai-second-brain frontmatter:

```yaml
---
name: <slug>
description: |
  Triggers: "...", "..."
when_to_use: |
  ...
inputs:
  - ...
steps:
  - ...
tools: ["Bash(...)", "mcp__github__create_pull_request", ...]
failure_modes:
  - ...
last_validated: <YYYY-MM-DD>
metrics: { invocations: 0, success_rate: null, mean_tokens: null }
prerequisites: []
is_prerequisite_of: []
links: []
tags: [skill]
---
```

Day-1 seeds at `prompts/ralph-meta-chain/seed/40-Skills/recall.md` and
`pr-from-branch.md`. Voyager curriculum: `recall` is foundation;
`pr-from-branch` depends on `recall`.

## Hooks

Hook examples ship in `prompts/ralph-meta-chain/hooks/` (Round 5+):

| Hook event       | Purpose                                          | Risk class |
| ---------------- | ------------------------------------------------ | ---------- |
| pre-tool-use     | guard against forbidden Bash patterns (e.g. `rm`) | LOW        |
| post-tool-use    | append a line to `90-Meta/log.md` per tool call   | LOW        |
| session-end      | propose a memory-capture for the session         | MEDIUM     |
| notification     | placeholder for desktop notification routing     | MEDIUM     |

Hooks must be **fail-safe**: a non-zero exit from a hook script must
NOT block Claude Code; it logs to `90-Meta/heal-checks.ndjson` and the
heal axis picks up the failure.

Hook installation is HIGH-risk and requires explicit user invocation
(via `install.sh --hooks`, Round 5+).

## Settings + permissions

The `permissions` block in `prompts/ralph-meta-chain/config.example.yml`
mirrors Claude Code's settings.json shape:

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

Allowlist-first; everything outside `allow` is implicitly denied. The
`deny` block is belt-and-suspenders for high-risk patterns that might
accidentally appear in `allow`.

## MCP servers

The chain uses these MCP server tools where available:

- `mcp__github__*` — for the `pr-from-branch` skill, autoheal CI checks,
  and PR-event subscription.
- (Future) `mcp__obsidian__*` — Round 6+ when an Obsidian MCP exists.

Ralph never *requires* MCP availability. Every MCP call has a fallback
(skip + log + tag `#unrecalled`).

## Subagent delegation

Every prompt uses `Agent(subagent_type=Explore)` for read-mostly digestion
to keep main-context tight:

- Memory: 1× over `00-Inbox/`, 1× over `10-Daily/`.
- Skills: 1× over `40-Skills/`, 1× general-purpose mining.
- Interaction: 1× over `60-Interactions/`, 1× general-purpose extraction.
- Heal: 1× over `90-Meta/log.md` tail.

Subagent results return as compact digests; the main prompt does not
re-read the raw files.

## Safety notes

- The vault CLAUDE.md is loaded into context **at every firing**. Treat
  edits as MEDIUM risk.
- Hook installation is HIGH risk (system-wide impact on every Claude
  Code session). Default: not installed.
- Permissions allowlist is the **first line of defense**. Removing a
  `deny:` entry is HIGH risk; adding one is LOW.

## Cross-references

- Repo `prompts/ralph-meta-chain/CLAUDE.md`.
- Vault `seed/CLAUDE.md` (template installed by `install.sh seed_vault`).
- `OBSIDIAN_PLUGIN.md` — the corresponding Obsidian-side surface.
- `APPROVAL_GATES.md` — risk classes for hooks / settings.
- `AB_HARNESS.md` — how skills + prompts are evaluated.
- Phase 1-6 reference: `prompts/ralph-meta-chain/seed/40-Skills/`,
  `harness/harness/judge.py`.

## Next actions

After this, read `OBSIDIAN_PLUGIN.md` for the corresponding plugin
surface, then `AB_HARNESS.md` for how skills + prompts get evaluated.
