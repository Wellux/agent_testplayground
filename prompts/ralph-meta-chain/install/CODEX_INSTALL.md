# Codex install — Ralph meta-chain

This document is the canonical guide for making the Ralph meta-chain
**executable from inside the OpenAI Codex CLI** — the sister install
to `CLAUDE_CODE_INSTALL.md`.

## TL;DR

```bash
# Most common — install to ~/.codex/ + ~/.agents/skills/ for any Codex session.
prompts/ralph-meta-chain/install/install_codex.sh

# Project-scoped: writes ONLY skills (.agents/skills/) into the repo. MCP +
# prompts stay user-scoped (Codex config.toml is user-only).
prompts/ralph-meta-chain/install/install_codex.sh --scope project

# Vault-scoped: writes skills + AGENTS.md into the vault, so Codex run
# from inside the vault discovers everything by walking up.
prompts/ralph-meta-chain/install/install_codex.sh --scope vault

# Preview without writing:
prompts/ralph-meta-chain/install/install_codex.sh --dry-run

# Skills-only mode (no slash-command prompts):
prompts/ralph-meta-chain/install/install_codex.sh --without-prompts
```

## What gets installed

| Surface                           | Path                                       | Source in repo                                   |
| --------------------------------- | ------------------------------------------ | ------------------------------------------------ |
| **8 axis skills**                  | `<skills_root>/ralph-<axis>/SKILL.md`       | wraps `agents/ralph-<axis>.md` in a skill dir    |
| **8 specialist skills**            | `<skills_root>/<slug>/`                     | symlink to `skills/<slug>/`                      |
| **11 slash-command prompts**       | `<prompts_dir>/ralph-*.md`                  | symlink to `commands/*.md`                       |
| **MCP server `ralph`**             | `[mcp_servers.ralph]` in `<toml_file>`      | merged from `mcp-server/`                        |
| **AGENTS.md briefing**             | `<briefing_dir>/AGENTS.md`                  | `install/AGENTS.template.md` (cp; never clobbers)|
| **Manifest**                       | `<manifest_dir>/.ralph-installed.json`      | for `uninstall_codex.sh`                         |

