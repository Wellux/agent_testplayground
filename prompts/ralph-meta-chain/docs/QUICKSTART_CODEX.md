# Quick start — OpenAI Codex CLI

Get the Ralph meta-chain running interactively inside the Codex CLI in
**under 10 minutes** from a fresh `git clone`. The Codex install is the
sister of the Claude Code one ([`QUICKSTART_CLAUDE_CODE.md`](QUICKSTART_CLAUDE_CODE.md))
— same chain, same MCP server, mapped to Codex's conventions
(skills + TOML config + AGENTS.md).

---

## Prerequisites (~3 min)

| Required | Version | Install |
| --- | --- | --- |
| `codex` (OpenAI Codex CLI) | latest | https://developers.openai.com/codex/cli |
| `python3` | ≥ 3.11 | system / `brew install python@3.11` / `apt install python3.11` |
| `git` | any modern | system / `brew install git` |
| `bats` (optional, for tests) | ≥ 1.5 | `brew install bats-core` / `apt install bats` |

Optional but recommended:

| Optional | Why |
| --- | --- |
| `ollama` running locally | semantic search via `nomic-embed-text` |
| an Obsidian vault | the chain's substrate |

Verify:

```bash
codex --version          # Codex CLI installed
python3 --version         # 3.11 or higher
echo "$CODEX_HOME"        # default: ~/.codex (configurable)
```

---

## 1. Clone + position (1 min)

```bash
git clone https://github.com/Wellux/agent_testplayground.git
cd agent_testplayground
```

---

## 2. Install — 1 line (1 min)

The unified dispatcher wires Codex in one shot.

```bash
# Preview first:
prompts/ralph-meta-chain/install/install.sh --target codex --dry-run

# Then install (default scope: user):
prompts/ralph-meta-chain/install/install.sh --target codex
```

What landed (28 artefacts, all tracked in
`~/.codex/.ralph-installed.json`):

| Surface | Path | Count |
| --- | --- | --- |
| Specialist skills | `~/.agents/skills/<slug>/` | 8 |
| Axis subagents (as skills) | `~/.agents/skills/ralph-<axis>/SKILL.md` | 8 |
| Slash-command prompts | `~/.codex/prompts/ralph-*.md` | 11 |
| MCP server `ralph` | `[mcp_servers.ralph]` in `~/.codex/config.toml` | 4 tools |
| Briefing | `~/.codex/AGENTS.md` | 1 |

### Scope choice

| Scope | When to use | Writes to |
| --- | --- | --- |
| `user` (default) | Codex available globally regardless of cwd | `~/.codex/` + `~/.agents/skills/` |
| `--scope project` | Surface only when running Codex inside this repo (collaborators inherit via git) | `<repo>/.codex/` + `<repo>/.agents/skills/` |
| `--scope vault` | Codex run from inside your vault discovers it by walking up | `<vault>/.codex/` + `<vault>/.agents/skills/` |

> Project/vault scopes are **strictly isolated** — they never write to
> `~/.codex/` or `~/.agents/`. Verified by the test suite (Codex P2-3
> regression).

---

## 3. Verify (1 min)

```bash
# Skills present
ls ~/.agents/skills/ | head     # 16 entries

# Wrapper dirs for axis subagents
cat ~/.agents/skills/ralph-memory/SKILL.md | head -3

# Prompts present
ls ~/.codex/prompts/ | head     # 11 entries

# config.toml has the ralph block
grep -A 8 'mcp_servers.ralph' ~/.codex/config.toml

# Briefing present
head -5 ~/.codex/AGENTS.md

# config.toml parses as valid TOML
python3 -c "
import tomllib
d = tomllib.load(open('$HOME/.codex/config.toml','rb'))
print('top-level keys:', sorted(d))
print('mcp servers:', sorted(d.get('mcp_servers', {})))
"
```

Expected:
- 16 skill entries (8 specialists + 8 axis subagents)
- 11 prompt files
- valid TOML with `mcp_servers.ralph` registered
- `AGENTS.md` starts with `<!-- RALPH-managed AGENTS.md briefing -->`

---

## 4. First commands (2 min)

