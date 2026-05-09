# Claude Code install — Ralph meta-chain

This document is the canonical guide for making the Ralph meta-chain
**executable from inside Claude Code** (any of the four surfaces:
CLI, web app, desktop app, or VS Code/JetBrains extension).

## TL;DR

```bash
# Most common — install to ~/.claude/ for any Claude Code session anywhere.
prompts/ralph-meta-chain/install/install_claude_code.sh

# Per-repo install — only active when Claude Code is run inside this repo.
prompts/ralph-meta-chain/install/install_claude_code.sh --scope project

# Per-vault install — only active when Claude Code is run inside the vault
# (the vault path is read from prompts/ralph-meta-chain/config.yml).
prompts/ralph-meta-chain/install/install_claude_code.sh --scope vault

# Preview without writing:
prompts/ralph-meta-chain/install/install_claude_code.sh --dry-run
```

## What gets installed

The installer is **idempotent** (safe to re-run; tracks every artefact
in a manifest) and **non-destructive** (refuses to clobber any
non-symlink file). Into `<target>/.claude/`:

| Subdir         | Contents                                | Source in repo                            |
| -------------- | --------------------------------------- | ----------------------------------------- |
| `commands/`    | 11 slash commands (`/ralph-cron`, …)    | `prompts/ralph-meta-chain/commands/*.md`  |
| `agents/`      | 8 axis subagents                         | `prompts/ralph-meta-chain/agents/*.md`    |
| `skills/`      | 8 specialist skills                      | `prompts/ralph-meta-chain/skills/<slug>/` |
| `hooks/`       | 5 lifecycle hooks (`session-start`, …)   | `prompts/ralph-meta-chain/hooks/*.sh`     |
| `settings.json`| Permissions allowlist + hook bindings    | merged from `config.example.yml` + `hooks.example.json` |
| `.mcp.json`    | `ralph` MCP server registration          | `prompts/ralph-meta-chain/mcp-server/`    |

Plus `.ralph-installed.json` — a manifest the uninstaller reads to
remove exactly what we put there.

## Scope choice

| Scope     | Target                           | When to use                                                             |
| --------- | -------------------------------- | ----------------------------------------------------------------------- |
| `user`    | `~/.claude/`                     | DEFAULT. You want `/ralph-cron` etc. available in any cwd.              |
| `project` | `<repo>/.claude/`                | You want the surface only when developing IN this repo (collaborators get it via git). |
| `vault`   | `<vault>/.claude/`               | You run `claude` from inside your Obsidian vault. The vault becomes self-installing. |

Multiple scopes can coexist. Project + vault installs override the
user install when their respective cwd matches.

## Verify the install

```bash
# 1. The four directories are populated:
ls ~/.claude/commands  ~/.claude/agents  ~/.claude/skills  ~/.claude/hooks

# 2. The manifest exists and lists what we tracked:
cat ~/.claude/.ralph-installed.json | jq .symlinks | head

# 3. Settings.json picked up the merged permissions + hooks:
jq '.permissions.allow | length, .hooks | keys' ~/.claude/settings.json

# 4. MCP server registered (if --with-mcp):
jq '.mcpServers.ralph' ~/.claude/.mcp.json

# 5. From inside Claude Code:
#    Type:  /ralph-cron
#    Expect: master dashboard with all 8 axes
```

## Surface map

After install, you have **three layers** of Ralph access from inside
Claude Code:

### 1. Slash commands (interactive, type-this-now)

Each is a read-only dashboard. Safe to invoke at any time.

```
/ralph-cron               ← master dashboard of all 8 axes
/ralph-memory             ← what got promoted overnight
/ralph-skill              ← propose a skill from the current note
/ralph-experiment         ← spawn an A/B fixture
/ralph-research           ← what arrived from upstream
/ralph-compress           ← what got compressed; what's bloated
/ralph-evolve             ← weekly fitness + open proposals
/ralph-autoheal           ← run validators + summarize
/ralph-autoupdate         ← weekly Monday digest
/ralph-business-review    ← pending approvals ledger
/ralph-migration-plan     ← preview the next migration pass
```

### 2. Subagents (delegated specialists)

Claude routes to these when it decides a task fits an axis. Trigger
phrases live in each agent's frontmatter `description:`. Example:

> User: "Promote the inbox notes from yesterday into atomic notes."
> Claude: *delegates to* `Agent(ralph-memory, prompt="...")`

The 8 axis subagents are: `ralph-research`, `ralph-memory`,
`ralph-skills`, `ralph-interaction`, `ralph-compress`,
`ralph-autoheal`, `ralph-evolve`, `ralph-update`. Each one runs the
canonical prompt in its own context window.