All paths are **scope-aware** so a project/vault install never leaks
into the user-global `$CODEX_HOME` (Codex P2 review on PR #2):

| Scope     | `<skills_root>`         | `<prompts_dir>`            | `<toml_file>`                | `<briefing_dir>` |
| --------- | ----------------------- | -------------------------- | ---------------------------- | ---------------- |
| `user`    | `~/.agents/skills/`     | `~/.codex/prompts/`        | `~/.codex/config.toml`       | `~/.codex/`      |
| `project` | `<repo>/.agents/skills/` | `<repo>/.codex/prompts/`  | `<repo>/.codex/config.toml`  | `<repo>/`        |
| `vault`   | `<vault>/.agents/skills/`| `<vault>/.codex/prompts/` | `<vault>/.codex/config.toml` | `<vault>/`       |

The MCP server is auto-skipped for project/vault scope (Codex's
config.toml is conventionally user-scoped). Pass `--with-mcp` to
override and write into the scoped `.codex/config.toml`.

Uninstall reads the manifest's `with_mcp` and `toml_file` fields, so
a project/vault uninstall never touches `~/.codex/config.toml`.

## Why this differs from the Claude Code install

Codex CLI's surface is leaner. The mapping is:

| Claude Code surface        | Codex equivalent          | Reason / status                                  |
| -------------------------- | ------------------------- | ------------------------------------------------ |
| `~/.claude/commands/`       | `~/.codex/prompts/`       | works; **deprecated upstream** — skills preferred |
| `~/.claude/agents/` (subagents) | folded into skills       | Codex doesn't have an Agent tool with names      |
| `~/.claude/skills/`         | `.agents/skills/`         | direct mirror; same `SKILL.md` format             |
| `~/.claude/hooks/` (lifecycle) | _no equivalent_         | Codex has no PreToolUse/PostToolUse/SessionStart |
| `~/.claude/.mcp.json` (JSON) | `~/.codex/config.toml` (TOML) | same MCP server; protocol layer is identical   |
| `CLAUDE.md` (auto-loaded)   | `AGENTS.md` (auto-loaded) | walks up from cwd                                 |

The **MCP server is shared** — `prompts/ralph-meta-chain/mcp-server/`
is a generic stdio server; both Claude Code and Codex talk to it
unchanged.

## Verify the install

```bash
# 1. Skills directory populated:
ls ~/.agents/skills/ | head    # ~16 entries (8 axis + 8 specialists)

# 2. The ralph-<axis>/SKILL.md wrapper directories exist:
cat ~/.agents/skills/ralph-memory/SKILL.md | head -3

# 3. Custom prompts (if you didn't pass --without-prompts):
ls ~/.codex/prompts/ | head    # ~11 entries

# 4. config.toml has the ralph block:
grep -A2 'mcp_servers.ralph' ~/.codex/config.toml

# 5. Manifest written:
cat ~/.codex/.ralph-installed.json | python3 -m json.tool | head

# 6. From inside Codex:
#    Type:  /ralph-cron
#    Or just describe a task — Codex will match a skill description.
```

## Surface map

After install, you have **three layers** of Ralph access from inside
Codex:

### 1. Skills (implicit + explicit)

Codex auto-discovers skills under `.agents/skills/`. Two ways to
trigger:

- **Implicit**: just describe what you want. Codex matches your
  prompt against each skill's `description:` and routes.
  > "Promote the inbox notes from yesterday into atomic notes."
  > → matches `ralph-memory` description triggers, routes there.
- **Explicit**: type `/skills` or `$<skill-name>` to invoke directly.
  > `$ralph-memory promote yesterday's inbox`

### 2. Custom prompts (deprecated but works)

`~/.codex/prompts/ralph-*.md` files become `/ralph-<name>` slash
commands in Codex CLI. Pass `--without-prompts` to skip if you don't
want them — the skills are sufficient for the same workflows.

### 3. MCP tools (programmatic, from inside Codex's reasoning)

Four tools. Codex will call them when the user's question matches the
tool's `description`:

```
ralph_query                 semantic search of the vault                  (read-only)
ralph_axis_status           last log line for one or all axes              (read-only)
ralph_self_test             run the local CI mirror                         (read-only)
ralph_migration_dry_run     generate migration proposal Markdown           (writes proposals; never moves files)
```

The first three are strictly read-only. `ralph_migration_dry_run`
writes proposal Markdown to `migration/`; revert with
`git restore prompts/ralph-meta-chain/migration/`. Implementation in
`mcp-server/README.md`.

## Uninstall

```bash
prompts/ralph-meta-chain/install/uninstall_codex.sh --scope user
```

Cleanly removes:
- Every tracked symlink (only if it still points inside the repo).
- Wrapper skill directories that become empty.
- The `[mcp_servers.ralph]` block from `~/.codex/config.toml` (and
  any sub-tables tagged with the `# RALPH-managed` marker).
- The AGENTS.md briefing **only** if it still has the
  `<!-- RALPH-managed AGENTS.md briefing -->` marker (i.e. you
  haven't edited it).
- The manifest itself, then any now-empty subdirs (`prompts/`,
  `.codex/`, `.agents/skills/`, `.agents/`).

## Coexistence with the Claude Code install

You can run both installers safely. They write to disjoint paths:

| Install              | Writes to                                                  |
| -------------------- | ---------------------------------------------------------- |
| `install_claude_code.sh` | `~/.claude/commands/`, `~/.claude/agents/`, `~/.claude/skills/`, `~/.claude/hooks/`, `~/.claude/settings.json`, `~/.claude/.mcp.json` |
| `install_codex.sh`   | `~/.agents/skills/`, `~/.codex/prompts/`, `~/.codex/config.toml`, `~/.codex/AGENTS.md` |

The shared MCP server (`prompts/ralph-meta-chain/mcp-server/`) is
referenced by both — registered in JSON for Claude Code, in TOML for
Codex. Both installers can be re-run independently and idempotently.

## Troubleshooting

**`config.toml` already has stuff in it — what gets touched?**
The installer only adds the block prefixed with
`# RALPH-managed: ralph MCP server`. Everything outside that block
is preserved byte-for-byte. The uninstaller strips only that block.

**Skills not picked up by Codex**
Codex needs `.agents/skills/<slug>/SKILL.md`. Run
`ls ~/.agents/skills/ralph-memory/` — you should see `SKILL.md` (a
symlink to `repo/agents/ralph-memory.md`).

**`/ralph-cron` not visible in Codex CLI**
Either (a) you passed `--without-prompts`, or (b) the file is at
`$CODEX_HOME/prompts/`, but you set a non-default `$CODEX_HOME`.
Check `echo $CODEX_HOME` and re-run with `CODEX_HOME=...
install_codex.sh`.

**MCP server registration in TOML didn't work**
Check syntax: `python3 -c "import tomllib;
tomllib.load(open('$HOME/.codex/config.toml','rb'))"`. If that
errors, the file had pre-existing invalid TOML; the installer only
appends. Fix the prior content and re-run.

**Want skills only (no MCP, no prompts)?**
`install_codex.sh --without-mcp --without-prompts`. Writes only the
16 skill directories. Cleanest install for environments where
config.toml is managed elsewhere.

## Cross-references

- `install/AGENTS.template.md` — the briefing that gets `cp`'d to
  `<briefing_dir>/AGENTS.md`.
- `mcp-server/README.md` — MCP protocol details (works with both
  Claude Code and Codex).
- `agents/README.md` — the 8 axis subagents (wrapped as skills here).
- `skills/` — the 8 specialist skills (mirrored unchanged here).
- `commands/README.md` — slash command catalog (used as Codex prompts).
- `install/CLAUDE_CODE_INSTALL.md` — sister install for Claude Code.