Open a new Codex session in any directory:

```bash
codex
```

Try a slash-command prompt:

```
/ralph-cron
```

Or describe a task in natural language — Codex routes via skill
description matching:

> "Promote the inbox notes from yesterday."
>
> Codex matches → `ralph-memory` skill (description triggers
> include "promote inbox", "memory pass")

Or invoke a skill explicitly:

```
$ralph-research
```

The MCP server is registered in `~/.codex/config.toml`; Codex will
call its tools when your prompt matches the tool descriptions:

> "What's the last research-ingest pass say?"
>
> Codex calls → `ralph_axis_status(axis='research')` MCP tool

---

## 5. Connect to a vault (1 min)

Same as Claude Code:

```bash
# Option A — from the bundled template
cp -rn prompts/ralph-meta-chain/vault-template ~/Obsidian/SecondBrain
export VAULT="$HOME/Obsidian/SecondBrain"

# Option B — existing vault
export VAULT="$HOME/Documents/MyExistingVault"
mkdir -p "$VAULT/90-Meta"

# Persist:
echo 'export VAULT="$HOME/Obsidian/SecondBrain"' >> ~/.zshrc
```

---

## 6. (Optional) Schedule the cron + co-install Claude Code

The `cron` and `claude-code` targets are independent of the `codex`
target. To run all three at once:

```bash
prompts/ralph-meta-chain/install/install.sh --target all
```

Both Claude Code and Codex can share the chain — they write to disjoint
paths and the same MCP server serves both.

---

## Notes on Codex specifics

- **Custom prompts are deprecated upstream.** They still work today
  (the slash commands resolve), but the future-proof path is skills.
  Pass `--without-prompts` if you want skills-only:

  ```bash
  prompts/ralph-meta-chain/install/install.sh --target codex -- --without-prompts
  ```

- **No lifecycle hooks.** Codex doesn't have Claude Code's
  PreToolUse/PostToolUse/SessionStart hook surface — the SessionStart
  briefing is replaced by `AGENTS.md` (auto-loaded from cwd-up).

- **No Agent-tool subagents.** The 8 axis subagents are folded into
  skills (one `ralph-<axis>/SKILL.md` per axis). Codex routes by
  matching the user prompt against each skill's `description:`.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `/ralph-cron` not visible in Codex | wrong scope | If you used `--scope project`, `cd` into the repo. If `--scope user`, any cwd should work. |
| `config.toml` rejects with parse error | pre-existing invalid TOML | The installer only appends; it doesn't repair earlier syntax errors. Fix the prior content and re-run. |
| Skills not picked up | `.agents/skills/` not in cwd-up walk | Codex walks from cwd up. If you used `--scope project`, `cd` into the repo. |
| `MCP server not loading` | absolute path issue | `cat ~/.codex/config.toml` and verify `cwd` + `env.PYTHONPATH` are absolute |
| Codex not routing to a skill | description triggers don't match | Each skill's `description:` is the routing key. Edit the skill if your phrasings differ. |
| `installer refuses: ~/.agents/skills/<slug> exists and is not a symlink` | pre-existing user file | Move it aside, re-run installer |

---

## Uninstall

```bash
prompts/ralph-meta-chain/install/install.sh --target codex --uninstall
```

The Codex uninstaller is **scope-aware**. A project/vault uninstall
will NOT touch `~/.codex/config.toml` even if you've separately
installed the chain at user scope (verified by Codex P2-4 regression
test).

---

## What you've installed (deeper read)

- [`install/CODEX_INSTALL.md`](../install/CODEX_INSTALL.md) — full surface map
- [`install/AGENTS.template.md`](../install/AGENTS.template.md) — the briefing that lands at `~/.codex/AGENTS.md`
- [`mcp-server/README.md`](../mcp-server/README.md) — MCP protocol (same server as Claude Code)
- [`docs/PRD.md`](PRD.md) — product requirements
- [`docs/HANDOFF.md`](HANDOFF.md) — for the next maintainer
- [`QUICKSTART_CLAUDE_CODE.md`](QUICKSTART_CLAUDE_CODE.md) — sister guide