### 3. MCP tools (programmatic, from inside Claude's reasoning)

Four tools the model can call without a Bash shell:

```
ralph_query                semantic search of the vault                   (read-only)
ralph_axis_status          last log line for one or all axes               (read-only)
ralph_self_test            run the local CI mirror                          (read-only)
ralph_migration_dry_run    generate migration proposal Markdown            (writes proposals; never moves files)
```

The first three are strictly read-only. `ralph_migration_dry_run`
writes proposal Markdown into `migration/` (proposed-moves.md,
rollback-plan.md, conflicts.md if any) but never moves files — the
proposals ARE the artefact. Revert with
`git restore prompts/ralph-meta-chain/migration/`. The tool's MCP
description surfaces this to the LLM client.

These hit the `harness` CLI / `migration/scripts/` under the hood.
The MCP server is documented in `mcp-server/README.md`.

## Hooks installed

| Event         | Hook                | Purpose                                                  |
| ------------- | ------------------- | -------------------------------------------------------- |
| `SessionStart`| `session-start.sh`  | One-screen briefing of the chain's state on every launch |
| `PreToolUse`  | `pre-tool-use.sh`   | Block forbidden Bash patterns; log every tool call       |
| `PostToolUse` | `post-tool-use.sh`  | Append duration to log; bump heal-check counters         |
| `Stop`        | `session-end.sh`    | Drop a session-capture stub into `00_Inbox/`             |
| `Notification`| `notification.sh`   | Route important notifications to the user                |

Each hook honours the fail-safe contract: never blocks Claude Code,
hard 10s timeout, no network, fail-quiet on errors.

## Permissions installed

Set-union'd into `<target>/.claude/settings.json` (your existing
permissions are preserved):

**Allow** (read-only or vault-scoped writes only):

```
Read(**)
Write($VAULT/**)
Edit($VAULT/**)
Bash(mkdir:*,grep:*,find:*,wc:*,jq:*,git status,git log:*,test:*,touch:*,mv:*)
Bash(uv:*,python:*,python3:*,node:*,npm:*)
Bash(harness:*,ollama:*)
Agent(Explore)
Agent(general-purpose)
TodoWrite
```

**Deny**:

```
Bash(rm:*)
Bash(git push:*)
Bash(git reset:*)
Bash(curl:*)
Bash(wget:*)
Bash(ssh:*)
```

The chain itself never asks for `git push` or `curl` — these are
denied so the model can't accidentally invoke them via tool use.

## Uninstall

```bash
prompts/ralph-meta-chain/install/uninstall_claude_code.sh --scope user
# Or project / vault as appropriate. Honours --dry-run.
```

The uninstaller reads the manifest and removes:
- Every tracked symlink (only if it still points inside the repo).
- Hook bindings whose command path lives in the install target.
- Permissions entries that originated from `config.example.yml`.
- The `ralph` entry in `.mcp.json`.
- The manifest itself, then any now-empty subdirs.

It will **not** touch hooks, permissions, or files you added yourself.

## Troubleshooting

**"refuses: ~/.claude/commands/ralph-memory.md exists and is not a symlink"**
The installer never overwrites real files. Move the existing one
aside (e.g. rename to `.bak`) and re-run.

**"vault_path missing from config.yml"**
You used `--scope vault` but haven't created `config.yml`. Either
`cp config.example.yml config.yml` and edit `vault_path:` first, or
use `--scope user` / `--scope project`.

**`/ralph-cron` not visible inside Claude Code**
The installer wrote to your selected scope; Claude Code looks in
`<cwd>/.claude/` and `~/.claude/`. If you used `--scope project`,
`cd` into the repo. If you used `--scope vault`, `cd` into the
vault.

**Hook fires but produces no output**
SessionStart hook needs `$VAULT/` to exist. Set the env var before
launching Claude Code, or it falls back to
`~/Obsidian/SecondBrain` (skips silently if absent).

**MCP server not loading**
Check `~/.claude/.mcp.json` paths are absolute. Run the manual
smoke test in `mcp-server/README.md`. The server has zero deps so
it should import on any Python 3.11+.

## Cross-references

- `commands/README.md` — slash command catalog.
- `agents/README.md` — subagent catalog.
- `skills/` — specialist skill catalog (one folder per skill).
- `hooks/README.md` — hook scripts + fail-safe contract.
- `mcp-server/README.md` — MCP server protocol details.
- `providers/claude-code/runtime-notes.md` — 13-field provider conformance.
- `install/install_cron.sh` — separately installs the **scheduled** cron
  axis runs (different from this install, which makes the chain
  available **interactively**).
